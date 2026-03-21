"""
分析ロジックモジュール
GASの分析機能をPythonに移植
"""
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .csv_normalizer import label_to_satisfaction_value, label_to_understanding_value


# 設定
SKILL_AXES = [
    {'name': 'リサーチ・分析力', 'key': 'research', 'questions': ['Q1', 'Q2', 'Q3']},
    {'name': '構想・コンセプト力', 'key': 'concept', 'questions': ['Q4', 'Q5', 'Q6']},
    {'name': '具体化・検証力', 'key': 'delivery', 'questions': ['Q7', 'Q8', 'Q9']},
    {'name': '伝達・構造化力', 'key': 'communication', 'questions': ['Q10', 'Q11', 'Q12']},
    {'name': '実現・ディレクション力', 'key': 'implementation', 'questions': ['Q13', 'Q14', 'Q15']}
]

SCORE_RANGE = {'min': 1, 'max': 5}


def calculate_axis_score(row: Dict, questions: List[str]) -> Optional[float]:
    """スキル軸のスコアを計算（3問の平均）"""
    values = []
    for q in questions:
        val = row.get(q, '')
        if val == '' or val is None:
            continue
        try:
            num = float(val)
            if SCORE_RANGE['min'] <= num <= SCORE_RANGE['max']:
                values.append(num)
        except (ValueError, TypeError):
            continue
    
    if len(values) == 0:
        return None
    
    return sum(values) / len(values)


def calculate_scores(data: List[Dict]) -> Dict[str, float]:
    """スコアを計算"""
    if not data or len(data) == 0:
        return {
            'research': 0.0,
            'concept': 0.0,
            'delivery': 0.0,
            'communication': 0.0,
            'implementation': 0.0,
            'total': 0.0
        }
    
    scores = {
        'research': [],
        'concept': [],
        'delivery': [],
        'communication': [],
        'implementation': [],
        'total': []
    }
    
    for row in data:
        if not row:
            continue
        
        # 各スキル軸のスコアを計算
        research_score = calculate_axis_score(row, SKILL_AXES[0]['questions'])
        concept_score = calculate_axis_score(row, SKILL_AXES[1]['questions'])
        delivery_score = calculate_axis_score(row, SKILL_AXES[2]['questions'])
        communication_score = calculate_axis_score(row, SKILL_AXES[3]['questions'])
        implementation_score = calculate_axis_score(row, SKILL_AXES[4]['questions'])
        
        if research_score is not None:
            scores['research'].append(research_score)
        if concept_score is not None:
            scores['concept'].append(concept_score)
        if delivery_score is not None:
            scores['delivery'].append(delivery_score)
        if communication_score is not None:
            scores['communication'].append(communication_score)
        if implementation_score is not None:
            scores['implementation'].append(implementation_score)
        
        # 総合スコア（全15問の平均）
        all_scores = [
            research_score, concept_score, delivery_score,
            communication_score, implementation_score
        ]
        all_scores = [s for s in all_scores if s is not None]
        
        if len(all_scores) > 0:
            total = sum(all_scores) / len(all_scores)
            scores['total'].append(total)
    
    # 平均を計算
    return {
        'research': statistics.mean(scores['research']) if scores['research'] else 0.0,
        'concept': statistics.mean(scores['concept']) if scores['concept'] else 0.0,
        'delivery': statistics.mean(scores['delivery']) if scores['delivery'] else 0.0,
        'communication': statistics.mean(scores['communication']) if scores['communication'] else 0.0,
        'implementation': statistics.mean(scores['implementation']) if scores['implementation'] else 0.0,
        'total': statistics.mean(scores['total']) if scores['total'] else 0.0
    }


def calculate_question_average(data: List[Dict], question_key: str) -> Optional[float]:
    """特定の質問項目の平均を計算"""
    if not data or len(data) == 0:
        return None
    
    values = []
    for row in data:
        val = row.get(question_key, '')
        if val == '' or val is None:
            continue
        try:
            num = float(val)
            # NPSは0〜10の範囲、その他は1〜5の範囲
            if question_key == 'NPS':
                if 0 <= num <= 10:
                    values.append(num)
            else:
                if SCORE_RANGE['min'] <= num <= SCORE_RANGE['max']:
                    values.append(num)
        except (ValueError, TypeError):
            continue
    
    if len(values) == 0:
        return None
    
    return statistics.mean(values)


def calculate_satisfaction(post_data: List[Dict]) -> Dict[str, float]:
    """満足度を計算（Phase 2）"""
    satisfaction = []
    understanding = []
    nps = []
    
    for row in post_data:
        # WS満足度（5段階: 1-5）
        ws_sat_val = row.get('WS満足度', '')
        if ws_sat_val:
            if isinstance(ws_sat_val, str):
                ws_sat_val = ws_sat_val.strip()
            else:
                ws_sat_val = str(ws_sat_val).strip()
            if ws_sat_val and ws_sat_val != '':
                try:
                    val = float(ws_sat_val)
                    if 1 <= val <= 5:  # 有効範囲をチェック
                        satisfaction.append(val)
                except (ValueError, TypeError):
                    val = label_to_satisfaction_value(ws_sat_val)
                    if val is not None:
                        satisfaction.append(float(val))
        # WS理解度（5段階: 1-5）
        ws_und_val = row.get('WS理解度', '')
        if ws_und_val:
            if isinstance(ws_und_val, str):
                ws_und_val = ws_und_val.strip()
            else:
                ws_und_val = str(ws_und_val).strip()
            if ws_und_val and ws_und_val != '':
                try:
                    val = float(ws_und_val)
                    if 1 <= val <= 5:  # 有効範囲をチェック
                        understanding.append(val)
                except (ValueError, TypeError):
                    val = label_to_understanding_value(ws_und_val)
                    if val is not None:
                        understanding.append(float(val))
        # NPS（11段階: 0-10）
        # 'NPS' または 'NPS(推奨度)' の両方に対応
        nps_val = row.get('NPS', '') or row.get('NPS(推奨度)', '')
        if nps_val:
            if isinstance(nps_val, str):
                nps_val = nps_val.strip()
            else:
                nps_val = str(nps_val).strip()
            if nps_val and nps_val != '':
                try:
                    val = float(nps_val)
                    if 0 <= val <= 10:  # 有効範囲をチェック
                        nps.append(val)
                except (ValueError, TypeError):
                    pass
    
    return {
        'satisfaction': statistics.mean(satisfaction) if satisfaction else 0.0,
        'understanding': statistics.mean(understanding) if understanding else 0.0,
        'nps': statistics.mean(nps) if nps else 0.0
    }


def calculate_practice_frequency(follow_data: List[Dict]) -> Dict[str, int]:
    """実践頻度を計算（Phase 3）"""
    frequency = {
        'high': 0,    # よくあった（週1回以上）
        'medium': 0,  # たまにあった（月数回程度）
        'low': 0,     # ほとんどなかった（1回程度）
        'none': 0     # 全くなかった
    }
    
    for row in follow_data:
        val = row.get('Q16B', '')
        if val == '1' or val == 1:
            frequency['high'] += 1
        elif val == '2' or val == 2:
            frequency['medium'] += 1
        elif val == '3' or val == 3:
            frequency['low'] += 1
        elif val == '4' or val == 4:
            frequency['none'] += 1
    
    return frequency


def calculate_median(values: List[float]) -> float:
    """中央値を計算"""
    if not values or len(values) == 0:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 1:
        # 奇数の場合：中央の値
        return sorted_values[n // 2]
    else:
        # 偶数の場合：中央2つの平均値
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0


def calculate_weighted_median(values: List[float], weights: List[float]) -> float:
    """重み付き中央値を計算"""
    if not values or len(values) == 0:
        return 0.0
    if len(values) != len(weights):
        # 重みの数が一致しない場合は通常の中央値を計算
        return calculate_median(values)
    
    # 各スコアを重み分だけ複製
    weighted_values = []
    for val, weight in zip(values, weights):
        # 重みを整数に丸めて複製回数を決定（例：1.0→1回、2.0→2回）
        count = max(1, int(round(weight)))
        weighted_values.extend([val] * count)
    
    # 複製後のデータセットで中央値を計算
    return calculate_median(weighted_values)


def calculate_manager_scores(manager_data: List[Dict]) -> Dict[str, float]:
    """上長評価を計算（Phase 3）- 後方互換性のため保持"""
    scores = {
        'research': [],
        'concept': [],
        'delivery': [],
        'communication': [],
        'implementation': []
    }
    
    for row in manager_data:
        for i, m_key in enumerate(['M1', 'M2', 'M3', 'M4', 'M5']):
            if m_key in row:
                try:
                    val = float(row[m_key])
                    key = list(scores.keys())[i]
                    scores[key].append(val)
                except (ValueError, TypeError):
                    pass
    
    return {
        'research': statistics.mean(scores['research']) if scores['research'] else 0.0,
        'concept': statistics.mean(scores['concept']) if scores['concept'] else 0.0,
        'delivery': statistics.mean(scores['delivery']) if scores['delivery'] else 0.0,
        'communication': statistics.mean(scores['communication']) if scores['communication'] else 0.0,
        'implementation': statistics.mean(scores['implementation']) if scores['implementation'] else 0.0
    }


def calculate_manager_scores_by_target(manager_data: List[Dict]) -> Dict[str, Dict]:
    """
    対象者ごとに上長評価を計算（複数評価者対応）
    
    Returns:
        Dict[str, Dict]: 対象者メールアドレスをキーとした辞書
        {
            'user@example.com': {
                'manager_scores': {'research': 4.0, ...},
                'evaluators': [
                    {
                        'email': 'manager1@example.com',
                        'name': '上司 一郎',
                        'department': '営業部',
                        'weight': 1.0,
                        'scores': {'research': 4, ...},
                        'comment': 'コメント'
                    },
                    ...
                ],
                'evaluator_count': 3
            },
            ...
        }
    """
    # 対象者ごとにグループ化
    target_groups = {}
    
    for row in manager_data:
        target_email = row.get('対象者メールアドレス', '') or row.get('メールアドレス', '')
        if not target_email:
            continue
        
        if target_email not in target_groups:
            target_groups[target_email] = []
        
        # 評価者情報を抽出
        evaluator_info = {
            'email': row.get('上長メールアドレス', '') or row.get('メールアドレス', ''),
            'name': row.get('上長氏名', '') or row.get('氏名', ''),
            'department': row.get('上長部署', '') or row.get('所属部署', ''),
            'weight': 1.0,  # デフォルト値
            'scores': {},
            'comment': row.get('M7', '') or row.get('上長コメント', '') or row.get('コメント', '')
        }
        
        # 重みを取得（あれば）
        weight_str = row.get('評価者重み', '') or row.get('重み', '')
        if weight_str:
            try:
                evaluator_info['weight'] = float(weight_str)
            except (ValueError, TypeError):
                pass
        
        # スコアを抽出
        skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
        for i, m_key in enumerate(['M1', 'M2', 'M3', 'M4', 'M5']):
            if m_key in row:
                try:
                    val = float(row[m_key])
                    evaluator_info['scores'][skill_keys[i]] = val
                except (ValueError, TypeError):
                    pass
        
        target_groups[target_email].append(evaluator_info)
    
    # 各対象者ごとに中央値を計算
    result = {}
    for target_email, evaluators in target_groups.items():
        if not evaluators:
            continue
        
        # 各スキル軸ごとにスコアを収集
        skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
        scores_by_skill = {key: [] for key in skill_keys}
        weights_by_skill = {key: [] for key in skill_keys}
        
        for evaluator in evaluators:
            for skill_key in skill_keys:
                if skill_key in evaluator['scores']:
                    scores_by_skill[skill_key].append(evaluator['scores'][skill_key])
                    weights_by_skill[skill_key].append(evaluator['weight'])
        
        # 中央値を計算（重み付けがある場合は重み付き中央値）
        manager_scores = {}
        has_weights = any(w != 1.0 for weights in weights_by_skill.values() for w in weights)
        
        for skill_key in skill_keys:
            if scores_by_skill[skill_key]:
                if has_weights and len(scores_by_skill[skill_key]) == len(weights_by_skill[skill_key]):
                    manager_scores[skill_key] = calculate_weighted_median(
                        scores_by_skill[skill_key],
                        weights_by_skill[skill_key]
                    )
                else:
                    manager_scores[skill_key] = calculate_median(scores_by_skill[skill_key])
            else:
                manager_scores[skill_key] = 0.0
        
        result[target_email] = {
            'manager_scores': manager_scores,
            'evaluators': evaluators,
            'evaluator_count': len(evaluators)
        }
    
    return result


def calculate_gap(self_scores: Dict[str, float], manager_scores: Dict[str, float]) -> Dict[str, float]:
    """ギャップを計算（本人1ヶ月後評価 - 上長評価）: 正 = 本人が高く自己評価、負 = 上長が高く評価"""
    return {
        'research': self_scores['research'] - manager_scores['research'],
        'concept': self_scores['concept'] - manager_scores['concept'],
        'delivery': self_scores['delivery'] - manager_scores['delivery'],
        'communication': self_scores['communication'] - manager_scores['communication'],
        'implementation': self_scores['implementation'] - manager_scores['implementation']
    }


def detect_phase(uploaded_files: Dict[str, str]) -> int:
    """フェーズを自動判定"""
    has_pre = 'pre' in uploaded_files
    has_post = 'post' in uploaded_files
    has_follow = 'follow' in uploaded_files
    
    if not has_pre:
        return 0
    if has_pre and not has_post:
        return 1
    if has_pre and has_post and not has_follow:
        return 2
    if has_pre and has_post and has_follow:
        return 3
    return 0


def validate_email_consistency(pre_data: List[Dict], post_data: Optional[List[Dict]],
                               phase: int) -> Tuple[bool, Optional[str]]:
    """
    実施前・直後のメールアドレス整合性を検証する。
    Phase 2 以上かつ post_data がある場合のみ検証。
    Returns: (is_valid, error_message)
    """
    if phase < 2 or not post_data:
        return True, None

    # 実施前のメール重複チェック
    pre_by_email: Dict[str, List[str]] = {}
    for row in pre_data:
        email = (row.get('メールアドレス', '') or '').strip()
        if not email:
            continue
        name = (row.get('氏名', '') or '').strip() or email
        if email not in pre_by_email:
            pre_by_email[email] = []
        pre_by_email[email].append(name)
    for email, names in pre_by_email.items():
        unique_names = list(dict.fromkeys(names))
        if len(unique_names) > 1:
            names_str = '、'.join(f'{n}さん' for n in unique_names)
            return False, (
                f'エラー: メールアドレスの重複が検出されました。実施前.csvで、'
                f'メールアドレス「{email}」が複数の方（{names_str}）で登録されています。'
                f'実施前.csvのメールアドレスを確認し、修正してください。'
            )

    # 直後のメール重複チェック
    post_by_email: Dict[str, List[str]] = {}
    for row in post_data:
        email = (row.get('メールアドレス', '') or '').strip()
        if not email:
            continue
        name = (row.get('氏名', '') or '').strip() or email
        if email not in post_by_email:
            post_by_email[email] = []
        post_by_email[email].append(name)
    for email, names in post_by_email.items():
        unique_names = list(dict.fromkeys(names))
        if len(unique_names) > 1:
            names_str = '、'.join(f'{n}さん' for n in unique_names)
            return False, (
                f'エラー: メールアドレスの重複が検出されました。直後.csvで、'
                f'メールアドレス「{email}」が複数の方（{names_str}）で登録されています。'
                f'直後.csvのメールアドレスを確認し、修正してください。'
            )

    # 実施前と直後の不一致チェック（実施前にいる人が直後にマッチしない）
    post_emails = set(post_by_email.keys())
    unmatched_names = []
    for row in pre_data:
        email = (row.get('メールアドレス', '') or '').strip()
        if not email:
            continue
        if email not in post_emails:
            name = (row.get('氏名', '') or '').strip() or email
            if name not in unmatched_names:
                unmatched_names.append(name)
    if unmatched_names:
        names_str = '、'.join(f'{n}さん' for n in unmatched_names)
        return False, (
            f'エラー: メールアドレスの不一致が検出されました。実施前.csvに登録されている'
            f'以下の方のメールアドレスが、直後.csvと一致していません：{names_str}。'
            f'実施前と直後で同じメールアドレスを使用しているか確認し、CSVを修正してください。'
        )

    return True, None


def analyze_phase1(pre_data: List[Dict]) -> Dict:
    """Phase 1 分析"""
    if not pre_data or len(pre_data) == 0:
        raise ValueError('実施前のデータが空です。')
    
    pre_scores = calculate_scores(pre_data)
    if pre_scores['total'] == 0:
        raise ValueError('スコアの計算に失敗しました。データを確認してください。')
    
    return {
        'pre': pre_scores,
        'participant_count': len(pre_data)
    }


def analyze_phase2(pre_data: List[Dict], post_data: List[Dict]) -> Dict:
    """Phase 2 分析"""
    if not pre_data or len(pre_data) == 0:
        raise ValueError('実施前のデータが空です。')
    if not post_data or len(post_data) == 0:
        raise ValueError('直後のデータが空です。')
    
    pre_scores = calculate_scores(pre_data)
    post_scores = calculate_scores(post_data)
    
    if pre_scores['total'] == 0:
        raise ValueError('実施前のスコア計算に失敗しました。')
    if post_scores['total'] == 0:
        raise ValueError('直後のスコア計算に失敗しました。')
    
    return {
        'pre': pre_scores,
        'post': post_scores,
        'participant_count': len(post_data),
        'satisfaction': calculate_satisfaction(post_data)
    }


def analyze_phase3(pre_data: List[Dict], post_data: List[Dict], 
                   follow_data: List[Dict], manager_data: Optional[List[Dict]] = None) -> Dict:
    """Phase 3 分析"""
    if not pre_data or len(pre_data) == 0:
        raise ValueError('実施前のデータが空です。')
    if not post_data or len(post_data) == 0:
        raise ValueError('直後のデータが空です。')
    if not follow_data or len(follow_data) == 0:
        raise ValueError('1ヶ月後のデータが空です。')
    
    pre_scores = calculate_scores(pre_data)
    post_scores = calculate_scores(post_data)
    follow_scores = calculate_scores(follow_data)
    
    if pre_scores['total'] == 0:
        raise ValueError('実施前のスコア計算に失敗しました。')
    if post_scores['total'] == 0:
        raise ValueError('直後のスコア計算に失敗しました。')
    if follow_scores['total'] == 0:
        raise ValueError('1ヶ月後のスコア計算に失敗しました。')
    
    analysis = {
        'pre': pre_scores,
        'post': post_scores,
        'follow': follow_scores,
        'participant_count': len(follow_data),
        'practice_frequency': calculate_practice_frequency(follow_data)
    }
    
    # 満足度データを追加（Phase 3でも満足度分析を表示するため）
    if post_data and len(post_data) > 0:
        analysis['satisfaction'] = calculate_satisfaction(post_data)
    
    if manager_data and len(manager_data) > 0:
        # 複数評価者対応：対象者ごとに集計
        manager_scores_by_target = calculate_manager_scores_by_target(manager_data)
        
        # 全対象者のスコアを平均して組織全体のスコアを計算（後方互換性のため）
        all_manager_scores = {
            'research': [],
            'concept': [],
            'delivery': [],
            'communication': [],
            'implementation': []
        }
        
        for target_info in manager_scores_by_target.values():
            scores = target_info['manager_scores']
            for key in all_manager_scores.keys():
                if scores.get(key, 0) > 0:
                    all_manager_scores[key].append(scores[key])
        
        # 組織全体の平均スコアを計算
        manager_scores = {
            'research': statistics.mean(all_manager_scores['research']) if all_manager_scores['research'] else 0.0,
            'concept': statistics.mean(all_manager_scores['concept']) if all_manager_scores['concept'] else 0.0,
            'delivery': statistics.mean(all_manager_scores['delivery']) if all_manager_scores['delivery'] else 0.0,
            'communication': statistics.mean(all_manager_scores['communication']) if all_manager_scores['communication'] else 0.0,
            'implementation': statistics.mean(all_manager_scores['implementation']) if all_manager_scores['implementation'] else 0.0
        }
        
        if manager_scores['research'] > 0:  # 有効なデータがあるか確認
            analysis['manager'] = manager_scores
            analysis['gap'] = calculate_gap(follow_scores, manager_scores)
            # 複数評価者対応：対象者ごとの詳細情報も保持
            analysis['manager_by_target'] = manager_scores_by_target
    
    return analysis


def get_highest_skill(scores: Dict[str, float]) -> str:
    """最高スコアのスキル軸を取得"""
    skills = [
        {'name': 'リサーチ・分析力', 'score': scores['research']},
        {'name': '構想・コンセプト力', 'score': scores['concept']},
        {'name': '具体化・検証力', 'score': scores['delivery']},
        {'name': '伝達・構造化力', 'score': scores['communication']},
        {'name': '実現・ディレクション力', 'score': scores['implementation']}
    ]
    
    return max(skills, key=lambda x: x['score'])['name']


def get_lowest_skill(scores: Dict[str, float]) -> str:
    """最低スコアのスキル軸を取得"""
    # scoresが辞書でない場合の処理
    if not isinstance(scores, dict):
        raise TypeError(f"scores must be a dict, got {type(scores)}")
    
    # 必要なキーが存在するか確認
    required_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    for key in required_keys:
        if key not in scores:
            raise KeyError(f"Required key '{key}' not found in scores")
    
    skills = [
        {'name': 'リサーチ・分析力', 'score': scores.get('research', 0.0)},
        {'name': '構想・コンセプト力', 'score': scores.get('concept', 0.0)},
        {'name': '具体化・検証力', 'score': scores.get('delivery', 0.0)},
        {'name': '伝達・構造化力', 'score': scores.get('communication', 0.0)},
        {'name': '実現・ディレクション力', 'score': scores.get('implementation', 0.0)}
    ]
    
    # スコアが数値であることを確認
    for skill in skills:
        if not isinstance(skill['score'], (int, float)):
            raise TypeError(f"Score must be a number, got {type(skill['score'])} for {skill['name']}")
    
    result = min(skills, key=lambda x: x['score'])
    if not isinstance(result, dict) or 'name' not in result:
        raise ValueError(f"get_lowest_skill returned invalid result: {result}")
    
    return result['name']


def identify_strengths(scores: Dict[str, float]) -> List[Dict]:
    """強みを特定（平均スコアより高いスキル、なければ最高スコアを1件返す）"""
    # 各スキル軸に対する具体的な説明
    skill_descriptions = {
        'リサーチ・分析力': '顧客や関係者へのヒアリングで深い洞察を得る能力が高く、課題の本質を把握できている',
        '構想・コンセプト力': '独自の視点から解決策を定義する能力が向上し、革新的なアイデア創出が可能になっている',
        '具体化・検証力': 'プロトタイプを素早く作成し、検証サイクルを効果的に回す能力が高い',
        '伝達・構造化力': '会議やプレゼンテーションでの合意形成がスムーズで、ファシリテーションスキルが確立されている',
        '実現・ディレクション力': 'プロジェクト推進におけるリーダーシップが発揮され、他者を巻き込む能力が向上している'
    }
    
    skills = [
        {'name': 'リサーチ・分析力', 'score': scores['research']},
        {'name': '構想・コンセプト力', 'score': scores['concept']},
        {'name': '具体化・検証力', 'score': scores['delivery']},
        {'name': '伝達・構造化力', 'score': scores['communication']},
        {'name': '実現・ディレクション力', 'score': scores['implementation']}
    ]
    
    # 0.0以下のスコア（データがない）を除外
    valid_skills = [s for s in skills if s['score'] > 0.0]
    if not valid_skills:
        return []
    
    # 平均スコアを計算
    avg_score = sum(s['score'] for s in valid_skills) / len(valid_skills)
    
    # 平均より高いスコアの領域を強みとして識別（最大3件、スコア降順）
    strengths = [
        {
            'name': s['name'],
            'score': s['score'],
            'description': skill_descriptions.get(s['name'], 'スコアが高く、組織の強みとなっています。')
        }
        for s in sorted(valid_skills, key=lambda x: x['score'], reverse=True)
        if s['score'] > avg_score
    ]
    
    # 強みが見つからない場合は、最高スコアの領域を1件返す
    if not strengths:
        highest = max(valid_skills, key=lambda x: x['score'])
        strengths = [{
            'name': highest['name'],
            'score': highest['score'],
            'description': skill_descriptions.get(highest['name'], '他の領域と比較してスコアが高く、強みとなっています。')
        }]
    
    return strengths[:3]


def identify_weaknesses(scores: Dict[str, float]) -> List[Dict]:
    """弱みを特定"""
    # 各スキル軸に対する具体的な説明
    skill_descriptions = {
        'リサーチ・分析力': '基礎スキルは向上しているが、深い分析とインサイト抽出に課題がある',
        '構想・コンセプト力': 'アイデア発想はできているが、コンセプトを明確に定義し、関係者の合意形成に課題がある',
        '具体化・検証力': 'プロトタイプ作成の実践機会が不足し、検証サイクルが効果的に回されていない',
        '伝達・構造化力': '情報伝達はできているが、複雑な情報の構造化や可視化に課題がある',
        '実現・ディレクション力': '計画立案はできているが、チームを巻き込んだ実行や品質管理に課題がある'
    }
    
    skills = [
        {'name': 'リサーチ・分析力', 'score': scores['research']},
        {'name': '構想・コンセプト力', 'score': scores['concept']},
        {'name': '具体化・検証力', 'score': scores['delivery']},
        {'name': '伝達・構造化力', 'score': scores['communication']},
        {'name': '実現・ディレクション力', 'score': scores['implementation']}
    ]
    
    # 0.0以下のスコア（データがない）を除外
    valid_skills = [s for s in skills if s['score'] > 0.0]
    
    # 有効なスキルがない場合は空のリストを返す
    if not valid_skills:
        return []
    
    # 平均スコアを計算（有効なスキルのみ）
    avg_score = sum(s['score'] for s in valid_skills) / len(valid_skills)
    
    # 平均より低いスコアの領域を弱みとして識別（最低2つ、最大2つ）
    weaknesses = [
        {
            'name': s['name'],
            'score': s['score'],
            'description': skill_descriptions.get(s['name'], 'スコアが低く、補強が必要な領域です。')
        }
        for s in sorted(valid_skills, key=lambda x: x['score'])
        if s['score'] < avg_score
    ]
    
    # 弱みが見つからない場合は、最低スコアの領域を1つ返す
    if not weaknesses:
        sorted_skills = sorted(valid_skills, key=lambda x: x['score'])
        if sorted_skills:
            lowest = sorted_skills[0]
            weaknesses = [{
                'name': lowest['name'],
                'score': lowest['score'],
                'description': skill_descriptions.get(lowest['name'], '他の領域と比較してスコアが低めです。さらなる向上の余地があります。')
            }]
    
    return weaknesses[:2]


def analyze_by_department(data: List[Dict]) -> Dict[str, Dict]:
    """部署別分析"""
    dept_scores = {}
    
    for row in data:
        # 所属部署のキーを複数試す（BOM対応）。前後空白で別キーにならないよう strip（業務システム課スコア不一致原因追求）
        dept_raw = row.get('所属部署', '') or row.get('﻿所属部署', '') or row.get('所属', '') or row.get('﻿所属', '') or ''
        dept = (dept_raw.strip() if isinstance(dept_raw, str) else str(dept_raw or '').strip()) or 'その他'
        if dept not in dept_scores:
            dept_scores[dept] = []
        
        # 個人スコアを計算
        research_score = calculate_axis_score(row, SKILL_AXES[0]['questions'])
        concept_score = calculate_axis_score(row, SKILL_AXES[1]['questions'])
        delivery_score = calculate_axis_score(row, SKILL_AXES[2]['questions'])
        communication_score = calculate_axis_score(row, SKILL_AXES[3]['questions'])
        implementation_score = calculate_axis_score(row, SKILL_AXES[4]['questions'])
        
        all_scores = [s for s in [research_score, concept_score, delivery_score, 
                                   communication_score, implementation_score] if s is not None]
        if len(all_scores) > 0:
            total = sum(all_scores) / len(all_scores)
            dept_scores[dept].append({
                'research': research_score or 0,
                'concept': concept_score or 0,
                'delivery': delivery_score or 0,
                'communication': communication_score or 0,
                'implementation': implementation_score or 0,
                'total': total
            })
    
    # 部署別平均を計算
    result = {}
    for dept, scores in dept_scores.items():
        if len(scores) > 0:
            # 各スキル軸の平均を計算（0より大きい値のみ）
            research_vals = [s['research'] for s in scores if s['research'] and s['research'] > 0]
            concept_vals = [s['concept'] for s in scores if s['concept'] and s['concept'] > 0]
            delivery_vals = [s['delivery'] for s in scores if s['delivery'] and s['delivery'] > 0]
            communication_vals = [s['communication'] for s in scores if s['communication'] and s['communication'] > 0]
            implementation_vals = [s['implementation'] for s in scores if s['implementation'] and s['implementation'] > 0]
            total_vals = [s['total'] for s in scores if s['total'] and s['total'] > 0]
            
            # 有効なデータがある場合のみ結果に含める
            # 少なくとも1つのスキル軸に有効なデータがある場合のみ
            if research_vals or concept_vals or delivery_vals or communication_vals or implementation_vals or total_vals:
                result[dept] = {
                    'count': len(scores),
                    'research': statistics.mean(research_vals) if research_vals else 0.0,
                    'concept': statistics.mean(concept_vals) if concept_vals else 0.0,
                    'delivery': statistics.mean(delivery_vals) if delivery_vals else 0.0,
                    'communication': statistics.mean(communication_vals) if communication_vals else 0.0,
                    'implementation': statistics.mean(implementation_vals) if implementation_vals else 0.0,
                    'total': statistics.mean(total_vals) if total_vals else 0.0
                }
    
    return result


def _email_local_match(email_a: str, email_b: str) -> bool:
    """メールアドレスの照合：完全一致、または@より前の部分が一致すればTrue"""
    if not email_a or not email_b:
        return False
    if email_a == email_b:
        return True
    local_a = email_a.split('@')[0] if '@' in email_a else email_a
    local_b = email_b.split('@')[0] if '@' in email_b else email_b
    return local_a == local_b


def analyze_individual_progress(pre_data: List[Dict], post_data: Optional[List[Dict]] = None,
                                follow_data: Optional[List[Dict]] = None) -> List[Dict]:
    """個人別スコア推移分析"""
    results = []

    # メールアドレスをキーにマッチング
    for pre_row in pre_data:
        email = pre_row.get('メールアドレス', '')
        if not email:
            continue
        
        pre_scores = {
            'research': calculate_axis_score(pre_row, SKILL_AXES[0]['questions']) or 0,
            'concept': calculate_axis_score(pre_row, SKILL_AXES[1]['questions']) or 0,
            'delivery': calculate_axis_score(pre_row, SKILL_AXES[2]['questions']) or 0,
            'communication': calculate_axis_score(pre_row, SKILL_AXES[3]['questions']) or 0,
            'implementation': calculate_axis_score(pre_row, SKILL_AXES[4]['questions']) or 0,
        }
        pre_total = sum(pre_scores.values()) / len([v for v in pre_scores.values() if v > 0])
        
        post_scores = None
        post_total = None
        post_row = None
        if post_data:
            post_row = next((r for r in post_data if _email_local_match(r.get('メールアドレス', ''), email)), None)
            if post_row:
                post_scores = {
                    'research': calculate_axis_score(post_row, SKILL_AXES[0]['questions']) or 0,
                    'concept': calculate_axis_score(post_row, SKILL_AXES[1]['questions']) or 0,
                    'delivery': calculate_axis_score(post_row, SKILL_AXES[2]['questions']) or 0,
                    'communication': calculate_axis_score(post_row, SKILL_AXES[3]['questions']) or 0,
                    'implementation': calculate_axis_score(post_row, SKILL_AXES[4]['questions']) or 0,
                }
                post_total = sum(post_scores.values()) / len([v for v in post_scores.values() if v > 0])
        
        follow_scores = None
        follow_total = None
        follow_row = None
        if follow_data:
            follow_row = next((r for r in follow_data if _email_local_match(r.get('メールアドレス', ''), email)), None)
            if follow_row:
                follow_scores = {
                    'research': calculate_axis_score(follow_row, SKILL_AXES[0]['questions']) or 0,
                    'concept': calculate_axis_score(follow_row, SKILL_AXES[1]['questions']) or 0,
                    'delivery': calculate_axis_score(follow_row, SKILL_AXES[2]['questions']) or 0,
                    'communication': calculate_axis_score(follow_row, SKILL_AXES[3]['questions']) or 0,
                    'implementation': calculate_axis_score(follow_row, SKILL_AXES[4]['questions']) or 0,
                }
                follow_total = sum(follow_scores.values()) / len([v for v in follow_scores.values() if v > 0])
        
        # 表示名: CSVの「氏名」（フォームの「あなたの氏名を入力してください。」等）を優先。実施前→直後→1ヶ月後の順で取得。いずれも空の場合はメール@前をフォールバックとする
        display_name = (pre_row.get('氏名') or '').strip()
        if not display_name and post_row:
            display_name = (post_row.get('氏名') or '').strip()
        if not display_name and follow_row:
            display_name = (follow_row.get('氏名') or '').strip()
        if not display_name and email:
            display_name = email.split('@')[0] if '@' in email else email
        # 所属部署: 直後.csvを優先、無ければ実施前.csv（20_個別レポート_所属部署表示要件）
        dept = ''
        if post_row:
            dept = (post_row.get('所属部署', '') or post_row.get('\ufeff所属部署', '') or '').strip()
        if not dept and pre_row:
            dept = (pre_row.get('所属部署', '') or pre_row.get('\ufeff所属部署', '') or '').strip()
        results.append({
            'email': email,
            'name': display_name,
            'department': dept,
            'pre': pre_scores,
            'pre_total': pre_total,
            'post': post_scores,
            'post_total': post_total,
            'follow': follow_scores,
            'follow_total': follow_total
        })
    
    return results


def analyze_manager_comparison(follow_data: List[Dict], manager_data: List[Dict]) -> List[Dict]:
    """本人上長比較分析（複数評価者対応）"""
    results = []
    
    # 対象者ごとに上長評価を集計
    manager_scores_by_target = calculate_manager_scores_by_target(manager_data)
    
    for follow_row in follow_data:
        email = follow_row.get('メールアドレス', '')
        if not email:
            continue
        
        # 本人評価
        self_scores = {
            'research': calculate_axis_score(follow_row, SKILL_AXES[0]['questions']) or 0,
            'concept': calculate_axis_score(follow_row, SKILL_AXES[1]['questions']) or 0,
            'delivery': calculate_axis_score(follow_row, SKILL_AXES[2]['questions']) or 0,
            'communication': calculate_axis_score(follow_row, SKILL_AXES[3]['questions']) or 0,
            'implementation': calculate_axis_score(follow_row, SKILL_AXES[4]['questions']) or 0,
        }
        self_total = sum(self_scores.values()) / len([v for v in self_scores.values() if v > 0])
        
        # 上長評価（複数評価者の中央値）
        manager_info = manager_scores_by_target.get(email)
        manager_scores = None
        manager_total = None
        evaluators = []
        evaluator_count = 0
        
        if manager_info:
            manager_scores = manager_info['manager_scores']
            evaluators = manager_info['evaluators']
            evaluator_count = manager_info['evaluator_count']
            if manager_scores:
                manager_total = sum(manager_scores.values()) / len([v for v in manager_scores.values() if v > 0])
        
        if manager_scores:
            gap = calculate_gap(self_scores, manager_scores)
            gap_total = self_total - manager_total
        else:
            gap = None
            gap_total = None
        
        results.append({
            'email': email,
            'name': follow_row.get('氏名', ''),
            'department': follow_row.get('所属部署', ''),
            'self': self_scores,
            'self_total': self_total,
            'manager': manager_scores,
            'manager_total': manager_total,
            'gap': gap,
            'gap_total': gap_total,
            'evaluators': evaluators,
            'evaluator_count': evaluator_count
        })
    
    return results

