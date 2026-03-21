"""
フォーム準拠 CSV 正規化モジュール（07_フォーム準拠_CSV取り込み仕様）

Google フォーム等からエクスポートされた CSV の列名・値を、
既存の analyzer / report_generator が期待する短いカラム名・数値に変換する。
読み込み直後にのみ適用し、既存の短い列名・数値の CSV は変化させない。
"""
from typing import Dict, List, Optional, Tuple, Any

# ---- 列名マッピング: (内部名, 候補リスト)。候補は完全一致または「列名が候補で始まる」でマッチ。
# 参加者用（実施前・直後・1ヶ月後）。Q15〜Q1 の順で登録し、Q1 が Q10 より先にマッチしないようにする。
COLUMN_MAP_PARTICIPANT: List[Tuple[str, List[str]]] = [
    ('メールアドレス', ['メールアドレス', 'あなたのメールアドレスを入力してください。', 'メール']),
    ('氏名', ['氏名', 'お名前', '名前', 'あなたの名前を入力してください。', 'あなたの氏名を入力してください。']),
    ('所属部署', ['所属部署', 'あなたの所属部署を選択してください。', '所属']),
    # Q15〜Q1 の順（Q10 等が Q1 にマッチしないように）
    ('Q15', ['Q15', 'Q15:', 'Q15：']),
    ('Q14', ['Q14', 'Q14:', 'Q14：']),
    ('Q13', ['Q13', 'Q13:', 'Q13：']),
    ('Q12', ['Q12', 'Q12:', 'Q12：']),
    ('Q11', ['Q11', 'Q11:', 'Q11：']),
    ('Q10', ['Q10', 'Q10:', 'Q10：']),
    ('Q9', ['Q9', 'Q9:', 'Q9：']),
    ('Q8', ['Q8', 'Q8:', 'Q8：']),
    ('Q7', ['Q7', 'Q7:', 'Q7：']),
    ('Q6', ['Q6', 'Q6:', 'Q6：']),
    ('Q5', ['Q5', 'Q5:', 'Q5：']),
    ('Q4', ['Q4', 'Q4:', 'Q4：']),
    ('Q3', ['Q3', 'Q3:', 'Q3：']),
    ('Q2', ['Q2', 'Q2:', 'Q2：']),
    # Q16A/Q17A/Q16B/Q17B を Q1 より前に配置（「Q16A：...」等が Q1 に startswith で誤マッチしないようにする）
    ('Q16A', ['Q16A', 'Q16A:', 'Q16A：', '活用意欲', 'Q16A：今回学んだ内容を、明日からの業務で活用できるイメージが湧いていますか？']),
    ('Q17A', ['Q17A', 'Q17A:', 'Q17A：', 'アクション宣言', 'Q17A：学んだ内容を踏まえ、直近で「変えてみよう」「やってみよう」と思う具体的な行動を1つ宣言してください。']),
    ('Q16B', ['Q16B', 'Q16B:', 'Q16B：', '実践頻度',
              'Q16B：研修受講後から現在までの間に、学んだスキルや考え方を業務で意識・実践する機会はありましたか？']),
    ('Q17B', ['Q17B', 'Q17B:', 'Q17B：', '実践エビデンス', '実践エピソード',
              'Q17B：（Q16Bで「あった」の方）具体的にどのような場面・業務で活用しましたか？']),
    ('Q1', ['Q1', 'Q1:', 'Q1：']),
    ('WS満足度', ['WS満足度', '満足度', '本ワークショップの満足度', '今回のワークショップの内容に対する満足度はどの程度ですか？']),
    ('WS理解度', ['WS理解度', '理解度', '本ワークショップの内容の理解度', '今回のワークショップの内容をどの程度理解できましたか？']),
    ('NPS', ['NPS(推奨度)', 'NPS', '推奨度', '知人に勧めたい度', 'このワークショップを、同僚や知人にどの程度おすすめしたいですか？']),
]

# 上長1ヶ月後用
COLUMN_MAP_MANAGER: List[Tuple[str, List[str]]] = [
    ('対象者メールアドレス', ['対象者メールアドレス', '評価対象者のメールアドレス', '本人のメールアドレス',
                             '評価対象となる方のメールアドレスを入力してください。']),
    ('上長メールアドレス', ['上長メールアドレス', 'メールアドレス', '回答者メールアドレス',
                           'あなた（評価者）のメールアドレスを入力してください。']),
    ('上長氏名', ['上長氏名', '氏名', 'お名前', 'あなた（評価者）の氏名を入力してください。']),
    ('上長部署', ['上長部署', '所属部署', 'あなた（評価者）の所属部署を入力してください。']),
    ('M6', ['M6', 'M6:', 'M6：']),
    ('M5', ['M5', 'M5:', 'M5：']),
    ('M4', ['M4', 'M4:', 'M4：']),
    ('M3', ['M3', 'M3:', 'M3：']),
    ('M2', ['M2', 'M2:', 'M2：']),
    ('M1', ['M1', 'M1:', 'M1：']),
    ('M7', ['M7', 'M7:', 'M7：', '上長コメント', 'コメント', '自由記述']),
]

# ---- 値マッピング: 日本語ラベル → 数値（5段階 1-5）
# Q1〜Q15・M1〜M5 は 02_評価フレームワーク に合わせる（1=できない、2=助けがあればできる、3=一人でできる、4=工夫・応用、5=人に教えられる）。
# キーは strip してからマッチ。複数候補は「含む」でマッチ（部分一致）する。
LABEL_TO_5_LOW_IS_BAD: List[Tuple[List[str], int]] = [
    (['全くできない', 'できない', 'そう思わない', '当てはまらない', '全く湧いていない', '湧いていない',
      '理解できなかった', '全く理解できなかった', '大変不満', 'とても不満'], 1),
    (['あまりできない', 'あまりそう思わない', '助けがあればできる', 'あまり湧いていない', 'あまり理解できなかった', '不満'], 2),
    (['どちらともいえない', '一人でできる', 'ある程度できる', 'そう思う'], 3),
    (['工夫・応用してできる'], 4),
    (['できる', 'とてもそう思う', '当てはまる', '人に教えられる', '湧いている', 'とても湧いている',
      '理解できた', 'よく理解できた', '大変満足', 'とても満足'], 5),
]

# 満足度専用（5=大変満足 → 1=大変不満）
LABEL_SATISFACTION: List[Tuple[List[str], int]] = [
    (['大変不満', 'とても不満'], 1),
    (['不満', 'やや不満'], 2),
    (['どちらともいえない'], 3),
    (['満足'], 4),
    (['大変満足', 'とても満足'], 5),
]

# 理解度専用
LABEL_UNDERSTANDING: List[Tuple[List[str], int]] = [
    (['理解できなかった', '全く理解できなかった'], 1),
    (['あまり理解できなかった'], 2),
    (['どちらともいえない', 'どちらでもない'], 3),
    (['ある程度理解できた'], 4),
    (['理解できた', 'よく理解できた', '深く理解できた'], 5),
]

# Q16A 活用意欲
LABEL_Q16A: List[Tuple[List[str], int]] = [
    (['湧いていない', '全く湧いていない'], 1),
    (['あまり湧いていない'], 2),
    (['どちらともいえない'], 3),
    (['やや湧いている'], 4),
    (['湧いている', 'とても湧いている'], 5),
]

# 上長評価専用ラベル（M1〜M6）: 参加者用と異なる表現を優先マッチするために独立定義
LABEL_TO_5_MANAGER: List[Tuple[List[str], int]] = [
    (['全くできない', 'まったくできない', 'できない', 'できていない', '任せられない'], 1),
    (['サポートがあればできる', '指示があればできる', '助けがあればできる'], 2),
    (['一人で任せられる', '自立してできる'], 3),
    (['工夫・応用してできる', '積極的に取り組める', '応用してできる'], 4),
    (['期待以上にできている', '卓越している', '人に教えられる', '非常にできる', '周囲の手本・指導レベル'], 5),
]

# Q16B 実践頻度（1〜4）
LABEL_Q16B: List[Tuple[List[str], int]] = [
    (['よくあった', '週1回以上'], 1),
    (['たまにあった', '月数回程度'], 2),
    (['ほとんどなかった', '1回程度'], 3),
    (['全くなかった'], 4),
]

# NPS は数値または "0"〜"10" の文字列のまま。日本語ラベルは想定しない（必要なら追加可）

# 参加者用スコア列（1-5）
SCORE_COLUMNS_5: List[str] = [
    'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10',
    'Q11', 'Q12', 'Q13', 'Q14', 'Q15',
    'WS満足度', 'WS理解度', 'Q16A'
]
# 参加者用 Q16B（1-4）
SCORE_COLUMNS_4: List[str] = ['Q16B']
# 上長用 M1-M5（1-5）、M6（変化感知・1-5）
SCORE_COLUMNS_M: List[str] = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']

# 自由記述欄：回答者入力の改行を除去して表・プレースホルダー等で1行に収める（再発防止）
FREE_TEXT_COLUMNS_PARTICIPANT: List[str] = ['Q17A', 'Q17B']
FREE_TEXT_COLUMNS_MANAGER: List[str] = ['M7']


def _strip_bom(s: str) -> str:
    """先頭の BOM を除去"""
    if s and s.startswith('\ufeff'):
        return s[1:]
    return s


def _normalize_newlines_in_text(s: Optional[Any]) -> str:
    """自由記述欄の改行をスペースに置換し、表・プレースホルダーで1行に収める。None/空はそのまま返す。"""
    if s is None or s == '':
        return '' if s is None else str(s)
    t = str(s).replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return t.strip()


def _normalize_header(header: str) -> str:
    """ヘッダー文字列の前後空白と BOM を除去"""
    return _strip_bom(header.strip())


def _match_column(header: str, mapping: List[Tuple[str, List[str]]]) -> Optional[str]:
    """
    列名を内部カラム名にマッピングする。
    完全一致または「列名が候補で始まる」で最初にマッチした内部名を返す。
    """
    h = _normalize_header(header)
    for internal_name, candidates in mapping:
        for c in candidates:
            c = c.strip()
            if h == c or h.startswith(c):
                return internal_name
    return None


def normalize_headers_participant(headers: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """
    参加者用 CSV の列名を正規化する。
    戻り値: (元の列名 → 内部名 の辞書, 内部名の順序リスト)。
    マッチしなかった列はそのまま内部名として使う（既存の短い列名の互換のため）。
    """
    result_order: List[str] = []
    seen_internal: set = set()
    col_map: Dict[str, str] = {}

    for raw in headers:
        h = _normalize_header(raw)
        internal = _match_column(raw, COLUMN_MAP_PARTICIPANT)
        if internal:
            col_map[raw] = internal
            if internal not in seen_internal:
                result_order.append(internal)
                seen_internal.add(internal)
        else:
            col_map[raw] = h
            if h not in seen_internal:
                result_order.append(h)
                seen_internal.add(h)

    return col_map, result_order


def normalize_headers_manager(headers: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """上長用 CSV の列名を正規化する。戻り値は参加者用と同様。"""
    result_order = []
    seen_internal = set()
    col_map = {}

    for raw in headers:
        h = _normalize_header(raw)
        internal = _match_column(raw, COLUMN_MAP_MANAGER)
        if internal:
            col_map[raw] = internal
            if internal not in seen_internal:
                result_order.append(internal)
                seen_internal.add(internal)
        else:
            col_map[raw] = h
            if h not in seen_internal:
                result_order.append(h)
                seen_internal.add(h)

    return col_map, result_order


def _label_to_5(value: Any, label_map: List[Tuple[List[str], int]]) -> Optional[int]:
    """文字列を 5 段階数値に変換。既に 1〜5 の数値ならそのまま。"""
    if value is None or value == '':
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        n = float(s)
        if 1 <= n <= 5 and n == int(n):
            return int(n)
    except (ValueError, TypeError):
        pass
    for labels, num in label_map:
        for label in labels:
            if label in s or s in label:
                return num
    return None


def label_to_satisfaction_value(value: Any) -> Optional[int]:
    """満足度の日本語ラベルを 1〜5 の数値に変換。他モジュールから利用するための公開関数。"""
    return _label_to_5(value, LABEL_SATISFACTION)


def label_to_understanding_value(value: Any) -> Optional[int]:
    """理解度の日本語ラベルを 1〜5 の数値に変換。他モジュールから利用するための公開関数。"""
    return _label_to_5(value, LABEL_UNDERSTANDING)


def _label_to_4(value: Any) -> Optional[int]:
    """Q16B 用: 1〜4"""
    if value is None or value == '':
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        n = float(s)
        if 1 <= n <= 4 and n == int(n):
            return int(n)
    except (ValueError, TypeError):
        pass
    for labels, num in LABEL_Q16B:
        for label in labels:
            if label in s or s in label:
                return num
    return None


def _nps_value(value: Any) -> Optional[float]:
    """NPS は 0〜10。数値または "0"〜"10" のまま。"""
    if value is None or value == '':
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        n = float(s)
        if 0 <= n <= 10:
            return n
    except (ValueError, TypeError):
        pass
    return None


def _normalize_value_5(key: str, value: Any) -> Any:
    """5 段階スコア列の値を数値に正規化。"""
    if value is None or value == '':
        return value
    if key == 'WS満足度':
        n = _label_to_5(value, LABEL_SATISFACTION)
    elif key == 'WS理解度':
        n = _label_to_5(value, LABEL_UNDERSTANDING)
    elif key == 'Q16A':
        n = _label_to_5(value, LABEL_Q16A)
    else:
        n = _label_to_5(value, LABEL_TO_5_LOW_IS_BAD)
    if n is not None:
        return str(n)
    return value


def normalize_row_values_participant(row: Dict[str, Any], normalized_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    参加者用の 1 行について、スコア列の値を数値に正規化する。
    row は「正規化後の列名」をキーにした辞書（列名正規化済み）を想定。
    """
    out = dict(row)
    for col in SCORE_COLUMNS_5:
        if col in out and out[col] not in (None, ''):
            v = _normalize_value_5(col, out[col])
            if v is not None:
                out[col] = v
    for col in SCORE_COLUMNS_4:
        if col in out and out[col] not in (None, ''):
            n = _label_to_4(out[col])
            if n is not None:
                out[col] = str(n)
    if 'NPS' in out and out['NPS'] not in (None, ''):
        n = _nps_value(out['NPS'])
        if n is not None:
            out['NPS'] = str(int(n)) if n == int(n) else str(n)
    # 自由記述欄（Q17A, Q17B）の改行を除去（直後.csv等のセル内改行でC_block_3_2_body_P等が崩れないようにする）
    for col in FREE_TEXT_COLUMNS_PARTICIPANT:
        if col in out and out[col] not in (None, ''):
            out[col] = _normalize_newlines_in_text(out[col])
    return out


def normalize_row_values_manager(row: Dict[str, Any]) -> Dict[str, Any]:
    """上長用の 1 行について、M1〜M6 の値を 1〜5 に正規化する。自由記述 M7 の改行も除去。"""
    out = dict(row)
    for col in SCORE_COLUMNS_M:
        if col in out and out[col] not in (None, ''):
            # 上長専用ラベルを優先し、マッチしない場合は汎用ラベルにフォールバック
            n = _label_to_5(out[col], LABEL_TO_5_MANAGER)
            if n is None:
                n = _label_to_5(out[col], LABEL_TO_5_LOW_IS_BAD)
            if n is not None:
                out[col] = str(n)
    for col in FREE_TEXT_COLUMNS_MANAGER:
        if col in out and out[col] not in (None, ''):
            out[col] = _normalize_newlines_in_text(out[col])
    return out


def normalize_participant_csv(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    参加者用 CSV（実施前・直後・1ヶ月後）の列名と値を正規化する。
    rows は csv.DictReader の結果（元の列名がキー）。
    """
    if not rows:
        return []
    headers = list(rows[0].keys())
    col_map, order = normalize_headers_participant(headers)
    # 列名を内部名に変換した行のリストを作成
    normalized_rows = []
    for row in rows:
        new_row = {}
        for raw_key, val in row.items():
            internal = col_map.get(raw_key, _normalize_header(raw_key))
            # 同一内部名が複数ある場合は最初の列のみ使う（仕様どおり）
            if internal not in new_row or new_row[internal] in (None, ''):
                new_row[internal] = val
        normalized_rows.append(new_row)
    # 値の正規化
    return [normalize_row_values_participant(r, {}) for r in normalized_rows]


def normalize_manager_csv(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """上長1ヶ月後 CSV の列名と値を正規化する。"""
    if not rows:
        return []
    headers = list(rows[0].keys())
    col_map, order = normalize_headers_manager(headers)
    normalized_rows = []
    for row in rows:
        new_row = {}
        for raw_key, val in row.items():
            internal = col_map.get(raw_key, _normalize_header(raw_key))
            if internal not in new_row or new_row[internal] in (None, ''):
                new_row[internal] = val
        normalized_rows.append(normalize_row_values_manager(new_row))
    return normalized_rows
