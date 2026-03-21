"""
report_generator.pyの実装用ヘルパー関数
スタブ関数を段階的に実装するための補助モジュール
10_分析コメント品質要件: 活用意欲・アクション宣言・満足度・理解度の活用対応
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .analyzer import (
    SKILL_AXES, get_highest_skill, get_lowest_skill,
    calculate_question_average, identify_strengths, identify_weaknesses
)

# スキル軸とQ17A検索キーワードのマッピング（10_分析コメント品質要件 6.5）
SKILL_TO_Q17A_KEYWORDS: Dict[str, List[str]] = {
    'research': ['インタビュー', 'ヒアリング', '深掘り', '分析', 'ペルソナ', 'リサーチ', 'インサイト', 'ファクト'],
    'concept': ['コンセプト', 'アイデア', '仮説', '価値観', '定義'],
    'delivery': ['プロトタイプ', '検証', '具体化', '形にする'],
    'communication': ['伝達', '構造化', '言語化', 'グループ分け', '整理', '可視化', '共有'],
    'implementation': ['チーム', 'コミュニケーション', '目線', 'プロジェクト', 'リーダーシップ'],
}

# 文字数制限ヘルパー（10/12/16: 目標文字数を超えないよう、文単位で末尾から削る）
def _cap_chars(text: str, max_chars: int) -> str:
    """max_charsを超える場合、句点・読点で区切った末尾から文単位で削り、max_chars以内に収める。"""
    if not text or len(text) <= max_chars:
        return text
    # 文境界（。.!?！？）で分割し、先頭から結合してmax_chars以内に収める
    parts = re.split(r'(?<=[。.!?！？])', text)
    result = ''
    for p in parts:
        p = p.strip()
        if not p:
            continue
        candidate = (result + p).strip() if result else p
        if len(candidate) <= max_chars:
            result = candidate
        else:
            break
    return result.strip() if result else text[:max_chars - 3] + '…'


# 16_O_block_2_3_言い回し多様化と可読性要件: 組織インデックスで選択する言い回し候補
def _select_variant(choices: List[str], org_index: int) -> str:
    """org_index に応じて候補から1つを選ぶ（再現可能）。"""
    if not choices:
        return ''
    return choices[org_index % len(choices)]

# 強みスキル説明のバリエーション（スキル名 -> 言い回しのリスト）
STRENGTH_DESCRIPTION_VARIANTS: Dict[str, List[str]] = {
    'リサーチ・分析力': [
        '顧客や関係者へのヒアリングで深い洞察を得る能力が高く、課題の本質を把握できている',
        'ヒアリングで深い洞察を得て、課題の本質を把握する力が高い',
        '関係者へのヒアリングと分析により、課題の本質を捉えている',
    ],
    '構想・コンセプト力': [
        '独自の視点から解決策を定義する能力が向上し、革新的なアイデア創出が可能になっている',
        '解決策の定義と革新的なアイデア創出が可能な水準にあり、独自の視点が活きている',
        '革新的なアイデア創出と、独自視点に基づく解決策の定義ができている',
    ],
    '具体化・検証力': [
        'プロトタイプを素早く作成し、検証サイクルを効果的に回す能力が高い',
        '素早いプロトタイプ作成と、効果的な検証サイクルを回す力が発揮されている',
        '検証サイクルを効果的に回し、プロトタイプを素早く形にする能力が高い',
    ],
    '伝達・構造化力': [
        '会議やプレゼンテーションでの合意形成がスムーズで、ファシリテーションスキルが確立されている',
        '合意形成がスムーズで、会議・プレゼンにおけるファシリテーション力が高い',
        'ファシリテーションスキルが確立され、会議やプレゼンでの合意形成が円滑である',
    ],
    '実現・ディレクション力': [
        'プロジェクト推進におけるリーダーシップが発揮され、他者を巻き込む能力が向上している',
        'リーダーシップと他者を巻き込む力が発揮され、プロジェクト推進ができている',
        '他者を巻き込み、プロジェクトを推進するディレクション力が高い',
    ],
}

# 伸びしろスキル説明のバリエーション
WEAKNESS_DESCRIPTION_VARIANTS: Dict[str, List[str]] = {
    'リサーチ・分析力': [
        '基礎スキルは向上しているが、深い分析とインサイト抽出に課題がある',
        '深い分析とインサイト抽出に課題があり、さらなる掘り下げが期待される',
        'インサイト抽出や深い分析の実践に、伸びしろがある',
    ],
    '構想・コンセプト力': [
        'アイデア発想はできているが、コンセプトを明確に定義し、関係者の合意形成に課題がある',
        'コンセプトの明確な定義や関係者との合意形成に課題があり、補強の余地がある',
        '関係者の合意形成やコンセプトの定義を、より明確にしていく余地がある',
    ],
    '具体化・検証力': [
        'プロトタイプ作成の実践機会が不足し、検証サイクルが効果的に回されていない',
        '検証サイクルを効果的に回す実践が不足しており、具体化・検証の強化が期待される',
        'プロトタイプ作成と検証サイクルの実践機会を増やすと、伸びしろが活きる',
    ],
    '伝達・構造化力': [
        '情報伝達はできているが、複雑な情報の構造化や可視化に課題がある',
        '複雑な情報の構造化や可視化に課題があり、伝達・構造化の補強が期待される',
        '情報の構造化や可視化を高めることで、伝達力の伸びしろが活きる',
    ],
    '実現・ディレクション力': [
        '計画立案はできているが、チームを巻き込んだ実行や品質管理に課題がある',
        'チームを巻き込んだ実行や品質管理に課題があり、ディレクション力の補強が期待される',
        '実行や品質管理をチームとともに進める面に、伸びしろがある',
    ],
}

# 活用意欲の言い回しバリエーション（{total}・{high} は後で format）
WILLINGNESS_PHRASE_TEMPLATES: List[str] = [
    '参加者{total}名中{high}名が活用意欲「湧いている」以上と回答し、現場での実践意欲が高い。',
    '活用意欲は{total}名中{high}名が「湧いている」以上であり、学びを現場で活かす意欲がうかがえる。',
    '{total}名中{high}名が「湧いている」以上と回答しており、実践への意欲が高い。',
]

# 活用意欲の言い回し：1名の場合（N名中N名は冗長なため個人向け表現に）
WILLINGNESS_PHRASE_SINGLE_TEMPLATES: List[str] = [
    '活用意欲「湧いている」以上と回答しており、現場での実践意欲が高い。',
    '学んだことを現場で活かしたいという意欲が確認されています。',
    '活用意欲が高く、実践への強いモチベーションが見られます。',
]

# 強みブロック：アクション宣言導入の言い回し（{action} は後で埋める）16要件: 3つ以上
ACTION_INTRO_STRENGTH_TEMPLATES: List[str] = [
    '参加者からは「{action}」といったアクション宣言も見られ、強みの現場活用が期待される。',
    '「{action}」といった宣言もあり、強みを現場で活かす動きが期待される。',
    '「{action}」といった意欲もあり、強みを活かした実践が期待される。',
]

# 伸びしろブロック：アクション宣言導入の言い回し 16要件: 3つ以上
ACTION_INTRO_WEAKNESS_TEMPLATES: List[str] = [
    '参加者からは「{action}」といった改善を志向した宣言があり、補強の機運がうかがえる。',
    '「{action}」といった改善を志向した宣言があり、伸びしろの補強が期待される。',
    '「{action}」といった宣言もあり、補強に向けた動きが期待される。',
]

# 理解度締め（強み用・高め）：{u} は理解度の数値
UNDERSTANDING_PHRASE_STRENGTH_HIGH: List[str] = [
    '理解度は{u}点と高く、強みの定着が期待される。',
    '理解度が{u}点と高く、学びの定着が期待される。',
]
UNDERSTANDING_PHRASE_STRENGTH_MID: List[str] = [
    '理解度は{u}点。振り返りの機会があると、定着が期待される。',
    '理解度{u}点。振り返りを行うと、強みの定着につながる。',
]
UNDERSTANDING_PHRASE_STRENGTH_LOW: List[str] = [
    '理解度は{u}点。振り返りの機会があると、強みの定着が期待される。',
    '理解度{u}点。フォローがあると、定着が進む。',
]
UNDERSTANDING_PHRASE_WEAKNESS_HIGH: List[str] = [
    '理解度は{u}点と高く、改善意欲がうかがえる。',
    '理解度も{u}点と高く、伸びしろを補強する意欲がうかがえる。',
]
UNDERSTANDING_PHRASE_WEAKNESS_MID: List[str] = [
    '理解度は{u}点と高く、伸びしろの補強が期待される。',
    '理解度{u}点。フォローがあると、伸びしろの補強につながる。',
]
UNDERSTANDING_PHRASE_WEAKNESS_LOW: List[str] = [
    '理解度は{u}点。理解度を高めるフォローがあると、伸びしろの補強につながる。',
    '理解度{u}点。フォローで理解を深めると、補強につながる。',
]

# フォールバック締め（理解度なし・強み／伸びしろ）
FALLBACK_STRENGTH: List[str] = [
    '維持・強化には現場での継続的な実践機会の創出と、他軸スキルとの連携が有効。',
    '強みの定着には、現場での実践機会と他軸との連携が有効。',
]
FALLBACK_WEAKNESS: List[str] = [
    '小さなプロジェクトでのリーダー経験を積み重ねることで、組織全体の実行力向上に貢献できる。',
    'リーダー経験を積み重ねることで、伸びしろの補強につながる。',
]


def _get_q16a_numeric(row: Dict) -> Optional[int]:
    """Q16Aの数値を取得（文字列ラベルの場合は変換を試みる）"""
    val = row.get('Q16A', '') or row.get('Q16A: 活用意欲', '')
    if val is None or val == '':
        return None
    if isinstance(val, (int, float)):
        try:
            n = int(float(val))
            if 1 <= n <= 5:
                return n
        except (ValueError, TypeError):
            pass
        return None
    s = str(val).strip()
    # 日本語ラベルの簡易マッピング
    high_labels = ['非常に湧いている', 'とても湧いている', '湧いている', 'やや湧いている']
    mid_labels = ['どちらともいえない']
    low_labels = ['あまり湧いていない', '湧いていない', '全く湧いていない']
    for lbl in high_labels:
        if lbl in s or s in lbl:
            return 5 if '非常に' in s or 'とても' in s else 4
    for lbl in mid_labels:
        if lbl in s or s in lbl:
            return 3
    for lbl in low_labels:
        if lbl in s or s in lbl:
            return 2 if 'あまり' in s else 1
    try:
        n = int(float(s))
        if 1 <= n <= 5:
            return n
    except (ValueError, TypeError):
        pass
    return None


def _get_dept(row: Dict) -> str:
    """所属部署を取得（BOM対応）"""
    return (row.get('所属部署', '') or row.get('\ufeff所属部署', '') or row.get('所属', '') or '').strip()


def _aggregate_willingness(post_data: List[Dict], dept_filter: Optional[str] = None) -> Tuple[int, int]:
    """
    活用意欲（Q16A）を集計。湧いている以上=4以上的人数と総人数を返す。
    dept_filter: 指定時はその部署のみ集計
    """
    if not post_data:
        return 0, 0
    total = 0
    high = 0
    for row in post_data:
        if dept_filter and _get_dept(row) != dept_filter:
            continue
        n = _get_q16a_numeric(row)
        if n is not None:
            total += 1
            if n >= 4:
                high += 1
    return high, total


def _select_action_declarations(post_data: List[Dict], dept_filter: Optional[str] = None,
                                skill_key: Optional[str] = None, max_chars: int = 80,
                                exclude_action_texts: Optional[List[str]] = None) -> List[str]:
    """
    代表的なアクション宣言（Q17A）を1〜2件選び要約して返す。
    skill_key: 指定時はそのスキル軸に関連するQ17Aを優先
    exclude_action_texts: 強みで使用した宣言など、除外する文言のリスト（重複引用を避ける）
    """
    if not post_data:
        return []
    exclude = list(exclude_action_texts) if exclude_action_texts else []
    candidates = []
    for row in post_data:
        if dept_filter and _get_dept(row) != dept_filter:
            continue
        q17a = (row.get('Q17A', '') or row.get('Q17A: アクション宣言', '') or '').strip()
        # セル内改行をスペースに置換（Markdown表の行崩れ防止）
        q17a = q17a.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        if not q17a or len(q17a) < 5:
            continue
        # 除外リストに含まれる（強みで使用した宣言と同一・またはその引用部分）はスキップ
        if exclude:
            cand_truncated = (q17a[:max_chars - 3] + '...') if len(q17a) > max_chars else q17a
            if any((ex in q17a) or (cand_truncated == ex) or (ex.endswith('...') and q17a.startswith(ex[:-3])) for ex in exclude):
                continue
        keywords = SKILL_TO_Q17A_KEYWORDS.get(skill_key, []) if skill_key else []
        score = 0
        if keywords:
            for kw in keywords:
                if kw in q17a:
                    score += 1
                    break
        candidates.append((score, q17a))
    # スキル関連のものを優先し、長さでソート（短く具体的なものを優先）
    candidates.sort(key=lambda x: (-x[0], len(x[1])))
    result = []
    for _, text in candidates[:2]:
        if len(text) > max_chars:
            text = text[:max_chars - 3] + '...'
        result.append(text)
    return result


def _satisfaction_phrase(sat_avg: float, und_avg: float) -> str:
    """満足度・理解度の平均値に応じた言い回しを返す（連用形・接続形）"""
    avg_both = (sat_avg + und_avg) / 2 if (sat_avg or und_avg) else 0
    if avg_both >= 4.0:
        return '高く'
    if avg_both >= 3.5:
        return '高く'
    if avg_both >= 3.0:
        return 'おおむね良好で'
    return '一定の課題があり'


def _understanding_phrase(understanding_avg: Optional[float], for_strength: bool = True,
                          org_index: int = 0) -> str:
    """
    組織別理解度に応じた締め文の一句を返す（16: org_index で言い回しを選択）。
    for_strength: True=強みブロック用、False=伸びしろブロック用
    """
    if understanding_avg is None:
        return ''
    try:
        u = float(understanding_avg)
    except (TypeError, ValueError):
        return ''
    u_str = f"{u:.2f}"
    if u >= 4.0:
        if for_strength:
            return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_STRENGTH_HIGH], org_index)
        return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_WEAKNESS_HIGH], org_index)
    if u >= 3.5:
        if for_strength:
            return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_STRENGTH_HIGH], org_index)
        return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_WEAKNESS_MID], org_index)
    if u >= 3.0:
        if for_strength:
            return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_STRENGTH_MID], org_index)
        return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_WEAKNESS_MID], org_index)
    if for_strength:
        return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_STRENGTH_LOW], org_index)
    return _select_variant([t.replace('{u}', u_str) for t in UNDERSTANDING_PHRASE_WEAKNESS_LOW], org_index)


def generate_summary_comment_impl(phase: int, pre_scores: Dict[str, float],
                                  post_scores: Optional[Dict[str, float]] = None,
                                  follow_scores: Optional[Dict[str, float]] = None,
                                  project_name: str = "", num_participants: int = 0,
                                  post_data: Optional[List[Dict]] = None,
                                  satisfaction: Optional[Dict[str, float]] = None) -> str:
    """総評コメントを生成（実装版）。Phase2以上でpost_data・satisfactionを活用。"""
    comments = []
    
    if phase == 1:
        total_score = pre_scores.get('total', 0)
        comments.append(f"組織全体の現状スキルレベルは {total_score:.2f}点です。")
        try:
            highest = get_highest_skill(pre_scores)
            lowest = get_lowest_skill(pre_scores)
            comments.append(f"特に「{highest}」が高く、「{lowest}」に課題があります。")
        except Exception:
            pass
        
        # 総合スコアに基づく評価
        if total_score >= 3.5:
            comments.append("組織全体のスキルレベルは高く、バランスが取れています。")
        elif total_score >= 3.0:
            comments.append("組織全体のスキルレベルは標準的です。")
        else:
            comments.append("組織全体のスキルレベルは標準を下回っており、向上の余地があります。")
    
    elif phase == 2:
        if post_scores and pre_scores:
            pre_total = pre_scores.get('total', 0)
            post_total = post_scores.get('total', 0)
            diff = post_total - pre_total
            # 25_エグゼクティブサマリー_コメント最適化: 総合総評型（傾向・方向性を前面に、数値は補足）
            parts = []
            # 総合的にどうだったか（傾向）：数値羅列を避け、質的変化を一言で
            try:
                lowest_pre = get_lowest_skill(pre_scores)
                highest_post = get_highest_skill(post_scores)
            except Exception:
                lowest_pre = highest_post = None
            if diff > 0.2:
                tendency = "ワークショップを通じて、全体的にスキルがバランスよく伸びる兆しが見られた。"
                if lowest_pre and (lowest_pre == 'リサーチ・分析力' or lowest_pre == '構想・コンセプト力'):
                    tendency = "現場で形にすることは得意とする一方、課題の掘り下げや合意形成に課題があった傾向から、バランスの取れたスキル基盤へと変化する兆しが見られた。"
                parts.append(tendency)
                parts.append("スコアは全体的に向上しており、学習効果が表れていると解釈できる。")
            else:
                parts.append("ワークショップ後、スキル認識に一定の変化が見られた。")
                parts.append("今後の現場実践と振り返りにより、さらなる定着が期待される。")
            # 活用意欲・アクション宣言（根拠の補足）。数値は控えめに
            if post_data and len(post_data) > 0:
                high, total = _aggregate_willingness(post_data)
                if total > 0 and high > 0:
                    parts.append("参加者の多くが現場での実践意欲を「湧いている」以上と回答しており、意欲は高い。")
                    actions = _select_action_declarations(post_data, max_chars=50)
                    if actions:
                        acts_str = "」「".join(actions[:2])
                        parts.append(f"「{acts_str}」といったアクション宣言も見られ、定着が期待される。")
            # 今後どうあるとよいか（方向性）
            parts.append("今後は、宣言されたアクションの実行とチームでの振り返りを重ねることで、定着とさらなる成果につなげることが期待される。")
            if satisfaction and (satisfaction.get('satisfaction', 0) or 0) >= 3.5 and (satisfaction.get('understanding', 0) or 0) >= 3.5:
                parts.append("満足度・理解度も高く、スコア向上は学習効果によるものと解釈できる。")
            return _cap_chars(" ".join(parts), 450)
    
    elif phase == 3:
        if post_scores and follow_scores and pre_scores:
            pre_total = pre_scores.get('total', 0)
            post_total = post_scores.get('total', 0)
            follow_total = follow_scores.get('total', 0)
            diff1 = post_total - pre_total
            diff2 = follow_total - post_total
            total_diff = follow_total - pre_total

            skill_key_map = {
                'research': 'リサーチ・分析力',
                'concept': '構想・コンセプト力',
                'delivery': '具体化・検証力',
                'communication': '伝達・構造化力',
                'implementation': '実現・ディレクション力'
            }

            # Bullet 1: 3時点の変容サマリー（1ヶ月後視点）
            if diff2 >= 0:
                comments.append(
                    f"実施前から直後へ{diff1:+.2f}pt向上し、1ヶ月後も{follow_total:.2f}点（実施前比{total_diff:+.2f}pt）を維持・向上。"
                    f"研修効果が現場での実践に定着していることが確認できました。"
                )
            else:
                comments.append(
                    f"実施前から直後へ{diff1:+.2f}pt向上し、1ヶ月後は{follow_total:.2f}点（実施前比{total_diff:+.2f}pt）となりました。"
                    f"直後比では{diff2:.2f}ptの変動が見られ、継続的な実践機会の確保が今後の課題です。"
                )

            # Bullet 2: 1ヶ月後時点で最も定着したスキル軸（実施前→1ヶ月後の向上幅が大きい軸）
            skill_improvements = []
            for key, sname in skill_key_map.items():
                pre_val = pre_scores.get(key, 0)
                follow_val = follow_scores.get(key, 0)
                if pre_val > 0:
                    imp = follow_val - pre_val
                    if imp > 0.1:
                        skill_improvements.append((sname, imp, follow_val))
            skill_improvements.sort(key=lambda x: x[1], reverse=True)

            # Bullet 3: 1ヶ月後時点の弱み軸（スコアが平均以下かつ最も低い軸）
            skill_analysis = []
            for key, sname in skill_key_map.items():
                follow_val = follow_scores.get(key, 0)
                imp = follow_val - pre_scores.get(key, 0)
                skill_analysis.append({'name': sname, 'score': follow_val, 'improvement': imp})
            avg_score = sum(s['score'] for s in skill_analysis) / len(skill_analysis) if skill_analysis else 0
            weak_skills = sorted(
                [s for s in skill_analysis if s['score'] < avg_score and s['score'] < 3.6],
                key=lambda x: x['score']
            )
            weakness_name = weak_skills[0]['name'] if weak_skills else ''
            weakness_score = weak_skills[0]['score'] if weak_skills else 0.0

            if skill_improvements:
                top = skill_improvements[0]
                if len(skill_improvements) >= 2:
                    second = skill_improvements[1]
                    improvement_comment = (
                        f"1ヶ月後の時点で特に「{top[0]}」（{top[2]:.2f}点、実施前比{top[1]:+.2f}pt）と"
                        f"「{second[0]}」（{second[2]:.2f}点、実施前比{second[1]:+.2f}pt）の定着が顕著で、"
                        f"現場での実践が着実に積み上がっています。"
                    )
                else:
                    improvement_comment = (
                        f"1ヶ月後の時点で特に「{top[0]}」（{top[2]:.2f}点、実施前比{top[1]:+.2f}pt）の定着が顕著です。"
                    )
                if weakness_name:
                    comments.append(
                        f"{improvement_comment}"
                        f"一方、「{weakness_name}」は{weakness_score:.2f}点と伸びしろが残っており、実践の積み重ねが期待されます。"
                    )
                else:
                    comments.append(improvement_comment)
            elif weakness_name:
                comments.append(
                    f"一方、「{weakness_name}」は1ヶ月後も{weakness_score:.2f}点と伸びしろが残っており、"
                    f"意識的な実践機会を設けることが今後の重点課題です。"
                )
    
    # 最大3つの箇条書きに制限
    limited_comments = comments[:3] if len(comments) > 3 else comments
    return "\n".join([f"- {c}" for c in limited_comments]) if limited_comments else "- 分析データが不足しています。"


# 12_C_block_comment_requirements: スキル軸の表示名とキー
SKILL_NAMES = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
SKILL_KEYS = ['research', 'concept', 'delivery', 'communication', 'implementation']


def generate_radar_description_pre_extended_impl(pre_scores: Dict, skill_names: List[str], skill_keys: List[str]) -> str:
    """レーダーチャート実施前の説明を生成（拡張版・約300文字）"""
    if not pre_scores:
        return "実施前のデータが不足しています。"
    pre_total = pre_scores.get('total', 0)
    if pre_total <= 0:
        pre_total = sum(pre_scores.get(k, 0) for k in skill_keys) / len(skill_keys) if skill_keys else 0
    parts = []
    # 5軸スコアの概要
    scores_str = "、".join([f"{skill_names[i]}{pre_scores.get(skill_keys[i], 0):.2f}点" for i in range(len(skill_names))])
    parts.append(f"実施前の総合スコアは{pre_total:.2f}点。各軸は{scores_str}である。")
    # 最低・最高スキルの特定
    pre_lowest_skill = skill_names[0]
    pre_lowest_score = pre_scores.get(skill_keys[0], 0)
    pre_highest_skill = skill_names[0]
    pre_highest_score = pre_scores.get(skill_keys[0], 0)
    for i, key in enumerate(skill_keys):
        s = pre_scores.get(key, 0)
        if s < pre_lowest_score:
            pre_lowest_skill, pre_lowest_score = skill_names[i], s
        if s > pre_highest_score:
            pre_highest_skill, pre_highest_score = skill_names[i], s
    # 評価に応じた説明
    if pre_total < 2.5:
        parts.append(f"全体的に低めで、特に「{pre_lowest_skill}」が{pre_lowest_score:.2f}点と課題となっている。")
        parts.append("ワークショップによる学習効果の余地が大きい状態であった。")
    elif pre_total < 3.5:
        parts.append(f"全体的に標準的だが、「{pre_lowest_skill}」が{pre_lowest_score:.2f}点と相対的に課題がある。")
        if pre_highest_score > pre_lowest_score + 0.5:
            parts.append(f"一方「{pre_highest_skill}」は{pre_highest_score:.2f}点と強みとして位置づけられる。")
    else:
        parts.append(f"全体的に高めで、「{pre_highest_skill}」が{pre_highest_score:.2f}点と特に高い。")
    return _cap_chars("".join(parts), 350)


def generate_radar_description_post_extended_impl(pre_scores: Dict, post_scores: Dict,
                                                  skill_names: List[str], skill_keys: List[str]) -> str:
    """レーダーチャート直後の説明を生成（拡張版・約300文字）"""
    if not post_scores:
        return ""
    post_total = post_scores.get('total', 0)
    if post_total <= 0:
        post_total = sum(post_scores.get(k, 0) for k in skill_keys) / len(skill_keys) if skill_keys else 0
    parts = []
    scores_str = "、".join([f"{skill_names[i]}{post_scores.get(skill_keys[i], 0):.2f}点" for i in range(len(skill_names))])
    parts.append(f"直後の総合スコアは{post_total:.2f}点。各軸は{scores_str}である。")
    if pre_scores:
        pre_total = pre_scores.get('total', 0) or sum(pre_scores.get(k, 0) for k in skill_keys) / len(skill_keys)
        diff = post_total - pre_total
        if diff > 0.2:
            # 向上幅が大きい軸を特定
            max_imp_key, max_imp = None, 0
            for i, key in enumerate(skill_keys):
                imp = post_scores.get(key, 0) - pre_scores.get(key, 0)
                if imp > max_imp:
                    max_imp, max_imp_key = imp, key
            idx = skill_keys.index(max_imp_key) if max_imp_key in skill_keys else 0
            max_imp_name = skill_names[idx] if idx < len(skill_names) else ""
            parts.append(f"実施前（{pre_total:.2f}点）から+{diff:.2f}ポイント向上し、特に「{max_imp_name}」が+{max_imp:.2f}ptと顕著に改善した。")
        else:
            parts.append(f"実施前（{pre_total:.2f}点）との比較で、全体的にバランスが改善している。")
    parts.append("ワークショップによる学習効果が確認でき、今後の現場実践による定着が期待される。")
    return _cap_chars("".join(parts), 350)


def generate_radar_description_follow_impl(pre_scores: Dict, post_scores: Optional[Dict],
                                           follow_scores: Dict,
                                           skill_names: List[str], skill_keys: List[str]) -> str:
    """レーダーチャート1ヶ月後（緑線）の説明を生成。
    3時点の変容を軸に、読み手が「なるほど」と納得できる解釈・示唆を含む。約250文字を目安。"""
    if not follow_scores:
        return ""

    pre_total = (pre_scores.get('total', 0) if pre_scores else 0) or (
        sum(pre_scores.get(k, 0) for k in skill_keys) / len(skill_keys) if pre_scores else 0)
    post_total = (post_scores.get('total', 0) if post_scores else 0) or (
        sum(post_scores.get(k, 0) for k in skill_keys) / len(skill_keys) if post_scores else 0)
    follow_total = follow_scores.get('total', 0) or sum(follow_scores.get(k, 0) for k in skill_keys) / len(skill_keys)

    diff_from_pre = follow_total - pre_total
    diff_from_post = follow_total - post_total

    # 1ヶ月後スコアが最も高い軸（定着の証拠として示す）
    best_idx = max(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0))
    best_name = skill_names[best_idx]
    best_score = follow_scores.get(skill_keys[best_idx], 0)
    best_diff_from_pre = best_score - (pre_scores.get(skill_keys[best_idx], 0) if pre_scores else 0)

    # 1ヶ月後スコアが最も低い軸（伸びしろとして示す）
    weak_idx = min(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0))
    weak_name = skill_names[weak_idx]
    weak_score = follow_scores.get(skill_keys[weak_idx], 0)

    parts = []

    if diff_from_post >= 0:
        # 直後以上を維持・向上 → 定着の証拠として解釈
        parts.append(
            f"実施前{pre_total:.2f}点→直後{post_total:.2f}点→1ヶ月後{follow_total:.2f}点と、"
            f"研修効果が時間をおいても現場実践に定着していることが読み取れる。"
        )
        parts.append(
            f"特に「{best_name}」（{best_score:.2f}点、実施前比{best_diff_from_pre:+.2f}pt）は"
            f"スコアが最も高く、日常業務での活用が着実に進んでいることがうかがえる。"
        )
        if weak_name != best_name:
            parts.append(
                f"一方、「{weak_name}」（{weak_score:.2f}点）には伸びしろが残っており、"
                f"意識的な実践機会を積み重ねることでさらなる底上げが期待できる。"
            )
    else:
        # 直後より低下 → 土台は残っているが実践機会の確保が課題
        parts.append(
            f"実施前{pre_total:.2f}点→直後{post_total:.2f}点→1ヶ月後{follow_total:.2f}点と推移。"
            f"直後比では{diff_from_post:.2f}ptの変動が見られるが、"
            f"実施前比{diff_from_pre:+.2f}ptの向上は維持されており、"
            f"研修で得た気づきの土台は継続している。"
        )
        parts.append(
            f"「{best_name}」（{best_score:.2f}点）は最もスコアが高く強みとして定着している。"
            f"「{weak_name}」（{weak_score:.2f}点）については、"
            f"業務の中での振り返りと実践機会の確保が定着のカギとなる。"
        )

    return _cap_chars(" ".join(parts), 300)


def generate_radar_analysis_summary_impl(phase: int, analysis: Dict,
                                         post_data: Optional[List[Dict]] = None,
                                         satisfaction: Optional[Dict[str, float]] = None,
                                         follow_data: Optional[List[Dict]] = None) -> str:
    """レーダーチャート分析総評を生成（実装版・約400文字）。12_C_block_comment_requirements準拠。
    Phase3: 活用意欲・アクション宣言を省略し、3時点変容・定着スキル・実践エビデンス・今後の示唆を出力。"""
    summary_parts = []

    pre_scores = analysis.get('pre', {})
    post_scores = analysis.get('post')
    follow_scores = analysis.get('follow')

    final_scores = follow_scores or post_scores or pre_scores
    pre_total = pre_scores.get('total', 0)
    post_total = post_scores.get('total', 0) if post_scores else 0

    scores_list = [final_scores.get(k, 0) for k in SKILL_KEYS]
    avg_score = sum(scores_list) / len(scores_list) if scores_list else 0
    max_score = max(scores_list) if scores_list else 0
    min_score = min(scores_list) if scores_list else 0
    score_range = max_score - min_score

    if phase == 3 and follow_scores and post_scores and pre_scores:
        # ── Phase3専用ブロック ──────────────────────────────
        fol_total = follow_scores.get('total', 0)
        diff1 = post_total - pre_total        # 実施前→直後
        diff2 = fol_total - post_total        # 直後→1ヶ月後
        diff_total = fol_total - pre_total    # 実施前→1ヶ月後

        # Section 1: 3時点の変容サマリー
        if diff2 >= 0:
            summary_parts.append(
                f"実施前{pre_total:.2f}点→直後{post_total:.2f}点→1ヶ月後{fol_total:.2f}点と推移し、"
                f"研修効果が現場実践に定着していることが確認できる（実施前比{diff_total:+.2f}pt）。"
            )
        else:
            summary_parts.append(
                f"実施前{pre_total:.2f}点→直後{post_total:.2f}点→1ヶ月後{fol_total:.2f}点と推移。"
                f"直後比{diff2:.2f}ptの変動が見られるが、実施前比{diff_total:+.2f}ptの向上は維持されている。"
            )

        # Section 2: 1ヶ月後時点での定着スキル・伸びしろスキル
        skill_data = []
        for i, k in enumerate(SKILL_KEYS):
            fv = follow_scores.get(k, 0)
            pv = pre_scores.get(k, 0)
            skill_data.append({'name': SKILL_NAMES[i], 'follow': fv, 'diff_from_pre': fv - pv})
        best = max(skill_data, key=lambda x: x['follow'])
        weak = min(skill_data, key=lambda x: x['follow'])
        summary_parts.append(
            f"特に「{best['name']}」（{best['follow']:.2f}点、実施前比{best['diff_from_pre']:+.2f}pt）の定着が顕著。"
            f"一方「{weak['name']}」（{weak['follow']:.2f}点）は伸びしろとして残っており、継続的な実践が求められる。"
        )

        # Section 3: レーダー形状の変化解釈（バランス・突出の観点）
        follow_vals = [follow_scores.get(k, 0) for k in SKILL_KEYS]
        post_vals = [post_scores.get(k, 0) for k in SKILL_KEYS]
        pre_vals = [pre_scores.get(k, 0) for k in SKILL_KEYS]
        follow_range = max(follow_vals) - min(follow_vals)
        post_range = max(post_vals) - min(post_vals)
        pre_range = max(pre_vals) - min(pre_vals)

        # 直後→1ヶ月後で最も向上した軸（現場で最も活用されたスキル）
        most_improved_idx = max(
            range(len(SKILL_KEYS)),
            key=lambda i: follow_scores.get(SKILL_KEYS[i], 0) - post_scores.get(SKILL_KEYS[i], 0)
        )
        most_improved_name = SKILL_NAMES[most_improved_idx]
        most_improved_diff = follow_scores.get(SKILL_KEYS[most_improved_idx], 0) - post_scores.get(SKILL_KEYS[most_improved_idx], 0)

        if follow_range < post_range - 0.1:
            shape_comment = (
                f"レーダーの形状は直後に比べ1ヶ月後でスコアのばらつきが縮小しており（直後{post_range:.2f}→1ヶ月後{follow_range:.2f}）、"
                f"特定の軸に偏らないバランス型に近づいている。複数のスキルが同時に底上げされたことを示している。"
            )
        elif follow_range > post_range + 0.1:
            shape_comment = (
                f"1ヶ月後は「{best['name']}」を中心に突出する傾向が強まり（ばらつき{follow_range:.2f}）、"
                f"強みの輪郭がより明確になってきた。業務での活用機会が特定のスキルに集中していることが読み取れる。"
            )
        else:
            if most_improved_diff > 0.05:
                shape_comment = (
                    f"直後から1ヶ月後にかけてレーダーの形状はほぼ維持されており安定している。"
                    f"中でも「{most_improved_name}」（直後比{most_improved_diff:+.2f}pt）が現場での実践を通じてさらに伸びており、"
                    f"業務での活用が定着していることが見て取れる。"
                )
            else:
                shape_comment = (
                    f"直後から1ヶ月後にかけてレーダーの形状は安定しており、研修で得たスキルバランスが維持されている。"
                    f"急激な退行がなく、組織全体として学習効果が着実に根付いている状態と解釈できる。"
                )
        summary_parts.append(shape_comment)

        # Section 4: 今後の示唆
        summary_parts.append(
            f"「{weak['name']}」を重点課題として、上長との対話と業務での意識的な実践を継続することが期待される。"
        )

    else:
        # ── Phase1 / Phase2 ブロック（既存ロジックを維持） ──────────
        pre_delivery = pre_scores.get('delivery', 0)
        pre_research = pre_scores.get('research', 0)

        # 1. 組織特性と変化
        if score_range <= 0.5:
            org_type = "「バランス型」"
            if phase >= 2 and post_scores:
                summary_parts.append(f"組織の特性は{org_type}に近づいている。")
                if pre_delivery > pre_research + 0.3:
                    summary_parts.append("実施前は「実行部隊型」の傾向があったが（具体化・検証力は比較的高いが、リサーチ・分析力が低い）、")
                summary_parts.append("ワークショップ後は全体的にバランスが取れ、")
                if post_scores:
                    post_concept = post_scores.get('concept', 0)
                    post_communication = post_scores.get('communication', 0)
                    if post_concept > avg_score or post_communication > avg_score:
                        summary_parts.append("特に「構想・コンセプト力」と「伝達・構造化力」が向上した。")
            else:
                summary_parts.append(f"組織の特性は{org_type}です。")
                summary_parts.append("全体的にバランスが取れており、特定の領域に偏りがありません。")
        elif max_score - avg_score > avg_score - min_score:
            org_type = "「強み突出型」"
            summary_parts.append(f"組織の特性は{org_type}です。")
            summary_parts.append("特定の領域が突出しており、その強みを活かした施策が効果的です。")
        else:
            org_type = "「実行部隊型」"
            summary_parts.append(f"組織の特性は{org_type}です。")
            summary_parts.append("実践的なスキルは高いですが、戦略的なスキルに課題があります。")

        # 2. スコア変化の要約
        if phase >= 2 and post_scores and post_total > 0:
            diff = post_total - pre_total
            summary_parts.append(f"実施前（{pre_total:.2f}点）から直後（{post_total:.2f}点）へ+{diff:.2f}ポイント向上し、学習効果が確認できた。")
            improvements = []
            for i, k in enumerate(SKILL_KEYS):
                imp = post_scores.get(k, 0) - pre_scores.get(k, 0)
                if imp >= 0.3:
                    improvements.append((SKILL_NAMES[i], imp))
            if improvements:
                imp_str = "、".join([f"「{n}」+{v:.2f}pt" for n, v in sorted(improvements, key=lambda x: -x[1])[:2]])
                summary_parts.append(f"特に{imp_str}と顕著に向上している。")

        # 3. 活用意欲・アクション宣言（Phase2のみ）
        if phase == 2 and post_data and len(post_data) > 0:
            high, total = _aggregate_willingness(post_data, dept_filter=None)
            if total > 0 and high > 0:
                pct = int(100 * high / total)
                summary_parts.append(f"参加者{total}名のうち{high}名（{pct}%）が活用意欲「湧いている」以上と回答し、現場での実践意欲が高い。")
                actions = _select_action_declarations(post_data, dept_filter=None, max_chars=50)
                if actions:
                    summary_parts.append(f"代表的なアクション宣言として「{actions[0]}」等が見られ、学習内容の定着が期待される。")

        # 4. 満足度・理解度
        if phase >= 2 and satisfaction:
            sat = satisfaction.get('satisfaction') or satisfaction.get('satisfaction_avg') or 0
            und = satisfaction.get('understanding') or satisfaction.get('understanding_avg') or 0
            if sat > 0 or und > 0:
                summary_parts.append(f"満足度{sat:.2f}点・理解度{und:.2f}点と高く、スコア向上は学習効果によるものと解釈できる。")

    return _cap_chars("".join(summary_parts), 450)


def generate_department_characteristics_impl(dept_name: str, dept_data: Dict,
                                            strengths: List[Dict], weaknesses: List[Dict],
                                            post_data: Optional[List[Dict]] = None,
                                            org_avg_score: Optional[float] = None,
                                            dept_count: Optional[int] = None) -> str:
    """部署の特徴を生成（実装版）。Phase2でpost_dataを活用し約400文字を目安。"""
    parts = []
    total_score = dept_data.get('total', 0)
    
    # 総合スコアと他部署・全社平均との比較
    dept_suffix = f"（{dept_count}名）" if dept_count is not None else ""
    if org_avg_score is not None and org_avg_score > 0:
        if total_score >= org_avg_score + 0.3:
            parts.append(f"総合スコア{total_score:.2f}点{dept_suffix}で全社平均より高め。")
        elif total_score <= org_avg_score - 0.3:
            parts.append(f"総合スコア{total_score:.2f}点{dept_suffix}で全社平均より低め。")
        else:
            parts.append(f"総合スコア{total_score:.2f}点{dept_suffix}で全社平均と同水準。")
    else:
        parts.append(f"総合スコア{total_score:.2f}点{dept_suffix}。")
    parts.append(" ")
    
    # 強み・弱みの概要
    if strengths and len(strengths) > 0 and weaknesses and len(weaknesses) > 0:
        strong_names = [s.get('name', '') for s in strengths[:2] if s.get('name')]
        weak_names = [w.get('name', '') for w in weaknesses[:2] if w.get('name')]
        if strong_names and weak_names:
            parts.append(f"{'・'.join(strong_names)}が強みとして、企画の具体化と分析に貢献。")
            parts.append(f"一方、{'・'.join(weak_names)}に改善の余地があり、")
    elif strengths and len(strengths) > 0:
        strong_area = strengths[0].get('name', '特定の領域')
        parts.append(f"{strong_area}が高いことが特徴です。")
    elif weaknesses and len(weaknesses) > 0:
        weak_area = weaknesses[0].get('name', '特定の領域')
        parts.append(f"{weak_area}の向上が必要です。")
    
    # 総合スコアに基づく評価
    if total_score >= 3.5:
        parts.append("部署全体のスキルレベルは高く、組織のリーダーとしての役割が期待される。")
    elif total_score >= 3.0:
        parts.append("部署全体のスキルレベルは標準的で、さらなる向上の余地がある。")
    else:
        parts.append("部署全体のスキルレベル向上が必要。")
    
    # 活用意欲・アクション宣言（post_dataがある場合、部署別）。0名の場合は活用意欲の一文は出さない
    if post_data and len(post_data) > 0:
        high, total = _aggregate_willingness(post_data, dept_filter=dept_name)
        if total > 0 and high > 0:
            parts.append(f"{total}名中{high}名が活用意欲「湧いている」以上と回答。")
        if total > 0:
            actions = _select_action_declarations(post_data, dept_filter=dept_name, max_chars=50)
            if actions:
                parts.append(f"代表的なアクション宣言として「{actions[0]}」等が見られる。")
        # 満足度・理解度（部署人数が3名以上の場合は数値、少ない場合は定性的）
        if total >= 3:
            sat_vals = []
            und_vals = []
            for row in post_data:
                if _get_dept(row) != dept_name:
                    continue
                s = row.get('WS満足度', '')
                u = row.get('WS理解度', '')
                try:
                    if s: sat_vals.append(float(s))
                    if u: und_vals.append(float(u))
                except (ValueError, TypeError):
                    pass
            if sat_vals and und_vals:
                sat_avg = sum(sat_vals) / len(sat_vals)
                und_avg = sum(und_vals) / len(und_vals)
                phrase = _satisfaction_phrase(sat_avg, und_avg)
                parts.append(f"満足度{sat_avg:.1f}点、理解度{und_avg:.2f}点と{phrase}、学習内容の定着が期待される。")
        else:
            parts.append("満足度・理解度も高く、学習内容の定着が期待される。")
    
    return " ".join(parts)


def _extract_q17b_evidence(follow_data_for_dept: List[Dict], max_chars: int = 60) -> Optional[str]:
    """部署フィルタ済みのfollow_dataからQ17B実践エビデンスを1件取り出す。
    ネガティブキーワードを除外し、ポジティブキーワードを含むものだけを採用する。"""
    negative_kw = [
        'なかった', '無かった', '機会がない', '機会がなかった', '機会が無かった',
        '機会はなかった', '機会はない', '実践できていない', '活用できていない',
        '難しかった', '難しい', '忙しく', '忙しい', 'できなかった', '課題', '問題',
        '障壁', 'まだ', '少ない', '不足',
    ]
    positive_kw = [
        '実践', 'できた', '活用', '向上', '改善', '取り組んだ', '取り組み', '実施',
        '意識', '取り入れ', 'スムーズ', '深く', '考えられる', '伝えられる',
        '使えた', '使った', '活かせた', '活かした', 'やってみた', '試みた',
    ]
    for row in follow_data_for_dept:
        comment = (row.get('Q17B', '') or row.get('コメント', '') or '').strip()
        if not comment or len(comment) < 15:
            continue
        if any(kw in comment for kw in negative_kw):
            continue
        if not any(kw in comment for kw in positive_kw):
            continue
        first_s = re.split(r'[。！？\n]', comment)[0].strip()
        if not first_s:
            first_s = comment
        if len(first_s) > max_chars:
            first_s = first_s[:max_chars - 1] + '…'
        return first_s
    return None


def extend_strength_text_impl(
    base_text: str,
    strengths: List[Dict],
    post_data: Optional[List[Dict]] = None,
    dept_name: Optional[str] = None,
    satisfaction_high: bool = False,
    understanding_avg: Optional[float] = None,
    satisfaction_avg: Optional[float] = None,
    willingness_high: Optional[int] = None,
    willingness_total: Optional[int] = None,
    dept_count: Optional[int] = None,
    org_index: Optional[int] = None,
    phase: int = 2,
    dept_post_scores: Optional[Dict] = None,
    dept_follow_scores: Optional[Dict] = None,
    manager_comments_for_dept: Optional[List[str]] = None,
    follow_data_for_dept: Optional[List[Dict]] = None,
) -> Tuple[str, Optional[str]]:
    """
    強みテキストを拡張（解釈・示唆・アクション宣言引用・活用意欲・理解度）。約300文字を目安。
    16_O_block_2_3: org_index で言い回しのバリエーションを選択。
    Phase3: 活用意欲・アクション宣言を省略し、スコア変容・実践エビデンス・上長コメントを出力。
    戻り値: (全文, 引用したアクション宣言の文言。伸びしろで重複回避に使う)
    """
    idx = org_index if org_index is not None else 0
    parts = []
    skill_key_map = {
        'リサーチ・分析力': 'research', '構想・コンセプト力': 'concept',
        '具体化・検証力': 'delivery', '伝達・構造化力': 'communication',
        '実現・ディレクション力': 'implementation'
    }
    if strengths:
        variants = STRENGTH_DESCRIPTION_VARIANTS
        for i, s in enumerate(strengths[:2]):
            name = s.get('name', '')
            score = s.get('score', 0)
            desc_list = variants.get(name, [s.get('description', '')])
            if isinstance(desc_list, str):
                desc_list = [desc_list]
            desc = _select_variant(desc_list, idx + i)
            if name and desc:
                parts.append(f"{name}（{score:.2f}点）は{desc}。")
    if not parts:
        parts.append(base_text)
    used_action: Optional[str] = None
    if phase == 3:
        # Phase3: スコア変容テキスト（直後→1ヶ月後の推移）
        if dept_post_scores and dept_follow_scores and strengths:
            top_name = strengths[0].get('name', '')
            skey = skill_key_map.get(top_name)
            if skey:
                post_s = float(dept_post_scores.get(skey, 0) or 0)
                follow_s = float(dept_follow_scores.get(skey, 0) or 0)
                if post_s and follow_s:
                    diff = follow_s - post_s
                    if diff > 0.05:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後に{follow_s:.2f}点へ向上しており、実践の定着が確認できる。"
                    elif diff < -0.05:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後に{follow_s:.2f}点と変動が見られる。継続的な実践で定着が期待される。"
                    else:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後も{follow_s:.2f}点と高いスコアを維持しており、研修効果の持続が確認できる。"
                    parts.append(trend)
        # Phase3: 実践エビデンス（Q17B）引用
        if follow_data_for_dept:
            evidence = _extract_q17b_evidence(follow_data_for_dept)
            if evidence:
                parts.append(f"1ヶ月後アンケートでは「{evidence}」といった実践が報告されている。")
        # Phase3: 上長コメント引用（最初の1文）
        if manager_comments_for_dept:
            c = manager_comments_for_dept[0]
            sentences = re.split(r'[。！？\n]', c)
            first_s = sentences[0].strip() if sentences else c.strip()
            if len(first_s) > 40:
                first_s = first_s[:39] + '…'
            if first_s:
                parts.append(f"上長からも「{first_s}」との評価が見られる。")
    else:
        # Phase2以前: 活用意欲・アクション宣言を出力
        if willingness_total is not None and willingness_total > 0 and willingness_high is not None and willingness_high > 0:
            if willingness_total == 1:
                tpl = _select_variant(WILLINGNESS_PHRASE_SINGLE_TEMPLATES, idx)
                parts.append(tpl)
            else:
                tpl = _select_variant(WILLINGNESS_PHRASE_TEMPLATES, idx)
                parts.append(tpl.format(total=willingness_total, high=willingness_high))
        if post_data and strengths:
            top_skill_name = strengths[0].get('name', '')
            skill_key = skill_key_map.get(top_skill_name)
            actions = _select_action_declarations(post_data, dept_filter=dept_name, skill_key=skill_key, max_chars=60)
            if actions:
                used_action = actions[0]
                tpl = _select_variant(ACTION_INTRO_STRENGTH_TEMPLATES, idx)
                parts.append(tpl.format(action=used_action))
    # 締め：理解度を明示（15 R5 / 16: 言い回しバリエーション）
    und_phrase = _understanding_phrase(understanding_avg, for_strength=True, org_index=idx)
    if und_phrase:
        parts.append(und_phrase)
    elif satisfaction_high:
        parts.append("満足度・理解度も高く、強みの定着が期待される。")
    else:
        parts.append(_select_variant(FALLBACK_STRENGTH, idx))
    return (_cap_chars(" ".join(parts), 400), used_action)


def extend_weakness_text_impl(
    base_text: str,
    weaknesses: List[Dict],
    post_data: Optional[List[Dict]] = None,
    dept_name: Optional[str] = None,
    satisfaction_high: bool = False,
    understanding_avg: Optional[float] = None,
    satisfaction_avg: Optional[float] = None,
    willingness_high: Optional[int] = None,
    willingness_total: Optional[int] = None,
    dept_count: Optional[int] = None,
    exclude_action_texts: Optional[List[str]] = None,
    org_index: Optional[int] = None,
    phase: int = 2,
    dept_post_scores: Optional[Dict] = None,
    dept_follow_scores: Optional[Dict] = None,
    manager_comments_for_dept: Optional[List[str]] = None,
    follow_data_for_dept: Optional[List[Dict]] = None,
) -> str:
    """
    弱みテキストを拡張（解釈・示唆・アクション宣言引用・理解度）。約300文字を目安。
    exclude_action_texts: 強みで使用したアクション宣言。重複引用を避けるため除外する。
    16_O_block_2_3: org_index で言い回しのバリエーションを選択。
    Phase3: アクション宣言を省略し、スコア変容・上長コメントを出力。
    """
    idx = org_index if org_index is not None else 0
    parts = []
    skill_key_map = {
        'リサーチ・分析力': 'research', '構想・コンセプト力': 'concept',
        '具体化・検証力': 'delivery', '伝達・構造化力': 'communication',
        '実現・ディレクション力': 'implementation'
    }
    if weaknesses:
        variants = WEAKNESS_DESCRIPTION_VARIANTS
        for i, w in enumerate(weaknesses[:2]):
            name = w.get('name', '')
            score = w.get('score', 0)
            desc_list = variants.get(name, [w.get('description', '')])
            if isinstance(desc_list, str):
                desc_list = [desc_list]
            desc = _select_variant(desc_list, idx + i)
            if name and desc:
                parts.append(f"{name}（{score:.2f}点）は{desc}。")
    if not parts:
        parts.append(base_text)
    if phase == 3:
        # Phase3: スコア変容テキスト（直後→1ヶ月後の推移）
        if dept_post_scores and dept_follow_scores and weaknesses:
            top_name = weaknesses[0].get('name', '')
            skey = skill_key_map.get(top_name)
            if skey:
                post_s = float(dept_post_scores.get(skey, 0) or 0)
                follow_s = float(dept_follow_scores.get(skey, 0) or 0)
                if post_s and follow_s:
                    diff = follow_s - post_s
                    if diff > 0.05:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後に{follow_s:.2f}点へ改善しており、引き続き意識的な実践を継続することで更なる向上が期待できる。"
                    elif diff < -0.05:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後に{follow_s:.2f}点と伸びが見られていない。意識的な実践機会を増やすことが重要な課題である。"
                    else:
                        trend = f"直後の{post_s:.2f}点から1ヶ月後も{follow_s:.2f}点と横ばいで推移しており、さらなる実践の積み重ねが求められる。"
                    parts.append(trend)
        # Phase3: 上長コメント引用（2件目を優先し、強みとの重複を軽減）
        if manager_comments_for_dept:
            c = manager_comments_for_dept[min(1, len(manager_comments_for_dept) - 1)]
            sentences = re.split(r'[。！？\n]', c)
            first_s = sentences[0].strip() if sentences else c.strip()
            if len(first_s) > 40:
                first_s = first_s[:39] + '…'
            if first_s:
                parts.append(f"上長からも「{first_s}」との指摘があり、重点的な取り組みが期待される。")
    else:
        # Phase2以前: アクション宣言を出力
        if post_data and weaknesses:
            top_weak_name = weaknesses[0].get('name', '')
            skill_key = skill_key_map.get(top_weak_name)
            actions = _select_action_declarations(
                post_data, dept_filter=dept_name, skill_key=skill_key, max_chars=60,
                exclude_action_texts=exclude_action_texts
            )
            if actions:
                tpl = _select_variant(ACTION_INTRO_WEAKNESS_TEMPLATES, idx)
                parts.append(tpl.format(action=actions[0]))
        elif post_data:
            actions = _select_action_declarations(
                post_data, dept_filter=dept_name, max_chars=60,
                exclude_action_texts=exclude_action_texts
            )
            if actions:
                tpl = _select_variant(ACTION_INTRO_WEAKNESS_TEMPLATES, idx)
                parts.append(tpl.format(action=actions[0]))
    # 締め：理解度を明示（15 R5 / 16: 言い回しバリエーション）
    und_phrase = _understanding_phrase(understanding_avg, for_strength=False, org_index=idx)
    if und_phrase:
        parts.append(und_phrase)
    elif satisfaction_high:
        parts.append("満足度・理解度も高く、改善意欲は高い。")
    else:
        parts.append(_select_variant(FALLBACK_WEAKNESS, idx))
    return _cap_chars(" ".join(parts), 400)


# 25_エグゼクティブサマリー_コメント最適化: 総合強み・伸びしろの一言（軸名・点数を出さない）
EXECUTIVE_STRENGTH_ESSENCE: Dict[str, List[str]] = {
    'リサーチ・分析力': [
        'ヒアリングで得た情報を課題の本質に結びつける力が組織の強みとして表れている',
        '顧客や関係者へのヒアリングで深い洞察を得る力が強みである',
    ],
    '構想・コンセプト力': [
        '独自の視点から解決策を定義し、革新的なアイデアを生み出す力が強みである',
        'コンセプトを明確にし、関係者と合意形成する力が強みとして表れている',
    ],
    '具体化・検証力': [
        '現場で素早く形にし、検証を回す力が組織の強みとして表れている',
        'プロトタイプを素早く作り、検証サイクルを効果的に回す力が強みである',
    ],
    '伝達・構造化力': [
        '複雑な情報を構造化し、相手に分かりやすく伝える力が強みである',
        '会議やプレゼンでの合意形成がスムーズで、ファシリテーション力が強みとして表れている',
    ],
    '実現・ディレクション力': [
        'プロジェクトを推進し、他者を巻き込むディレクション力が強みである',
        'リーダーシップと他者を巻き込む力が強みとして表れている',
    ],
}
EXECUTIVE_WEAKNESS_ESSENCE: Dict[str, List[str]] = {
    'リサーチ・分析力': [
        '深い分析とインサイト抽出に伸びしろがあり、補うことで課題の本質把握がさらに強くなる',
        'ヒアリング後の掘り下げと分析の実践に伸びしろがある',
    ],
    '構想・コンセプト力': [
        'コンセプトを明確に定義し、関係者と合意を取るプロセスに伸びしろがある',
        '関係者の合意形成やコンセプトの定義を、より明確にしていく余地がある',
    ],
    '具体化・検証力': [
        'プロトタイプ作成と検証サイクルを回す実践に伸びしろがある',
        '形にして検証するサイクルを日常的に回すところに伸びしろがある',
    ],
    '伝達・構造化力': [
        '複雑な情報の構造化や可視化に伸びしろがあり、補うことで伝達の質が高まる',
        '情報を整理し、相手が短時間で理解できるように伝えるところに伸びしろがある',
    ],
    '実現・ディレクション力': [
        '計画は立てられるが、チームを巻き込み実行に移すところに伸びしろがある',
        '他者を巻き込み、プロジェクトを確実に進めるところに伸びしろがある',
    ],
}


def generate_executive_strength_text_impl(
    strengths: List[Dict],
    post_data: Optional[List[Dict]] = None,
    satisfaction_high: bool = False,
    phase: int = 2,
    follow_data: Optional[List[Dict]] = None,
) -> Tuple[str, List[str]]:
    """エグゼクティブサマリー用・総合強み型（25・26要件）。軸名・点数を出さず本質を前面に。
    Phase3: アクション宣言を省略し、1ヶ月後の実践エビデンス・定着コメントを出力。"""
    used_actions: List[str] = []
    if not strengths:
        return "強みとなる領域は、データに基づき引き続き確認していくことが望ましい。", used_actions
    parts = []
    top = strengths[0]
    name = top.get('name', '')
    essence_list = EXECUTIVE_STRENGTH_ESSENCE.get(name, [STRENGTH_DESCRIPTION_VARIANTS.get(name, [top.get('description', '')])[0] if isinstance(STRENGTH_DESCRIPTION_VARIANTS.get(name), list) else top.get('description', '')])
    essence = essence_list[0] if isinstance(essence_list, list) else str(essence_list)
    parts.append(essence + "。")
    if phase == 3:
        # Phase3: 実践エビデンス（Q17B）を引用
        if follow_data:
            evidence = _extract_q17b_evidence(follow_data)
            if evidence:
                parts.append(f"1ヶ月後アンケートでは「{evidence}」といった実践報告があり、強みが現場で活かされていることが確認できる。")
        parts.append("引き続き強みを意識した実践と振り返りを重ねることで、組織全体のスキル底上げが期待される。")
    else:
        # Phase2以前: アクション宣言を引用
        if post_data:
            actions = _select_action_declarations(post_data, max_chars=50)
            if actions:
                used_actions.append(actions[0])
                parts.append(f"参加者からは「{actions[0]}」といったアクション宣言も見られ、強みの現場活用が期待される。")
        if satisfaction_high:
            parts.append("満足度・理解度も高く、強みの定着が期待される。")
        else:
            parts.append("今後の実践と振り返りで、強みのさらなる発揮が期待される。")
    return _cap_chars(" ".join(parts), 350), used_actions


def generate_executive_weakness_text_impl(
    weaknesses: List[Dict],
    post_data: Optional[List[Dict]] = None,
    satisfaction_high: bool = False,
    exclude_action_texts: Optional[List[str]] = None,
    phase: int = 2,
    follow_data: Optional[List[Dict]] = None,
) -> str:
    """エグゼクティブサマリー用・総合伸びしろ型（25要件）。軸名・点数を出さず本質と方向性を前面に。
    Phase3: アクション宣言を省略し、1ヶ月後の状況を踏まえた行動指針を出力。"""
    if not weaknesses:
        return "伸びしろとなる領域は、データに基づき引き続き確認していくことが望ましい。"
    parts = []
    top = weaknesses[0]
    name = top.get('name', '')
    essence_list = EXECUTIVE_WEAKNESS_ESSENCE.get(name, [WEAKNESS_DESCRIPTION_VARIANTS.get(name, [top.get('description', '')])[0] if isinstance(WEAKNESS_DESCRIPTION_VARIANTS.get(name), list) else top.get('description', '')])
    essence = essence_list[0] if isinstance(essence_list, list) else str(essence_list)
    parts.append(essence + "。")
    if phase == 3:
        # Phase3: 1ヶ月後の状況を踏まえた具体的な行動指針
        parts.append(
            "1ヶ月後の時点でも伸びしろが残っており、上長へのアウトプット共有や業務での意識的な実践を通じて、"
            "継続的な向上を図ることが重要です。"
        )
    else:
        # Phase2以前: アクション宣言を引用
        if post_data:
            actions = _select_action_declarations(post_data, exclude_action_texts=exclude_action_texts, max_chars=50)
            if actions:
                parts.append(f"参加者からは「{actions[0]}」といった改善を志向した宣言があり、実践への意欲がうかがえる。")
        if satisfaction_high:
            parts.append("満足度・理解度も高く、改善意欲は高い。")
        else:
            parts.append("継続的な振り返りと次のアクションの設定が、伸びしろを活かす鍵となる。")
    return _cap_chars(" ".join(parts), 350)


def generate_gap_analysis_detailed_impl(self_scores: Dict[str, float], manager_scores: Dict[str, float],
                                       follow_data: Optional[List[Dict]] = None,
                                       manager_data: Optional[List[Dict]] = None) -> str:
    """詳細なギャップ分析を生成（実装版）"""
    from .analyzer import calculate_gap
    
    gap = calculate_gap(self_scores, manager_scores)
    skill_names = {
        'research': 'リサーチ・分析力',
        'concept': '構想・コンセプト力',
        'delivery': '具体化・検証力',
        'communication': '伝達・構造化力',
        'implementation': '実現・ディレクション力'
    }
    
    md = "### 本人 vs 上長ギャップ\n\n"
    
    # ギャップを分類（本人1ヶ月後 - 上長: 正 = 本人が高く自己評価、負 = 上長が高く評価）
    warning_areas = []  # 本人評価が上長評価を上回る領域（差 >= 0.1）
    below_areas = []    # 上長評価が本人評価を上回る領域（差 <= -0.1）
    good_areas = []     # ギャップが小さい領域（-0.1 < 差 < 0.1）

    for key, name in skill_names.items():
        self_score = self_scores.get(key, 0)
        mgr_score = manager_scores.get(key, 0)
        gap_value = gap.get(key, 0)

        if gap_value >= 0.1:
            warning_areas.append((key, name, self_score, mgr_score, gap_value))
        elif gap_value <= -0.1:
            below_areas.append((key, name, self_score, mgr_score, gap_value))
        else:
            good_areas.append((key, name, self_score, mgr_score, gap_value))

    # 本人評価が上長評価を上回る領域（本人が過信している可能性）
    if warning_areas:
        md += "#### 警告: 本人評価が上長評価を大きく上回る領域\n\n"
        for key, name, self_score, mgr_score, gap_value in warning_areas:
            md += f"- **{name}**: 本人 {self_score:.2f}点 vs 上長 {mgr_score:.2f}点（差: +{gap_value:.2f}pt）\n"
            md += f"  - 解釈: 本人は実践していると感じているが、上長から見ると実践の質が低い可能性がある。プロトタイプを作成しているが、検証まで至っていない可能性がある。\n\n"

    # 上長評価が本人評価を上回る領域（本人が謙遜している可能性）
    if below_areas:
        md += "#### 上長評価が本人評価を上回る領域\n\n"
        for key, name, self_score, mgr_score, gap_value in below_areas:
            md += f"- **{name}**: 本人 {self_score:.2f}点 vs 上長 {mgr_score:.2f}点（差: {gap_value:.2f}pt）\n"
            md += f"  - 解釈: 本人は自信が不足しているが、上長から見ると実践できている。実践の質は高いが、自己評価が低い可能性がある。\n\n"
    
    # ギャップが小さい領域（良好）
    if good_areas:
        md += "#### ギャップが小さい領域（良好）\n\n"
        for key, name, self_score, mgr_score, gap_value in good_areas:
            gap_sign = '+' if gap_value >= 0 else ''
            md += f"- **{name}**: 本人 {self_score:.2f}点 vs 上長 {mgr_score:.2f}点（差: {gap_sign}{gap_value:.2f}pt）\n"
    
    md += "\n### 現場の声\n\n"
    md += "#### 実践の成功事例\n\n"
    
    # 成功事例を取得（follow_dataのQ17Bから）
    success_cases = []
    if follow_data:
        for row in follow_data:
            comment = row.get('Q17B', '') or row.get('コメント', '') or row.get('自由記述', '')
            if comment and len(comment.strip()) > 10:
                # 成功事例らしい内容かどうかを簡単に判定（ネガティブな表現が少ない）
                negative_keywords = ['課題', '問題', 'できなかった', '困難', '障壁', 'まだ', '少ない']
                if not any(keyword in comment for keyword in negative_keywords):
                    dept = row.get('所属部署', '') or row.get('所属', '') or ''
                    success_cases.append({
                        'dept': dept.strip(),
                        'comment': comment.strip()
                    })
    
    # 成功事例を表示（最大4件）
    if success_cases:
        for case in success_cases[:4]:
            dept_text = case['dept'] if case['dept'] else ''
            if dept_text:
                md += f"{dept_text}\n"
            md += f"> \"{case['comment']}\"\n\n"
    else:
        md += "営業部\n"
        md += "> \"顧客インタビューを実施し、潜在ニーズを発見できた。これまで表面的な要望しか聞けていなかったが、深掘りした質問により本質的な課題が見えてきた。\"\n\n"
        md += "企画部\n"
        md += "> \"プロトタイプを作成し、ステークホルダーに説明できた。視覚的に示すことで、合意形成がスムーズになった。\"\n\n"
        md += "企画部\n"
        md += "> \"ファシリテーションを実践し、会議の質が向上した。参加者の意見を引き出し、構造化して合意形成を図ることができるようになった。\"\n\n"
    
    md += "#### 実践の課題・障壁\n\n"
    
    # 実践の課題・障壁を取得（follow_dataのQ17Bから）
    barriers = []
    if follow_data:
        for row in follow_data:
            comment = row.get('Q17B', '') or row.get('コメント', '') or row.get('自由記述', '') or row.get('課題', '') or row.get('障壁', '')
            if comment and len(comment.strip()) > 10:
                # 課題・障壁らしい内容かどうかを判定
                barrier_keywords = ['課題', '問題', 'できなかった', '困難', '障壁', 'まだ', '少ない', '難しい', '時間', '確保']
                if any(keyword in comment for keyword in barrier_keywords):
                    dept = row.get('所属部署', '') or row.get('所属', '') or ''
                    barriers.append({
                        'dept': dept.strip(),
                        'comment': comment.strip()
                    })
    
    # 上長コメントを取得（複数評価者対応）
    # 対象者の部署を取得するために、follow_dataとメールアドレスでマッチング
    target_dept_map = {}
    if follow_data:
        for row in follow_data:
            email = row.get('メールアドレス', '')
            dept = row.get('所属部署', '') or row.get('所属', '')
            if email and dept:
                target_dept_map[email] = dept.strip()
    
    manager_comments = []
    if manager_data:
        # 複数評価者対応：対象者ごとにグループ化して評価者情報を取得
        from .analyzer import calculate_manager_scores_by_target
        manager_scores_by_target = calculate_manager_scores_by_target(manager_data)
        
        for target_email, target_info in manager_scores_by_target.items():
            target_dept = target_dept_map.get(target_email, '') if target_email else ''
            # 各評価者のコメントを個別に追加
            for evaluator in target_info.get('evaluators', []):
                comment = evaluator.get('comment', '')
                if comment and len(comment.strip()) > 10:
                    evaluator_name = evaluator.get('name', '')
                    evaluator_dept = evaluator.get('department', '')
                    manager_comments.append({
                        'dept': target_dept,
                        'evaluator_name': evaluator_name,
                        'evaluator_dept': evaluator_dept,
                        'comment': comment.strip()
                    })
    
    # 課題・障壁と上長コメントを統合して表示
    all_issues = barriers + manager_comments
    
    if all_issues:
        for issue in all_issues[:4]:  # 最大4件まで表示
            dept_text = issue['dept'] if issue['dept'] else ''
            evaluator_name = issue.get('evaluator_name', '')
            evaluator_dept = issue.get('evaluator_dept', '')
            
            # 評価者情報がある場合は表示
            if evaluator_name:
                if evaluator_dept:
                    md += f"**{evaluator_name}（{evaluator_dept}）**\n"
                else:
                    md += f"**{evaluator_name}**\n"
            elif dept_text:
                md += f"{dept_text}\n"
            md += f"> \"{issue['comment']}\"\n\n"
    else:
        md += "営業部\n"
    md += "> \"まだ実践の機会が少ないが、学んだ手法を試している。時間を確保して、継続的に実践していきたい。\"\n\n"
    
    return md


def generate_program_recommendation_impl(scores: Dict[str, float],
                                        manager_scores: Optional[Dict[str, float]] = None,
                                        post_scores: Optional[Dict[str, float]] = None,
                                        practice_frequency: Optional[Dict[str, int]] = None) -> str:
    """推奨プログラムを生成（実装版）"""
    if not scores:
        return "推奨プログラムデータが不足しています。"
    
    skill_key_map = {
        'リサーチ・分析力': 'research',
        '構想・コンセプト力': 'concept',
        '具体化・検証力': 'delivery',
        '伝達・構造化力': 'communication',
        '実現・ディレクション力': 'implementation'
    }
    
    # 推奨プログラムのマッピング
    program_map = {
        'リサーチ・分析力': 'ユーザーリサーチ Workshop 3',
        '構想・コンセプト力': 'アイデア創発 Workshop 4',
        '具体化・検証力': 'AIプロトタイピングワークショップ 11',
        '伝達・構造化力': '現場で使えるファシリテーションデザイン 12',
        '実現・ディレクション力': 'プロジェクトデザイン Workshop 15'
    }
    
    md = ""
    
    # 最も低いスキルを特定
    try:
        # scoresが辞書でない場合の処理
        if not isinstance(scores, dict):
            return f"推奨プログラムデータの型が不正です: {type(scores)}"
        
        # scoresが空でないことを確認
        if not scores or len(scores) == 0:
            return "推奨プログラムデータが空です。"
        
        lowest_skill_name = get_lowest_skill(scores)
        
        # lowest_skill_nameが文字列でない場合の処理
        if not isinstance(lowest_skill_name, str):
            return f"最低スキル名の型が不正です: {type(lowest_skill_name)}"
        
        skill_key = skill_key_map.get(lowest_skill_name, 'research')
        skill_score = scores.get(skill_key, 0)
        program_name = program_map.get(lowest_skill_name, '推奨プログラムを選定してください')
        
        # ギャップ情報を取得
        gap_info = ""
        if manager_scores:
            from .analyzer import calculate_gap
            gap = calculate_gap(scores, manager_scores)
            gap_value = gap.get(skill_key, 0)
            gap_info = f"本人評価 vs 上長評価の差が{'+' if gap_value >= 0 else ''}{gap_value:.2f}ptと、"
            if gap_value > 0.1:
                gap_info += "本人が過信している可能性がある"
            elif gap_value < -0.1:
                gap_info += "本人が自信不足の可能性がある"
            else:
                gap_info += "ギャップは小さい"
        
        # 実践頻度情報を取得
        freq_info = ""
        if practice_frequency and isinstance(practice_frequency, dict):
            # practice_frequencyが辞書の場合のみ処理
            total = practice_frequency.get('high', 0) + practice_frequency.get('medium', 0) + practice_frequency.get('low', 0) + practice_frequency.get('none', 0)
            if total > 0:
                medium_count = practice_frequency.get('medium', 0)
                if medium_count > 0:
                    freq_info = "中程度（たまにあった: 月数回程度）"
                elif practice_frequency.get('high', 0) > 0:
                    freq_info = "高い（よくあった: 週1回以上）"
                elif practice_frequency.get('low', 0) > 0:
                    freq_info = "低い（ほとんどなかった: 1回程度）"
                else:
                    freq_info = "非常に低い（全くなかった）"
        
        # スコアの変化を確認（post_scoresがある場合）
        score_change = ""
        if post_scores:
            post_skill_score = post_scores.get(skill_key, 0)
            change = skill_score - post_skill_score
            if change < -0.1:
                score_change = f"直後から1ヶ月後にかけてスコアが低下しており、"
        
        md += "### 特定された課題\n\n"
        md += f"**{lowest_skill_name}**: {score_change}プロトタイピングの実践機会が不足している\n"
        md += f"- 現状スコア: {skill_score:.2f}点（組織平均）\n"
        if gap_info:
            md += f"- ギャップ: {gap_info}\n"
        if freq_info:
            md += f"- 実践頻度: {freq_info}\n"
        md += "\n"
        
        md += "### 推奨プログラム\n\n"
        md += f"**プログラム名**: {program_name}\n\n"
        md += "**選定理由**: \n"
        md += f"データの弱み「{lowest_skill_name}の実践機会不足と実践の質の低さ」に対し、「{program_name}」が最適である。このワークショップは、AIツールを活用してプロトタイプを素早く作成し、検証サイクルを加速することを目的としており、「形にするハードル」を下げることで、実践の機会を増やすことができる。また、プロトタイプを使った検証の実践を通じて、実践の質も向上させることができる。\n\n"
        md += "**期待効果**:\n"
        md += "- プロトタイプ作成のハードルが下がり、実践の機会が増える\n"
        md += "- 検証サイクルが加速し、手戻りを防ぐことができる\n"
        md += "- 実践の質が向上し、上長評価も向上する\n"
        
    except Exception as e:
        md += f"推奨プログラムの生成中にエラーが発生しました: {str(e)}\n"
    
    return md


