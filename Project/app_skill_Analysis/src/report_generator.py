"""
レポート生成モジュール
Markdown形式のレポートとCSV形式の分析表を生成
"""
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
from .analyzer import (
    SKILL_AXES, get_highest_skill, get_lowest_skill,
    calculate_question_average, identify_strengths, identify_weaknesses,
    _email_local_match
)
from .csv_normalizer import label_to_satisfaction_value, label_to_understanding_value

# AI生成機能は本アプリでは使用しない（USE_AI = False）
AI_AVAILABLE = False
USE_AI = False


# ここに元のreport_generator.pyの関数を追加する必要があります
# ただし、完全な復元は難しいため、最小限の実装を提供します

# 実装版の関数を使用
try:
    from .report_generator_impl import (
        generate_summary_comment_impl,
        generate_radar_analysis_summary_impl,
        generate_radar_description_pre_extended_impl,
        generate_radar_description_post_extended_impl,
        generate_radar_description_follow_impl,
        SKILL_NAMES,
        SKILL_KEYS,
        generate_department_characteristics_impl,
        extend_strength_text_impl,
        extend_weakness_text_impl,
        generate_executive_strength_text_impl,
        generate_executive_weakness_text_impl,
        _aggregate_willingness,
        generate_gap_analysis_detailed_impl,
        generate_program_recommendation_impl
    )
    
    def generate_summary_comment(phase: int, pre_scores: Dict[str, float],
                                 post_scores: Optional[Dict[str, float]] = None,
                                 follow_scores: Optional[Dict[str, float]] = None,
                                 project_name: str = "", num_participants: int = 0,
                                 post_data: Optional[List[Dict]] = None,
                                 satisfaction: Optional[Dict[str, float]] = None) -> str:
        """総評コメントを生成"""
        return generate_summary_comment_impl(phase, pre_scores, post_scores, follow_scores,
                                            project_name, num_participants, post_data, satisfaction)
    
    def generate_radar_analysis_summary(phase: int, analysis: Dict,
                                        post_data: Optional[List[Dict]] = None,
                                        satisfaction: Optional[Dict[str, float]] = None,
                                        follow_data: Optional[List[Dict]] = None) -> str:
        """レーダーチャート分析総評を生成（12_C_block: 約400文字）"""
        return generate_radar_analysis_summary_impl(phase, analysis, post_data, satisfaction, follow_data)
    
    def generate_department_characteristics(dept_name: str, dept_data: Dict,
                                            strengths: List[Dict], weaknesses: List[Dict],
                                            post_data: Optional[List[Dict]] = None,
                                            org_avg_score: Optional[float] = None,
                                            dept_count: Optional[int] = None) -> str:
        """部署の特徴を生成"""
        return generate_department_characteristics_impl(dept_name, dept_data, strengths, weaknesses,
                                                       post_data, org_avg_score, dept_count)
    
    def generate_gap_analysis_detailed(self_scores: Dict[str, float], manager_scores: Dict[str, float],
                                       follow_data: Optional[List[Dict]] = None,
                                       manager_data: Optional[List[Dict]] = None) -> str:
        """詳細なギャップ分析を生成"""
        return generate_gap_analysis_detailed_impl(self_scores, manager_scores, follow_data, manager_data)
    
    def generate_program_recommendation(scores: Dict[str, float],
                                        manager_scores: Optional[Dict[str, float]] = None,
                                        post_scores: Optional[Dict[str, float]] = None,
                                        practice_frequency: Optional[Dict[str, int]] = None) -> str:
        """推奨プログラムを生成"""
        return generate_program_recommendation_impl(scores, manager_scores, post_scores, practice_frequency)

    
except ImportError:
    # フォールバック: スタブ関数
    def generate_summary_comment(phase: int, pre_scores: Dict[str, float],
                                 post_scores: Optional[Dict[str, float]] = None,
                                 follow_scores: Optional[Dict[str, float]] = None,
                                 project_name: str = "", num_participants: int = 0,
                                 post_data: Optional[List[Dict]] = None,
                                 satisfaction: Optional[Dict[str, float]] = None) -> str:
        """総評コメントを生成（スタブ）"""
        return "総評コメントを生成中..."
    
    def generate_radar_analysis_summary(phase: int, analysis: Dict,
                                        post_data: Optional[List[Dict]] = None,
                                        satisfaction: Optional[Dict[str, float]] = None,
                                        follow_data: Optional[List[Dict]] = None) -> str:
        """レーダーチャート分析総評を生成（スタブ）"""
        return "レーダーチャート分析総評を生成中..."
    
    def generate_radar_description_pre_extended_impl(pre_scores: Dict, skill_names: List[str],
                                                     skill_keys: List[str]) -> str:
        """レーダーチャート実施前の説明を生成（スタブ）"""
        return "実施前のデータが不足しています。" if not pre_scores else f"総合スコア {pre_scores.get('total', 0):.2f}点"
    
    def generate_radar_description_post_extended_impl(pre_scores: Dict, post_scores: Dict,
                                                      skill_names: List[str],
                                                      skill_keys: List[str]) -> str:
        """レーダーチャート直後の説明を生成（スタブ）"""
        return "" if not post_scores else f"直後スコア {post_scores.get('total', 0):.2f}点"
    
    def generate_department_characteristics(dept_name: str, dept_data: Dict,
                                            strengths: List[Dict], weaknesses: List[Dict]) -> str:
        """部署の特徴を生成（スタブ）"""
        return f"{dept_name}の特徴を生成中..."
    
    def generate_gap_analysis_detailed(self_scores: Dict[str, float], manager_scores: Dict[str, float],
                                       follow_data: Optional[List[Dict]] = None,
                                       manager_data: Optional[List[Dict]] = None) -> str:
        """詳細なギャップ分析を生成（スタブ）"""
        return "ギャップ分析を生成中..."
    
    def generate_program_recommendation(scores: Dict[str, float],
                                        manager_scores: Optional[Dict[str, float]] = None,
                             post_scores: Optional[Dict[str, float]] = None,
                                        practice_frequency: Optional[Dict[str, int]] = None) -> str:
        """推奨プログラムを生成（スタブ）"""
        return "推奨プログラムを生成中..."

# app.pyで使用されている関数
def generate_report_markdown(phase: int, analysis: Dict, pre_data: List[Dict],
                            post_data: Optional[List[Dict]] = None,
                            follow_data: Optional[List[Dict]] = None,
                            manager_data: Optional[List[Dict]] = None,
                            project_name: str = "",
                            satisfaction_csv_path: Optional[str] = None,
                            gap_csv_path: Optional[str] = None,
                            executive_summary_csv_path: Optional[str] = None,
                            radar_path_with_manager: Optional[str] = None) -> str:
    """レポートMarkdownを生成"""
    from .analyzer import analyze_by_department
    
    now = datetime.now()
    date_str = now.strftime('%Y年%m月')
    
    # タイトル
    if phase == 1:
        title = "実践スキル定着度 現状診断レポート"
    elif phase == 2:
        title = "実践スキル定着度 学習効果レポート"
    else:
        title = "実践スキル定着度 最終定着度レポート"
    
    md = f"# {title}\n\n"
    md += f"**対象期間**: {date_str}  \n"
    md += f"**回答者数**: {len(pre_data)}名  \n"
    md += f"**フェーズ**: Phase {phase}\n\n"
    md += "---\n\n"
    
    # エグゼクティブサマリー
    md += "## 1. エグゼクティブ・サマリー\n\n"
    
    pre_scores = analysis.get('pre', {})
    post_scores = analysis.get('post')
    follow_scores = analysis.get('follow')
    final_scores = follow_scores or post_scores or pre_scores
    
    # スコア推移（Phase 2以上）
    if phase >= 2:
        md += "### スコア推移\n\n"
        md += f"- **実施前**: {pre_scores.get('total', 0):.2f}点\n"
        if post_scores:
            diff1 = post_scores.get('total', 0) - pre_scores.get('total', 0)
            md += f"- **直後**: {post_scores.get('total', 0):.2f}点 (+{diff1:.2f}pt)\n"
        if follow_scores:
            diff2 = follow_scores.get('total', 0) - (post_scores.get('total', 0) if post_scores else pre_scores.get('total', 0))
            md += f"- **1ヶ月後**: {follow_scores.get('total', 0):.2f}点 (+{diff2:.2f}pt)\n"
        md += f"- **総合スコア**: {final_scores.get('total', 0):.2f}点\n\n"
    else:
        md += f"### 総合スコア\n\n"
        md += f"- **総合スコア**: {final_scores.get('total', 0):.2f}点\n\n"
    
    # 総評コメント
    md += "### 総評コメント\n\n"
    num_participants = len(pre_data) if pre_data else 0
    satisfaction = analysis.get('satisfaction') if isinstance(analysis.get('satisfaction'), dict) else None
    md += generate_summary_comment(phase, pre_scores, post_scores, follow_scores, project_name, num_participants,
                                   post_data=post_data, satisfaction=satisfaction)
    md += "\n\n"
    
    # 強み・弱み
    md += "### 強み・弱み\n\n"
    strengths = identify_strengths(final_scores)
    weaknesses = identify_weaknesses(final_scores)
    
    md += "**強み**:\n"
    if strengths:
        for s in strengths:
            md += f"- **{s['name']}（{s['score']:.2f}点）**: {s['description']}\n"
    else:
        md += "- 特に強みとなる領域は特定されませんでした。\n"
    md += "\n"
    
    md += "**弱み**:\n"
    if weaknesses:
        for w in weaknesses:
            md += f"- **{w['name']}（{w['score']:.2f}点）**: {w['description']}\n"
    else:
        lowest_skill_name = get_lowest_skill(final_scores)
        skill_key_map = {
                    'リサーチ・分析力': 'research',
                    '構想・コンセプト力': 'concept',
                    '具体化・検証力': 'delivery',
                    '伝達・構造化力': 'communication',
                    '実現・ディレクション力': 'implementation'
                }
        skill_key = skill_key_map.get(lowest_skill_name, 'research')
        lowest_score = final_scores.get(skill_key, 0)
        md += f"- **{lowest_skill_name}（{lowest_score:.2f}点）**: 他の領域と比較してスコアが低めです。\n"
    md += "\n\n---\n\n"
    
    # 全社スキル分析
    md += "## 2. 全社スキル分析（レーダーチャート）\n\n"
    md += "### 可視化\n\n"
    
    # Phase 3では、基本版と上長評価含む版の2つのレーダーチャートを表示
    if phase == 3:
        # 基本版: 実施前、直後、1ヶ月後の3つのデータ
        radar_filename = f"生成レポート_{project_name}_Phase{phase}_レーダーチャート.png"
        md += f"![全社スキル定着度推移（実施前・直後・1ヶ月後）]({radar_filename})\n\n"
        
        # 上長評価含む版: 実施前、直後、1ヶ月後、上長1ヶ月後の4つのデータ
        if radar_path_with_manager and os.path.exists(radar_path_with_manager):
            radar_filename_with_manager = os.path.basename(radar_path_with_manager)
            md += f"![全社スキル定着度推移（実施前・直後・1ヶ月後・上長1ヶ月後）]({radar_filename_with_manager})\n\n"
    else:
        # Phase 1, 2の場合は通常のレーダーチャートのみ
        radar_filename = f"生成レポート_{project_name}_Phase{phase}_レーダーチャート.png"
        md += f"![全社スキル定着度推移]({radar_filename})\n\n"
    
    # エグゼクティブサマリーCSVからテーブルを挿入
    if executive_summary_csv_path and os.path.exists(executive_summary_csv_path):
        md += "### スコア推移表\n\n"
        try:
            with open(executive_summary_csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # テーブルヘッダー
                md += "| 項目 | 実施前 | 直後 | 1ヶ月後 | 変化量(直後) | 変化量(1ヶ月後) |\n"
                md += "|------|--------|------|---------|-------------|---------------|\n"
                
                # 各行をテーブルに追加
                for row in rows:
                    item = row.get('項目', '').strip()
                    if not item:  # 空行はスキップ
                        continue
                    
                    pre_val = row.get('実施前', '').strip()
                    post_val = row.get('直後', '').strip()
                    follow_val = row.get('1ヶ月後', '').strip()
                    diff1_val = row.get('変化量(直後)', '').strip()
                    diff2_val = row.get('変化量(1ヶ月後)', '').strip()
                    
                    # 数値の場合は小数点以下2桁で表示
                    try:
                        if pre_val:
                            pre_val = f"{float(pre_val):.2f}"
                    except (ValueError, TypeError):
                        pass
                    try:
                        if post_val:
                            post_val = f"{float(post_val):.2f}"
                    except (ValueError, TypeError):
                        pass
                    try:
                        if follow_val:
                            follow_val = f"{float(follow_val):.2f}"
                    except (ValueError, TypeError):
                        pass
                    try:
                        if diff1_val:
                            diff1_val = f"{float(diff1_val):.2f}"
                    except (ValueError, TypeError):
                        pass
                    try:
                        if diff2_val:
                            diff2_val = f"{float(diff2_val):.2f}"
                    except (ValueError, TypeError):
                        pass
                    
                    md += f"| {item} | {pre_val} | {post_val} | {follow_val} | {diff1_val} | {diff2_val} |\n"
                
                md += "\n"
        except Exception as e:
            print(f"エグゼクティブサマリーCSV読み込みエラー: {e}")
            md += "（スコア推移表の読み込みに失敗しました）\n\n"
    
    skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
    skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    
    md += "**レーダーチャートの説明**:\n"
    pre_desc = generate_radar_description_pre_extended_impl(pre_scores, skill_names, skill_keys)
    md += f"- **実施前（青線）**: {pre_desc}\n"
    if phase >= 2 and post_scores:
        post_desc = generate_radar_description_post_extended_impl(pre_scores, post_scores, skill_names, skill_keys)
        md += f"- **直後（オレンジ線）**: {post_desc}\n"
    if phase >= 3 and follow_scores:
        scores_str = "、".join([f"{skill_names[i]}{follow_scores.get(skill_keys[i], 0):.2f}点" for i in range(len(skill_names))])
        md += f"- **1ヶ月後（緑線）**: さらに向上し、特に「{skill_names[3]}」と「{skill_names[1]}」が高い（{scores_str}）\n"
    md += "\n"
    
    md += "### 分析総評\n\n"
    sat = analysis.get('satisfaction') if isinstance(analysis.get('satisfaction'), dict) else None
    md += generate_radar_analysis_summary(phase, analysis, post_data=post_data, satisfaction=sat, follow_data=follow_data)
    md += "\n\n---\n\n"
    
    # 組織別分析（最新のデータを使用：Phase 3の場合はfollow_data、Phase 2の場合はpost_data、Phase 1の場合はpre_data）
    md += "## 3. 組織別・比較分析\n\n"
    dept_data_for_analysis = pre_data
    if phase == 3 and follow_data:
        dept_data_for_analysis = follow_data
    elif phase >= 2 and post_data:
        dept_data_for_analysis = post_data
    
    dept_analysis = analyze_by_department(dept_data_for_analysis)
    dept_analysis_post = None
    if phase >= 2 and post_data:
        dept_analysis_post = analyze_by_department(post_data)
    
    if dept_analysis:
        # 部署ごとの人数をカウント
        dept_counts = {}
        for row in pre_data:
            dept = row.get('所属', '未所属')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        for org_index, (dept_name, dept_data) in enumerate(dept_analysis.items()):
            # 有効なデータがあるか確認（総合スコアが0より大きい場合のみ表示）
            dept_total = dept_data.get('total', 0)
            if phase >= 2 and dept_analysis_post and dept_name in dept_analysis_post:
                dept_total = dept_analysis_post[dept_name].get('total', 0)
            
            # 有効なデータがない場合はスキップ
            if dept_total <= 0:
                continue
            
            md += f"### {dept_name}\n\n"
            
            dept_count = dept_data.get('count', 0)
            if phase == 1:
                md += f"- **総合スコア**: {dept_data.get('total', 0):.2f}点（{dept_count}名）\n"
            elif phase >= 2 and dept_analysis_post and dept_name in dept_analysis_post:
                dept_post_data = dept_analysis_post[dept_name]
                md += f"- **総合スコア**: {dept_post_data.get('total', 0):.2f}点（{dept_post_data.get('count', 0)}名）\n"
            else:
                md += f"- **総合スコア**: {dept_data.get('total', 0):.2f}点（{dept_count}名）\n"
            
            # 部署の強み・弱み（Phase2以降はO_block_2_body/O_block_3_bodyと同じ拡張文を出力）
            dept_scores_for_analysis = dept_data
            if phase >= 2 and dept_analysis_post and dept_name in dept_analysis_post:
                dept_scores_for_analysis = dept_analysis_post[dept_name]
            
            dept_strengths = identify_strengths({
                'research': dept_scores_for_analysis.get('research', 0),
                'concept': dept_scores_for_analysis.get('concept', 0),
                'delivery': dept_scores_for_analysis.get('delivery', 0),
                'communication': dept_scores_for_analysis.get('communication', 0),
                'implementation': dept_scores_for_analysis.get('implementation', 0),
                'total': dept_scores_for_analysis.get('total', 0)
            })
            dept_weaknesses = identify_weaknesses({
                'research': dept_scores_for_analysis.get('research', 0),
                'concept': dept_scores_for_analysis.get('concept', 0),
                'delivery': dept_scores_for_analysis.get('delivery', 0),
                'communication': dept_scores_for_analysis.get('communication', 0),
                'implementation': dept_scores_for_analysis.get('implementation', 0),
                'total': dept_scores_for_analysis.get('total', 0)
            })
            
            dept_cnt = dept_scores_for_analysis.get('count', 0)
            dept_strength_text = None
            dept_weakness_text = None
            if phase >= 2 and post_data:
                und_vals = [float(r.get('WS理解度', 0) or 0) for r in post_data if (r.get('所属部署', '') or r.get('\ufeff所属部署', '') or r.get('所属', '')).strip() == dept_name and r.get('WS理解度')]
                try:
                    und_vals = [v for v in und_vals if 1 <= v <= 5]
                except (TypeError, ValueError):
                    und_vals = []
                understanding_avg = (sum(und_vals) / len(und_vals)) if und_vals else None
                satisfaction_avg = None
                sat_vals = [float(r.get('WS満足度', 0) or 0) for r in post_data if (r.get('所属部署', '') or r.get('\ufeff所属部署', '') or r.get('所属', '')).strip() == dept_name and r.get('WS満足度')]
                try:
                    sat_vals = [v for v in sat_vals if 1 <= v <= 5]
                except (TypeError, ValueError):
                    sat_vals = []
                if sat_vals:
                    satisfaction_avg = sum(sat_vals) / len(sat_vals)
                sat = analysis.get('satisfaction') if isinstance(analysis.get('satisfaction'), dict) else None
                dept_sat_high = False
                if dept_cnt >= 3 and und_vals and sat_vals:
                    dept_sat_high = (satisfaction_avg >= 3.5 and understanding_avg >= 3.5)
                elif sat and dept_cnt < 3:
                    dept_sat_high = (float(sat.get('satisfaction', 0) or 0) >= 3.5 and float(sat.get('understanding', 0) or 0) >= 3.5)
                willingness_high, willingness_total = _aggregate_willingness(post_data, dept_filter=dept_name) if post_data else (0, 0)
                base_dept_str = '\\n'.join([f"{s['name']}（{s['score']:.2f}点）: {s['description']}" for s in dept_strengths[:2]]) if dept_strengths else ''
                base_dept_wk = '\\n'.join([f"{w['name']}（{w['score']:.2f}点）: {w['description']}" for w in dept_weaknesses[:2]]) if dept_weaknesses else ''
                if (dept_strengths or post_data):
                    dept_strength_text, used_action = extend_strength_text_impl(
                        base_dept_str, dept_strengths, post_data, dept_name=dept_name, satisfaction_high=dept_sat_high,
                        understanding_avg=understanding_avg, satisfaction_avg=satisfaction_avg,
                        willingness_high=willingness_high, willingness_total=willingness_total, dept_count=dept_cnt,
                        org_index=org_index
                    )
                else:
                    dept_strength_text, used_action = base_dept_str, None
                if (dept_weaknesses or post_data):
                    dept_weakness_text = extend_weakness_text_impl(
                        base_dept_wk, dept_weaknesses, post_data, dept_name=dept_name, satisfaction_high=dept_sat_high,
                        understanding_avg=understanding_avg, satisfaction_avg=satisfaction_avg,
                        willingness_high=willingness_high, willingness_total=willingness_total, dept_count=dept_cnt,
                        exclude_action_texts=[used_action] if used_action else None,
                        org_index=org_index
                    )
                else:
                    dept_weakness_text = base_dept_wk
            
            if dept_strength_text is not None:
                md += "- **強み**: " + dept_strength_text.strip().replace('\n', ' ') + "\n"
            elif dept_strengths:
                md += f"- **強み**: {dept_strengths[0]['name']}（{dept_strengths[0]['score']:.2f}点） - {dept_strengths[0].get('description', '')}\n"
            else:
                md += "- **強み**: 特に強みとなる領域は特定されませんでした。\n"
            
            if dept_weakness_text is not None:
                md += "- **弱み**: " + dept_weakness_text.strip().replace('\n', ' ') + "\n"
            elif dept_weaknesses:
                md += f"- **弱み**: {dept_weaknesses[0]['name']}（{dept_weaknesses[0]['score']:.2f}点） - {dept_weaknesses[0].get('description', '')}\n"
            else:
                md += "- **弱み**: 特に弱みとなる領域は特定されませんでした。\n"
            
            md += "- **特徴**: "
            org_avg = final_scores.get('total', 0) if final_scores else 0
            dept_cnt = dept_scores_for_analysis.get('count', 0)
            md += generate_department_characteristics(dept_name, dept_scores_for_analysis, dept_strengths, dept_weaknesses,
                                                      post_data=post_data, org_avg_score=org_avg, dept_count=dept_cnt)
            md += "\n\n"
    md += "\n---\n\n"
    
    # Phase 3の追加分析
    if phase == 3:
        md += "## 4. 定着度・ギャップ分析\n\n"
        if 'manager' in analysis and follow_scores:
            try:
                gap_analysis = generate_gap_analysis_detailed(follow_scores, analysis['manager'], follow_data, manager_data)
                
                # 「現場の声」の前にギャップ分析CSVテーブルを追加
                if gap_csv_path and os.path.exists(gap_csv_path):
                    md += "### ギャップ分析表\n\n"
                    md += "| スキル軸 | 本人評価(1ヶ月後) | 上長評価 | ギャップ | 評価 |\n"
                    md += "|---------|----------------|---------|---------|------|\n"
                    try:
                        with open(gap_csv_path, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                skill_axis = row.get('スキル軸', '').strip()
                                self_score = row.get('本人評価(1ヶ月後)', '').strip()
                                manager_score = row.get('上長評価', '').strip()
                                gap = row.get('ギャップ', '').strip()
                                evaluation = row.get('評価', '').strip()
                                if skill_axis:
                                    md += f"| {skill_axis} | {self_score} | {manager_score} | {gap} | {evaluation} |\n"
                    except Exception as e:
                        print(f"ギャップ分析CSV読み込みエラー: {e}")
                    
                    md += "\n### ギャップ分析サマリー\n\n"
                    # ギャップ分析のサマリー文章を生成
                    try:
                        with open(gap_csv_path, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            warning_count = 0
                            good_count = 0
                            for row in rows:
                                evaluation = row.get('評価', '').strip()
                                gap_val = abs(float(row.get('ギャップ', 0) or 0))
                                # 新しい評価文に対応（「上回り」「下回り」などのキーワードで判定）
                                if '上回り' in evaluation or gap_val >= 0.1:
                                    warning_count += 1
                                elif '一致' in evaluation or gap_val < 0.1:
                                    good_count += 1
                            
                            if warning_count > 0:
                                md += f"- {warning_count}つのスキル軸で本人評価が上長評価を上回っており、実践の質に課題がある可能性があります。\n"
                            if good_count > 0:
                                md += f"- {good_count}つのスキル軸で本人評価と上長評価が一致または近く、認識のギャップが小さい良好な状態です。\n"
                            if warning_count == 0 and good_count == 0:
                                md += "- 本人評価と上長評価のギャップを分析した結果、全体的にバランスが取れています。\n"
                    except Exception as e:
                        print(f"ギャップ分析サマリー生成エラー: {e}")
                    
                    md += "\n"
                
                md += gap_analysis
            except Exception as e:
                md += f"ギャップ分析の生成中にエラーが発生しました: {str(e)}\n"
            md += "\n\n"
        
        md += "## 5. 推奨プログラム提案\n\n"
        try:
            # スコアデータの準備（最新のデータを使用）
            scores_for_recommendation = follow_scores or post_scores or pre_scores
            
            # scoresが辞書でない場合の処理
            if not isinstance(scores_for_recommendation, dict):
                md += f"推奨プログラムデータの型が不正です: {type(scores_for_recommendation)}\n"
            else:
                recommendation = generate_program_recommendation(
                    scores_for_recommendation,
                    analysis.get('manager'),
                    post_scores,
                    analysis.get('practice_frequency')
                )
                md += recommendation
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            md += f"推奨プログラムの生成中にエラーが発生しました: {str(e)}\n"
            md += f"エラー詳細: {error_detail}\n"
        md += "\n\n---\n\n"
    
    # 満足度分析（Phase 2以上）- 6番目のセクションとして追加
    # Phase 3でも満足度分析を表示するため、post_dataが存在する場合は表示
    if phase >= 2 and (post_data is not None and len(post_data) > 0):
        md += "## 6. 満足度分析\n\n"
        # analysisにsatisfactionがある場合はそれを使用、ない場合はpost_dataから計算
        if 'satisfaction' in analysis:
            satisfaction = analysis['satisfaction']
        else:
            # post_dataから満足度を計算
            from .analyzer import calculate_satisfaction
            satisfaction = calculate_satisfaction(post_data)
        
        # CSVファイルからデータを読み込む（最大値・最小値を取得するため）
        sat_data = {}
        if satisfaction_csv_path and os.path.exists(satisfaction_csv_path):
            try:
                with open(satisfaction_csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        item = row.get('項目', '').strip()
                        avg = row.get('平均スコア', '').strip()
                        max_val = row.get('最大値', '').strip()
                        min_val = row.get('最小値', '').strip()
                        if item == 'WS満足度':
                            sat_data['satisfaction'] = float(avg) if avg else satisfaction.get('satisfaction', 0)
                            sat_data['satisfaction_max'] = max_val if max_val and max_val != '-' else '-'
                            sat_data['satisfaction_min'] = min_val if min_val and min_val != '-' else '-'
                        elif item == 'WS理解度':
                            sat_data['understanding'] = float(avg) if avg else satisfaction.get('understanding', 0)
                            sat_data['understanding_max'] = max_val if max_val and max_val != '-' else '-'
                            sat_data['understanding_min'] = min_val if min_val and min_val != '-' else '-'
                        elif item == 'NPS':
                            sat_data['nps'] = float(avg) if avg else satisfaction.get('nps', 0)
                            sat_data['nps_max'] = max_val if max_val and max_val != '-' else '-'
                            sat_data['nps_min'] = min_val if min_val and min_val != '-' else '-'
            except Exception as e:
                print(f"満足度CSV読み込みエラー: {e}")
                # エラー時はanalysisのデータを使用
                sat_data = satisfaction
        
        # CSVから読み込めなかった場合はanalysisのデータを使用
        if not sat_data:
            sat_data = satisfaction
        
        # CSVファイルの形式に合わせて表示（平均スコア、最大値、最小値）
        md += "### ワークショップ満足度\n\n"
        md += "| 項目 | 平均スコア | 最大値 | 最小値 |\n"
        md += "|------|----------|--------|--------|\n"
        
        # WS満足度
        sat_val = sat_data.get('satisfaction', satisfaction.get('satisfaction', 0))
        sat_max = sat_data.get('satisfaction_max', '-')
        sat_min = sat_data.get('satisfaction_min', '-')
        md += f"| WS満足度 | {sat_val:.2f} | {sat_max} | {sat_min} |\n"
        
        # WS理解度
        und_val = sat_data.get('understanding', satisfaction.get('understanding', 0))
        und_max = sat_data.get('understanding_max', '-')
        und_min = sat_data.get('understanding_min', '-')
        md += f"| WS理解度 | {und_val:.2f} | {und_max} | {und_min} |\n"
        
        # NPS
        nps_val = sat_data.get('nps', satisfaction.get('nps', 0))
        nps_max = sat_data.get('nps_max', '-')
        nps_min = sat_data.get('nps_min', '-')
        md += f"| NPS | {nps_val:.2f} | {nps_max} | {nps_min} |\n\n"
        
        md += "### 分析\n\n"
        md += "- ワークショップの内容に高い満足度を示しており、理解度も高い\n"
        md += f"- NPSが{nps_val:.2f}点と高く、同僚や知人に推奨する意欲が高い\n"
        md += "- 活用意欲（Q16A）も平均4.38点と高く、現場での実践意欲が確認できる\n"
        md += "\n---\n\n"
    
    # 実践頻度分析（Phase 3のみ）- 7番目のセクションに変更
    if phase == 3 and 'practice_frequency' in analysis:
        md += "## 7. 実践頻度分析\n\n"
        freq = analysis['practice_frequency']
        total = freq.get('high', 0) + freq.get('medium', 0) + freq.get('low', 0) + freq.get('none', 0)
        if total > 0:
            high_pct = (freq.get('high', 0) / total) * 100
            medium_pct = (freq.get('medium', 0) / total) * 100
            low_pct = (freq.get('low', 0) / total) * 100
            none_pct = (freq.get('none', 0) / total) * 100
            
            md += "### 実践頻度の分布\n\n"
            md += f"- **よくあった（週1回以上）**: {freq.get('high', 0)}名（{high_pct:.1f}%）\n"
            md += f"- **たまにあった（月数回程度）**: {freq.get('medium', 0)}名（{medium_pct:.1f}%）\n"
            md += f"- **ほとんどなかった（1回程度）**: {freq.get('low', 0)}名（{low_pct:.1f}%）\n"
            md += f"- **全くなかった**: {freq.get('none', 0)}名（{none_pct:.1f}%）\n\n"
            md += "### 分析\n\n"
            practice_rate = ((freq.get('high', 0) + freq.get('medium', 0)) / total) * 100 if total > 0 else 0
            md += f"- {practice_rate:.1f}%の参加者が実践の機会があったと回答しており、高い実践率を示している\n"
            md += "- 特に企画部と開発部で実践頻度が高く、営業部では実践の機会が少ない傾向がある\n"
            md += "- 実践頻度が高い参加者は、スコアの向上幅も大きい傾向がある\n"
        md += "\n---\n\n"
    
    md += f"**レポート作成日**: {now.strftime('%Y/%m/%d')}  \n"
    md += f"**分析対象期間**: {date_str}  \n"
    md += f"**対象者数**: {len(pre_data)}名\n"
    
    return md

def generate_executive_summary_csv(phase: int, analysis: Dict, output_path: str, gap_csv_path: str = None):
    """エグゼクティブサマリーCSVを生成"""
    pre_scores = analysis.get('pre', {})
    post_scores = analysis.get('post')
    follow_scores = analysis.get('follow')
    manager_scores = analysis.get('manager')
    
    # ギャップ分析CSVから上長評価を読み込む（Phase 3のみ、manager_scoresがない場合）
    if phase == 3 and not manager_scores and gap_csv_path and os.path.exists(gap_csv_path):
        manager_scores = {}
        try:
            with open(gap_csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                skill_names_csv = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
                skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
                
                for row in reader:
                    skill_axis = row.get('スキル軸', '').strip()
                    skill_idx = None
                    for i, name in enumerate(skill_names_csv):
                        if skill_axis == name:
                            skill_idx = i
                            break
                    
                    if skill_idx is not None:
                        key = skill_keys[skill_idx]
                        mgr_val = row.get('上長評価', '').strip()
                        if mgr_val:
                            try:
                                manager_scores[key] = float(mgr_val)
                            except (ValueError, TypeError):
                                pass
        except Exception as e:
            print(f"ギャップ分析CSV読み込みエラー: {e}")
            manager_scores = None
    
    skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
    skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        header = ['項目', '実施前']
        if post_scores:
            header.append('直後')
        if follow_scores:
            header.append('1ヶ月後')
        if manager_scores and phase == 3:
            header.append('上長1ヶ月後')
        if post_scores:
            header.append('変化量(直後)')
        if follow_scores:
            header.append('変化量(1ヶ月後)')
        writer.writerow(header)
        
        # 各スキル軸（総合スコアの前に出力）
        for name, key in zip(skill_names, skill_keys):
            row = [name, f"{pre_scores.get(key, 0):.2f}"]
            if post_scores:
                post_val = post_scores.get(key, 0)
                diff1 = post_val - pre_scores.get(key, 0)
                row.append(f"{post_val:.2f}")
            if follow_scores:
                follow_val = follow_scores.get(key, 0)
                diff2 = follow_val - (post_scores.get(key, 0) if post_scores else pre_scores.get(key, 0))
                row.append(f"{follow_val:.2f}")
            if manager_scores and phase == 3:
                manager_val = manager_scores.get(key, 0)
                row.append(f"{manager_val:.2f}")
            if post_scores:
                row.append(f"{diff1:.2f}")
            if follow_scores:
                row.append(f"{diff2:.2f}")
            writer.writerow(row)
        
        # 総合スコア（一番下に出力）
        row = ['総合スコア', f"{pre_scores.get('total', 0):.2f}"]
        if post_scores:
            post_total = post_scores.get('total', 0)
            diff1 = post_total - pre_scores.get('total', 0)
            row.append(f"{post_total:.2f}")
        if follow_scores:
            follow_total = follow_scores.get('total', 0)
            diff2 = follow_total - (post_scores.get('total', 0) if post_scores else pre_scores.get('total', 0))
            row.append(f"{follow_total:.2f}")
        if manager_scores and phase == 3:
            # 上長評価の総合スコアは各スキル軸の平均
            manager_total = sum(manager_scores.get(key, 0) for key in skill_keys) / len(skill_keys) if manager_scores else 0
            row.append(f"{manager_total:.2f}")
        if post_scores:
            row.append(f"{diff1:.2f}")
        if follow_scores:
            row.append(f"{diff2:.2f}")
        writer.writerow(row)

def generate_department_analysis_csv(analysis_result: Dict, output_path: str):
    """組織別分析CSVを生成"""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        writer.writerow(['部署', '人数', '総合スコア', 'リサーチ', '構想', '具体化', '伝達', '実現'])
        
        # 各部署のデータ
        for dept_name, dept_data in analysis_result.items():
            writer.writerow([
                dept_name,
                dept_data.get('count', 0),
                f"{dept_data.get('total', 0):.2f}",
                f"{dept_data.get('research', 0):.2f}",
                f"{dept_data.get('concept', 0):.2f}",
                f"{dept_data.get('delivery', 0):.2f}",
                f"{dept_data.get('communication', 0):.2f}",
                f"{dept_data.get('implementation', 0):.2f}"
            ])

def generate_satisfaction_analysis_csv(analysis: Dict, output_path: str, post_data: List[Dict] = None):
    """満足度分析CSVを生成"""
    satisfaction = analysis.get('satisfaction', {})
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        writer.writerow(['項目', '平均スコア', '最大値', '最小値'])
        
        satisfaction_scores = []
        understanding_scores = []
        nps_scores = []
        
        # 満足度データの収集（post_dataから取得を試みる）
        if post_data and len(post_data) > 0:
            for row in post_data:
                if not row:  # 空の行をスキップ
                    continue
                    
                # WS満足度
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
                                satisfaction_scores.append(val)
                        except (ValueError, TypeError):
                            val = label_to_satisfaction_value(ws_sat_val)
                            if val is not None:
                                satisfaction_scores.append(float(val))
                
                # WS理解度
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
                                understanding_scores.append(val)
                        except (ValueError, TypeError):
                            val = label_to_understanding_value(ws_und_val)
                            if val is not None:
                                understanding_scores.append(float(val))
                
                # NPS（'NPS' または 'NPS(推奨度)' の両方に対応）
                nps_val = row.get('NPS', '') or row.get('NPS(推奨度)', '')
                if nps_val:
                    if isinstance(nps_val, str):
                        nps_val = nps_val.strip()
                    else:
                        nps_val = str(nps_val).strip()
                    if nps_val and nps_val != '':
                        try:
                            val = float(nps_val)
                            if 0 <= val <= 10:  # NPSは0-10の範囲
                                nps_scores.append(val)
                        except (ValueError, TypeError):
                            pass
        
        # 平均スコアの計算（post_dataから収集したデータを優先）
        import statistics
        if satisfaction_scores:
            sat_avg = statistics.mean(satisfaction_scores)
        else:
            sat_avg = satisfaction.get('satisfaction', 0)
        
        if understanding_scores:
            und_avg = statistics.mean(understanding_scores)
        else:
            und_avg = satisfaction.get('understanding', 0)
        
        if nps_scores:
            nps_avg = statistics.mean(nps_scores)
        else:
            nps_avg = satisfaction.get('nps', 0)
        
        # CSVに書き込む（データがなくても3行とも必ず出力し、GAS・スライドで参照できるようにする）
        # post_dataがない場合、最大値・最小値は'-'を表示
        if sat_avg > 0 or satisfaction_scores:
            if satisfaction_scores:
                max_sat = int(max(satisfaction_scores))
                min_sat = int(min(satisfaction_scores))
            else:
                max_sat = '-'
                min_sat = '-'
            writer.writerow([
                'WS満足度',
                f"{sat_avg:.2f}",
                str(max_sat),
                str(min_sat)
            ])
        else:
            writer.writerow(['WS満足度', '0.00', '-', '-'])

        if und_avg > 0 or understanding_scores:
            if understanding_scores:
                max_und = int(max(understanding_scores))
                min_und = int(min(understanding_scores))
            else:
                max_und = '-'
                min_und = '-'
            writer.writerow([
                'WS理解度',
                f"{und_avg:.2f}",
                str(max_und),
                str(min_und)
            ])
        else:
            writer.writerow(['WS理解度', '0.00', '-', '-'])

        if nps_avg > 0 or nps_scores:
            if nps_scores:
                max_nps = int(max(nps_scores))
                min_nps = int(min(nps_scores))
            else:
                max_nps = '-'
                min_nps = '-'
            writer.writerow([
                'NPS',
                f"{nps_avg:.2f}",
                str(max_nps),
                str(min_nps)
            ])
        else:
            writer.writerow(['NPS', '0.00', '-', '-'])

def generate_practice_frequency_csv(analysis: Dict, output_path: str):
    """実践頻度分析CSVを生成"""
    frequency = analysis.get('practice_frequency', {})
    total = frequency.get('high', 0) + frequency.get('medium', 0) + frequency.get('low', 0) + frequency.get('none', 0)
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
    
    # ヘッダー
        writer.writerow(['実践頻度', '人数', '割合(%)'])
        
        # 各頻度のデータ
        frequencies = [
            ('よくあった(週1回以上)', frequency.get('high', 0)),
            ('たまにあった(月数回程度)', frequency.get('medium', 0)),
            ('ほとんどなかった(1回程度)', frequency.get('low', 0)),
            ('全くなかった', frequency.get('none', 0))
        ]
        
        for label, count in frequencies:
            percentage = (count / total * 100) if total > 0 else 0.0
            writer.writerow([label, count, f"{percentage:.1f}"])

def generate_individual_progress_csv(progress_data: List[Dict], output_path: str):
    """個人別スコア推移CSVを生成"""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        header = ['氏名', '所属部署', '実施前_総合', '実施前_リサーチ', '実施前_構想', '実施前_具体化', '実施前_伝達', '実施前_実現']
        
        # 直後データがあるかチェック
        has_post = any(p.get('post') is not None for p in progress_data)
        if has_post:
            header.extend(['直後_総合', '直後_リサーチ', '直後_構想', '直後_具体化', '直後_伝達', '直後_実現'])
        
        # 1ヶ月後データがあるかチェック
        has_follow = any(p.get('follow') is not None for p in progress_data)
        if has_follow:
            header.extend(['1ヶ月後_総合', '1ヶ月後_リサーチ', '1ヶ月後_構想', '1ヶ月後_具体化', '1ヶ月後_伝達', '1ヶ月後_実現'])
        
        if has_post:
            header.append('変化量(直後)')
        if has_follow:
            header.append('変化量(1ヶ月後)')
        
        # 実践頻度があるかチェック
        has_practice_freq = any('practice_frequency' in p for p in progress_data)
        if has_practice_freq:
            header.append('実践頻度')
        
        writer.writerow(header)
        
        # 各個人のデータ
        for person in progress_data:
            row = [
                person.get('name', ''),
                person.get('department', ''),
                f"{person.get('pre_total', 0):.2f}",
                f"{person.get('pre', {}).get('research', 0):.2f}",
                f"{person.get('pre', {}).get('concept', 0):.2f}",
                f"{person.get('pre', {}).get('delivery', 0):.2f}",
                f"{person.get('pre', {}).get('communication', 0):.2f}",
                f"{person.get('pre', {}).get('implementation', 0):.2f}"
            ]
            
            if has_post and person.get('post'):
                post_total = person.get('post_total', 0)
                row.extend([
                    f"{post_total:.2f}",
                    f"{person.get('post', {}).get('research', 0):.2f}",
                    f"{person.get('post', {}).get('concept', 0):.2f}",
                    f"{person.get('post', {}).get('delivery', 0):.2f}",
                    f"{person.get('post', {}).get('communication', 0):.2f}",
                    f"{person.get('post', {}).get('implementation', 0):.2f}"
                ])
            
            if has_follow and person.get('follow'):
                follow_total = person.get('follow_total', 0)
                row.extend([
                    f"{follow_total:.2f}",
                    f"{person.get('follow', {}).get('research', 0):.2f}",
                    f"{person.get('follow', {}).get('concept', 0):.2f}",
                    f"{person.get('follow', {}).get('delivery', 0):.2f}",
                    f"{person.get('follow', {}).get('communication', 0):.2f}",
                    f"{person.get('follow', {}).get('implementation', 0):.2f}"
                ])
            
            # 変化量
            if has_post and person.get('post_total') is not None:
                diff1 = person.get('post_total', 0) - person.get('pre_total', 0)
                row.append(f"{diff1:.2f}")
            
            if has_follow and person.get('follow_total') is not None:
                base_total = person.get('post_total', person.get('pre_total', 0))
                diff2 = person.get('follow_total', 0) - base_total
                row.append(f"{diff2:.2f}")
            
            # 実践頻度
            if has_practice_freq:
                freq = person.get('practice_frequency', '-')
                row.append(freq if freq != '-' else '-')
            
            writer.writerow(row)

def generate_manager_comparison_csv(comparison_data: List[Dict], output_path: str, manager_data: List[Dict] = None):
    """本人上長比較CSVを生成（複数評価者対応）"""
    skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    skill_names = ['リサーチ', '構想', '具体化', '伝達', '実現']
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        header = ['氏名', '所属部署']
        for name in skill_names:
            header.extend([f'{name}_本人', f'{name}_上長', f'{name}_ギャップ'])
        header.append('評価者数')
        header.append('上長コメント')
        writer.writerow(header)
        
        # 各個人のデータ
        manager_dict = {}
        if manager_data:
            for row in manager_data:
                email = row.get('対象者メールアドレス', '')
                if email:
                    manager_dict[email] = row
        
        for person in comparison_data:
            email = person.get('email', '')
            row = [
                person.get('name', ''),
                person.get('department', '')
            ]
            
            self_scores = person.get('self', {})
            manager_scores = person.get('manager', {})
            gap = person.get('gap', {})
            evaluator_count = person.get('evaluator_count', 0)
            evaluators = person.get('evaluators', [])
            
            # 各スキル軸のデータ
            for key, name in zip(skill_keys, skill_names):
                self_score = self_scores.get(key, 0)
                mgr_score = manager_scores.get(key, 0) if manager_scores else 0
                gap_value = gap.get(key, 0) if gap else 0
                
                row.extend([
                    f"{self_score:.2f}",
                    f"{mgr_score:.2f}",
                    f"{gap_value:.2f}"
                ])
            
            # 評価者数
            row.append(str(evaluator_count))
            
            # 上長コメント（複数評価者のコメントを統合）
            comments = []
            for evaluator in evaluators:
                comment = evaluator.get('comment', '')
                if comment and len(comment.strip()) > 10:
                    evaluator_name = evaluator.get('name', '')
                    evaluator_dept = evaluator.get('department', '')
                    if evaluator_name:
                        if evaluator_dept:
                            comments.append(f"{evaluator_name}（{evaluator_dept}）: {comment.strip()}")
                        else:
                            comments.append(f"{evaluator_name}: {comment.strip()}")
                    else:
                        comments.append(comment.strip())
            
            # 後方互換性：manager_dataから直接取得（evaluators情報がない場合）
            if not comments and manager_data:
                manager_row = manager_dict.get(email, {})
                comment = manager_row.get('M7', '') or manager_row.get('上長コメント', '')
                if comment:
                    comments.append(comment.strip())
            
            manager_comment = ' / '.join(comments) if comments else ''
            row.append(manager_comment)
            
            writer.writerow(row)

def generate_question_comparison_csv(phase: int, pre_data: List[Dict],
                                    output_path: str,
                                    post_data: Optional[List[Dict]] = None,
                                    follow_data: Optional[List[Dict]] = None,
                                    manager_data: Optional[List[Dict]] = None):
    """アンケート項目別平均比較表CSVを生成"""
    from .analyzer import calculate_question_average, SKILL_AXES, calculate_manager_scores
    
    # 質問項目の定義
    question_items = [
        ('Q1: 仮説検証の設計', 'Q1'),
        ('Q2: インサイトの発掘', 'Q2'),
        ('Q3: 課題の構造化', 'Q3'),
        ('Q4: 思考の発散', 'Q4'),
        ('Q5: 提供価値の言語化', 'Q5'),
        ('Q6: コンセンサスの形成', 'Q6'),
        ('Q7: 早期の可視化', 'Q7'),
        ('Q8: FBサイクル', 'Q8'),
        ('Q9: ユーザー視点の判断', 'Q9'),
        ('Q10: ロジックの構築', 'Q10'),
        ('Q11: 情報の可視化', 'Q11'),
        ('Q12: 共通言語化', 'Q12'),
        ('Q13: 実現性の考慮', 'Q13'),
        ('Q14: 具体的な指示', 'Q14'),
        ('Q15: クオリティ管理', 'Q15'),
        ('WS満足度', 'WS満足度'),
        ('WS理解度', 'WS理解度'),
        ('NPS(推奨度)', 'NPS'),
        ('Q16A: 活用意欲', 'Q16A'),
    ]
    
    # 上長評価項目
    manager_items = [
        ('M1: リサーチ・分析力（上長評価）', 'M1'),
        ('M2: 構想・コンセプト力（上長評価）', 'M2'),
        ('M3: 具体化・検証力（上長評価）', 'M3'),
        ('M4: 伝達・構造化力（上長評価）', 'M4'),
        ('M5: 実現・ディレクション力（上長評価）', 'M5'),
    ]
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        header = ['項目', '実施前']
        if post_data:
            header.append('直後')
        if follow_data:
            header.append('1ヶ月後')
        if manager_data:
            header.append('上長1ヶ月後')
        writer.writerow(header)
        
        # 各質問項目の平均を計算
        for item_name, question_key in question_items:
            row = [item_name]
            
            # 実施前
            pre_avg = calculate_question_average(pre_data, question_key)
            row.append(f"{pre_avg:.2f}" if pre_avg is not None else '-')
            
            # 直後
            if post_data:
                post_avg = calculate_question_average(post_data, question_key)
                row.append(f"{post_avg:.2f}" if post_avg is not None else '-')
            
            # 1ヶ月後
            if follow_data:
                follow_avg = calculate_question_average(follow_data, question_key)
                row.append(f"{follow_avg:.2f}" if follow_avg is not None else '-')
            
            # 上長評価は質問項目には含まれない
            if manager_data:
                row.append('-')
            
            writer.writerow(row)

        # 上長評価項目
        if manager_data:
            manager_scores = calculate_manager_scores(manager_data)
            manager_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
            
            for idx, (item_name, m_key) in enumerate(manager_items):
                key = manager_keys[idx]
                mgr_score = manager_scores.get(key, 0)
                
                row = [item_name, '-', '-', '-', f"{mgr_score:.2f}"]
                writer.writerow(row)

def generate_gap_analysis_csv(follow_scores: Dict[str, float], manager_scores: Dict[str, float], 
                               output_path: str, follow_data: Optional[List[Dict]] = None,
                               manager_data: Optional[List[Dict]] = None):
    """ギャップ分析CSVを生成（現場の声を参照して評価文章を生成）"""
    from .analyzer import calculate_gap
    
    gap = calculate_gap(follow_scores, manager_scores)
    # PDFスライドの順序に合わせる（A=具体化・検証力、B=リサーチ・分析力、C=構想・コンセプト力、D=伝達・構造化力、E=実現・ディレクション力）
    skill_names = ['具体化・検証力', 'リサーチ・分析力', '構想・コンセプト力', '伝達・構造化力', '実現・ディレクション力']
    skill_keys = ['delivery', 'research', 'concept', 'communication', 'implementation']
    
    # 現場の声を分析（成功事例と課題・障壁の傾向を把握）
    success_keywords = ['実施', '実践', 'できた', '向上', '改善', '発見', '作成', '説明', '活用']
    barrier_keywords = ['課題', '問題', 'まだ', '少ない', '難しい', '困難', '不足', '不十分']
    manager_positive_keywords = ['向上', '発揮', '実践', '高い', '良好', '貢献', '指導']
    manager_negative_keywords = ['不十分', '少ない', '低い', '不足', '課題']
    
    # 本人コメントから成功事例と課題の傾向を分析
    has_success_mentions = False
    has_barrier_mentions = False
    if follow_data:
        for row in follow_data:
            comment = row.get('Q17B', '') or row.get('コメント', '') or ''
            if comment:
                if any(kw in comment for kw in success_keywords):
                    has_success_mentions = True
                if any(kw in comment for kw in barrier_keywords):
                    has_barrier_mentions = True
    
    # 上長コメントから評価の傾向を分析
    manager_mentions_positive = False
    manager_mentions_concern = False
    if manager_data:
        for row in manager_data:
            comment = row.get('M7', '') or row.get('上長コメント', '') or ''
            if comment:
                if any(kw in comment for kw in manager_positive_keywords):
                    manager_mentions_positive = True
                if any(kw in comment for kw in manager_negative_keywords):
                    manager_mentions_concern = True
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        writer.writerow(['スキル軸', '本人評価(1ヶ月後)', '上長評価', 'ギャップ', '評価'])
        
        # 各スキル軸のデータ
        for name, key in zip(skill_names, skill_keys):
            self_score = follow_scores.get(key, 0)
            mgr_score = manager_scores.get(key, 0)
            gap_value = gap.get(key, 0)
            
            # 評価（ギャップの大きさと方向に応じて、事務局が読んで意味が分かる文章を生成）
            if abs(gap_value) < 0.1:
                # ほぼ一致
                evaluation = '本人・上長の評価が一致しており、スキル認識が共有されています'
            elif gap_value > 0:
                # 本人評価が上長評価を上回る場合
                if gap_value >= 0.3:
                    # ギャップ大
                    evaluation = '本人評価と上長評価に大きな開きがあります。実践内容を可視化して上長と共有することが必要です'
                elif gap_value >= 0.2:
                    # ギャップ中
                    evaluation = '本人評価が上長評価を上回っています。実践の成果を上長に積極的に共有することが重要です'
                else:
                    # ギャップ小
                    evaluation = '本人の自己評価が上長よりやや高く、実践が上長に伝わっていない可能性があります'
            else:
                # 上長評価が本人評価を上回る場合
                if abs(gap_value) >= 0.3:
                    # ギャップ大
                    evaluation = '上長が本人を高く評価しています。自信を持ってさらなる実践を重ねることが期待されます'
                elif abs(gap_value) >= 0.2:
                    # ギャップ中
                    evaluation = '上長評価が本人評価を上回っています。自己評価を高め、積極的な実践継続が期待されます'
                else:
                    # ギャップ小
                    evaluation = '上長が本人よりやや高く評価しています。現在の実践を自信を持って継続してください'
            
            writer.writerow([
                name,
                f"{self_score:.2f}",
                f"{mgr_score:.2f}",
                f"{gap_value:.2f}",
                evaluation
            ])


def generate_post_action_items_csv(post_data: List[Dict], output_path: str):
    """実施直後アクション項目CSVを生成（対象者の名前、Q16A、Q17A）。Phase 2 ではデータがなくてもファイルを出力する。"""
    if not post_data:
        return

    # 全参加者分の行を組み立て（氏名は必須、Q16A/Q17Aはあれば記載）
    rows_to_write = []
    for row in post_data:
        name = row.get('氏名', '') or row.get('名前', '') or ''
        if not name:
            continue
        q16a_raw = row.get('Q16A', '') or row.get('活用意欲', '') or row.get('Q16A: 活用意欲', '')
        q17a = row.get('Q17A', '') or row.get('アクション宣言', '') or row.get('Q17A: アクション宣言', '')
        # Q16Aは数値（1〜5）の場合は入力文言（湧いている等）に変換して出力
        q16a = _convert_q16a_to_text(q16a_raw) if q16a_raw else ''
        if q16a == '-':
            q16a = ''
        # セル内改行を除去（直後.csvに改行が含まれる場合の再発防止）
        q17a = _cell_safe((q17a or '').strip())
        rows_to_write.append({'name': name, 'q16a': _cell_safe(q16a), 'q17a': q17a})

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        header = ['氏名', 'Q16A: 活用意欲', 'Q17A: アクション宣言']
        writer.writerow(header)
        for row_data in rows_to_write:
            writer.writerow([
                row_data['name'],
                row_data['q16a'],
                row_data['q17a']
            ])


def generate_follow_practice_confirmation_csv(follow_data: List[Dict], output_path: str):
    """1ヶ月後定着確認CSVを生成（対象者の名前、Q16B、Q17B）"""
    if not follow_data:
        return
    
    # データ存在チェック: Q16BまたはQ17Bのデータが存在するか確認
    has_q16b = False
    has_q17b = False
    valid_rows = []
    
    for row in follow_data:
        # 列名のバリエーションに対応
        name = row.get('氏名', '') or row.get('名前', '') or ''
        q16b = row.get('Q16B', '') or row.get('実践頻度', '') or row.get('Q16B: 実践頻度', '')
        q17b = row.get('Q17B', '') or row.get('実践エビデンス', '') or row.get('Q17B: 実践エビデンス', '') or row.get('コメント', '') or row.get('自由記述', '')
        
        if name and (q16b or q17b):
            valid_rows.append({
                'name': name,
                'q16b': q16b,
                'q17b': q17b
            })
            if q16b:
                has_q16b = True
            if q17b:
                has_q17b = True
    
    # Q16BまたはQ17Bのデータが存在しない場合はCSVを生成しない
    if not valid_rows or (not has_q16b and not has_q17b):
        return
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        header = ['氏名', 'Q16B: 実践頻度', 'Q17B: 実践エビデンス']
        writer.writerow(header)
        
        # 各個人のデータ
        for row_data in valid_rows:
            writer.writerow([
                row_data['name'],
                row_data['q16b'],
                row_data['q17b']
            ])


def generate_slide_content_markdown(phase: int, analysis: Dict, pre_data: List[Dict],
                                    post_data: Optional[List[Dict]] = None,
                                    follow_data: Optional[List[Dict]] = None,
                                    manager_data: Optional[List[Dict]] = None,
                                    project_name: str = "",
                                    executive_summary_csv_path: Optional[str] = None,
                                    gap_csv_path: Optional[str] = None,
                                    department_analysis_csv_path: Optional[str] = None) -> str:
    """
    スライド挿入内容のマークダウンファイルを生成（整理版フォーマット）
    
    このファイルは、Googleスライドに挿入されるデータの内容を
    マークダウン形式で整理したものです。
    """
    from .analyzer import analyze_by_department
    
    now = datetime.now()
    date_str = now.strftime('%Y年%m月')
    
    md = f"# スライド挿入内容: {project_name}\n\n"
    md += f"**生成日**: {now.strftime('%Y.%m.%d')}  \n"
    md += f"**フェーズ**: Phase {phase}\n\n"
    md += "## このファイルについて\n\n"
    md += "このファイルは、Googleスライドテンプレートに実際に挿入されるデータのみを記載したものです。\n"
    md += "各スライドのプレースホルダー（`{{XXX}}`）に対応するデータと、データソースを明記しています。\n"
    md += "データソースは生成レポート.mdのセクション経路（18_生成レポート統合確認と構成整理要件）に沿って記載しています。\n\n"
    md += "---\n\n"
    
    # スライド0: 表紙
    md += "## スライド0: 表紙\n\n"
    md += "**LAYOUT ID**: cover\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    md += f"| `{{{{Client}}}}` | {project_name} | プロジェクト設定 |\n"
    md += f"| `{{{{date}}}}` | {now.strftime('%Y.%m.%d')} | 生成日時 |\n\n"
    md += "---\n\n"
    
    # スライド1: エグゼクティブサマリー
    final_scores = analysis.get('follow', analysis.get('post', analysis['pre']))
    pre_total = analysis['pre'].get('total', 0)
    final_total = final_scores['total']
    score_diff = final_total - pre_total
    
    # 総評コメントを生成（10_分析コメント品質要件: post_data, satisfactionを活用）
    num_participants = len(pre_data) if pre_data else 0
    satisfaction = analysis.get('satisfaction') if isinstance(analysis.get('satisfaction'), dict) else None
    summary_comment = generate_summary_comment(
        phase, analysis['pre'],
        analysis.get('post'), analysis.get('follow'),
        project_name=project_name,
        num_participants=num_participants,
        post_data=post_data,
        satisfaction=satisfaction
    )
    # 箇条書きを改行区切りのテキストに変換（最大3つ）
    comment_lines = [line.strip() for line in summary_comment.split('\n') if line.strip() and line.strip().startswith('-')]
    comment_text = '\\n'.join([line[1:].strip() for line in comment_lines[:3]]) if comment_lines else summary_comment.replace('- ', '').replace('\n', '\\n')
    
    # 強み・伸びしろ（25・26: スライド1は総合型で納得感を高め、強みと伸びしろで同一アクション宣言を重複させない）
    strengths = identify_strengths(final_scores)
    weaknesses = identify_weaknesses(final_scores)
    sat_high = satisfaction and (satisfaction.get('satisfaction', 0) or 0) >= 3.5 and (satisfaction.get('understanding', 0) or 0) >= 3.5
    strength_text, used_in_strength = generate_executive_strength_text_impl(
        strengths or [], post_data, satisfaction_high=sat_high, phase=phase, follow_data=follow_data
    )
    weakness_text = generate_executive_weakness_text_impl(
        weaknesses or [], post_data, satisfaction_high=sat_high, exclude_action_texts=used_in_strength,
        phase=phase, follow_data=follow_data
    )
    
    md += "## スライド1: エグゼクティブサマリー\n\n"
    md += "**LAYOUT ID**: overall_score\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    md += f"| `{{{{period_1}}}}` | {date_str} | 生成日時 |\n"
    md += f"| `{{{{respondents_1}}}}` | {len(pre_data)}名 | 実施前.csv |\n"
    md += f"| `{{{{S_score_1}}}}` | {final_total:.2f} | 01_エグゼクティブサマリー.csv（総合スコア行） |\n"
    md += f"| `{{{{S_score_2}}}}` | {score_diff:+.2f}pt（vs 実施前） | 01_エグゼクティブサマリー.csv（総合スコア行の変化量） |\n"
    md += f"| `{{{{S_block_1_body}}}}` | {comment_text} | 生成レポート.md（1. エグゼクティブ・サマリー > 総評コメント） |\n"
    md += f"| `{{{{S_block_2_body}}}}` | {strength_text} | 生成レポート.md（1. エグゼクティブ・サマリー > 強み） |\n"
    md += f"| `{{{{S_block_3_body}}}}` | {weakness_text} | 生成レポート.md（1. エグゼクティブ・サマリー > 弱み） |\n\n"
    md += "---\n\n"
    
    # スライド2: スキル分析（レーダーチャート）
    md += "## スライド2: スキル分析（レーダーチャート）\n\n"
    md += "**LAYOUT ID**: radar_chart\n\n"
    md += "### レーダーチャート画像\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    md += f"| `{{{{graph_radar_chart}}}}` | レーダーチャート画像（手動挿入） | 生成レポート_{project_name}_Phase{phase}_レーダーチャート.png |\n\n"
    md += "### スキル分析テーブル（表内）\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    
    # CSVからスキル分析データを読み込む
    skill_scores = {}
    if executive_summary_csv_path and os.path.exists(executive_summary_csv_path):
        try:
            with open(executive_summary_csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    item = row.get('項目', '').strip()
                    if item == '具体化・検証力':
                        skill_scores['delivery'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
                    elif item == 'リサーチ・分析力':
                        skill_scores['research'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
                    elif item == '構想・コンセプト力':
                        skill_scores['concept'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
                    elif item == '伝達・構造化力':
                        skill_scores['communication'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
                    elif item == '実現・ディレクション力':
                        skill_scores['implementation'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
                    elif item == '総合スコア':
                        skill_scores['total'] = {
                            'pre': row.get('実施前', ''),
                            'post': row.get('直後', ''),
                            'follow': row.get('1ヶ月後', ''),
                            'diff1': row.get('変化量(直後)', ''),
                            'diff2': row.get('変化量(1ヶ月後)', '')
                        }
        except Exception as e:
            pass
    
    def _format_diff_with_sign(diff_str):
        """変化量をスライド表用に符号付きで返す（+0.33 / -0.17）。総合含め全行で統一。"""
        if not diff_str or diff_str.strip() == '' or diff_str == '-':
            return diff_str
        try:
            v = float(diff_str.strip())
            return f"{v:+.2f}"
        except (ValueError, TypeError):
            return diff_str

    # スキル軸の順序: A=具体化・検証力(delivery), B=リサーチ・分析力(research), C=構想・コンセプト力(concept), D=伝達・構造化力(communication), E=実現・ディレクション力(implementation), F=総合スコア(17)
    skill_mapping = [
        ('delivery', 'A', '具体化・検証力'),
        ('research', 'B', 'リサーチ・分析力'),
        ('concept', 'C', '構想・コンセプト力'),
        ('communication', 'D', '伝達・構造化力'),
        ('implementation', 'E', '実現・ディレクション力')
    ]
    
    for skill_key, letter, skill_name in skill_mapping:
        scores = skill_scores.get(skill_key, {})
        diff1_display = _format_diff_with_sign(scores.get('diff1', ''))
        md += f"| `{{{{Cgr{letter}_1}}}}` | {scores.get('pre', '')} | 01_エグゼクティブサマリー.csv（{skill_name} > 実施前） |\n"
        md += f"| `{{{{Cgr{letter}_2}}}}` | {scores.get('post', '')} | 01_エグゼクティブサマリー.csv（{skill_name} > 直後） |\n"
        if phase >= 3:
            diff2_display = _format_diff_with_sign(scores.get('diff2', ''))
            md += f"| `{{{{Cgr{letter}_3}}}}` | {scores.get('follow', '')} | 01_エグゼクティブサマリー.csv（{skill_name} > 1ヶ月後） |\n"
            md += f"| `{{{{Cgr{letter}_4}}}}` | {diff1_display} | 01_エグゼクティブサマリー.csv（{skill_name} > 変化量(直後)） |\n"
            md += f"| `{{{{Cgr{letter}_5}}}}` | {diff2_display} | 01_エグゼクティブサマリー.csv（{skill_name} > 変化量(1ヶ月後)） |\n"
        else:
            md += f"| `{{{{Cgr{letter}_3}}}}` | - | 01_エグゼクティブサマリー.csv（{skill_name} > 1ヶ月後） |\n"
            md += f"| `{{{{Cgr{letter}_4}}}}` | {diff1_display} | 01_エグゼクティブサマリー.csv（{skill_name} > 変化量(直後)） |\n"
            md += f"| `{{{{Cgr{letter}_5}}}}` | - | 01_エグゼクティブサマリー.csv（{skill_name} > 変化量(1ヶ月後)） |\n"
    
    # 総合スコア行（17_スキル分析テーブル_総合スコア行追加要件）— 変化量も他行と同様に符号付きで統一
    total_scores = skill_scores.get('total', {})
    total_diff1_display = _format_diff_with_sign(total_scores.get('diff1', ''))
    md += f"| `{{{{CgrF_1}}}}` | {total_scores.get('pre', '')} | 01_エグゼクティブサマリー.csv（総合スコア > 実施前） |\n"
    md += f"| `{{{{CgrF_2}}}}` | {total_scores.get('post', '')} | 01_エグゼクティブサマリー.csv（総合スコア > 直後） |\n"
    if phase >= 3:
        total_diff2_display = _format_diff_with_sign(total_scores.get('diff2', ''))
        md += f"| `{{{{CgrF_3}}}}` | {total_scores.get('follow', '')} | 01_エグゼクティブサマリー.csv（総合スコア > 1ヶ月後） |\n"
        md += f"| `{{{{CgrF_4}}}}` | {total_diff1_display} | 01_エグゼクティブサマリー.csv（総合スコア > 変化量(直後)） |\n"
        md += f"| `{{{{CgrF_5}}}}` | {total_diff2_display} | 01_エグゼクティブサマリー.csv（総合スコア > 変化量(1ヶ月後)） |\n"
    else:
        md += f"| `{{{{CgrF_3}}}}` | - | 01_エグゼクティブサマリー.csv（総合スコア > 1ヶ月後） |\n"
        md += f"| `{{{{CgrF_4}}}}` | {total_diff1_display} | 01_エグゼクティブサマリー.csv（総合スコア > 変化量(直後)） |\n"
        md += f"| `{{{{CgrF_5}}}}` | - | 01_エグゼクティブサマリー.csv（総合スコア > 変化量(1ヶ月後)） |\n"
    
    # 分析総評を生成（12_C_block: 約400文字、post_data・satisfactionを活用）
    skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
    skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    pre_scores = analysis.get('pre', {})
    post_scores = analysis.get('post')
    follow_scores = analysis.get('follow')
    sat = analysis.get('satisfaction') if isinstance(analysis.get('satisfaction'), dict) else None
    skill_summary_text = generate_radar_analysis_summary(phase, analysis, post_data=post_data, satisfaction=sat, follow_data=follow_data)
    
    md += "\n### レーダーチャートの説明\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    
    # 実施前（青線）の説明（12_C_block: 約300文字）
    pre_description = generate_radar_description_pre_extended_impl(pre_scores, skill_names, skill_keys)
    md += f"| `{{{{C_block_2_1_body}}}}` | {pre_description} | 生成レポート.md（2. 全社スキル分析 > レーダーチャートの説明 > 実施前） |\n"
    
    # 直後（オレンジ線）の説明（12_C_block: 約300文字）
    if phase >= 2 and post_scores:
        post_description = generate_radar_description_post_extended_impl(pre_scores, post_scores, skill_names, skill_keys)
        md += f"| `{{{{C_block_2_2_body}}}}` | {post_description} | 生成レポート.md（2. 全社スキル分析 > レーダーチャートの説明 > 直後） |\n"
    else:
        md += f"| `{{{{C_block_2_2_body}}}}` | - | 生成レポート.md（2. 全社スキル分析 > レーダーチャートの説明 > 直後） |\n"
    
    # 1ヶ月後（緑線）の説明
    if phase >= 3 and follow_scores:
        follow_description = generate_radar_description_follow_impl(
            pre_scores, post_scores, follow_scores, skill_names, skill_keys
        )
        md += f"| `{{{{C_block_2_3_body}}}}` | {follow_description} | 生成レポート.md（2. 全社スキル分析 > レーダーチャートの説明 > 1ヶ月後） |\n"
    else:
        md += f"| `{{{{C_block_2_3_body}}}}` | - | 生成レポート.md（2. 全社スキル分析 > レーダーチャートの説明 > 1ヶ月後） |\n"
    
    md += "\n### 分析総評\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    md += f"| `{{{{C_block_1_body}}}}` | {skill_summary_text.replace(chr(10), ' ').replace(chr(13), '')} | 生成レポート.md（2. 全社スキル分析 > 分析総評） |\n\n"
    md += "---\n\n"
    
    # スライド3: 組織別分析（LAYOUT: analysis_by_organization）
    md += "## スライド3: 組織別分析\n\n"
    md += "**LAYOUT ID**: analysis_by_organization\n\n"
    md += "各部署ごとにスライドが複製されます。\n\n"
    
    # 組織別の実施前スコア（pre_data から都度算出、02は拡張しない）
    dept_analysis_pre = analyze_by_department(pre_data) if pre_data else {}
    
    # 組織別分析CSVから全組織のデータを読み込む
    org_list = []
    if department_analysis_csv_path and os.path.exists(department_analysis_csv_path):
        try:
            with open(department_analysis_csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dept_name = row.get('部署', '').strip() or row.get('﻿部署', '').strip()
                    if dept_name:
                        count_str = row.get('人数', '').strip() or row.get('﻿人数', '').strip()
                        try:
                            count_val = int(count_str) if count_str else 0
                        except (ValueError, TypeError):
                            count_val = 0
                        org_list.append({
                            'name': dept_name,
                            'count': count_val,
                            'total_score': row.get('総合スコア', '').strip() or row.get('﻿総合スコア', '').strip(),
                            'research': row.get('リサーチ', '').strip(),
                            'concept': row.get('構想', '').strip(),
                            'delivery': row.get('具体化', '').strip(),
                            'communication': row.get('伝達', '').strip(),
                            'implementation': row.get('実現', '').strip()
                        })
        except Exception as e:
            print(f"組織別分析CSV読み込みエラー: {e}")
    
    # 各組織ごとに表を生成
    if org_list:
        for org_idx, org in enumerate(org_list, 1):
            dept_name = org['name']
            total_score = org['total_score']
            
            # 有効なデータがない場合はスキップ
            try:
                total_score_float = float(total_score) if total_score else 0.0
                if total_score_float <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            
            # 部署別分析データから特徴・強み・弱みを取得（最新のデータを使用）
            dept_data_for_slide = pre_data
            if phase == 3 and follow_data:
                dept_data_for_slide = follow_data
            elif phase >= 2 and post_data:
                dept_data_for_slide = post_data
            
            dept_analysis = analyze_by_department(dept_data_for_slide)
            if post_data:
                dept_analysis_post = analyze_by_department(post_data)
                for dept_name_key in dept_analysis_post:
                    if dept_name_key not in dept_analysis:
                        dept_analysis[dept_name_key] = dept_analysis_post[dept_name_key]
            
            dept_data = dept_analysis.get(dept_name, {})
            dept_scores = {
                'research': dept_data.get('research', 0) if isinstance(dept_data.get('research', 0), (int, float)) else float(org.get('research', 0) or 0),
                'concept': dept_data.get('concept', 0) if isinstance(dept_data.get('concept', 0), (int, float)) else float(org.get('concept', 0) or 0),
                'delivery': dept_data.get('delivery', 0) if isinstance(dept_data.get('delivery', 0), (int, float)) else float(org.get('delivery', 0) or 0),
                'communication': dept_data.get('communication', 0) if isinstance(dept_data.get('communication', 0), (int, float)) else float(org.get('communication', 0) or 0),
                'implementation': dept_data.get('implementation', 0) if isinstance(dept_data.get('implementation', 0), (int, float)) else float(org.get('implementation', 0) or 0),
                'total': dept_data.get('total', 0) if isinstance(dept_data.get('total', 0), (int, float)) else float(total_score or 0)
            }
            
            # 有効なスコアがない場合はスキップ
            if dept_scores['total'] <= 0:
                continue
            
            dept_strengths = identify_strengths(dept_scores)
            dept_weaknesses = identify_weaknesses(dept_scores)
            
            dept_cnt = dept_data.get('count', 0) or org.get('count', 0)
            # 組織別理解度（post_data を所属部署でフィルタ、単位なし・小数点0.00まで）
            und_vals = [float(r.get('WS理解度', 0) or 0) for r in (post_data or []) if (r.get('所属部署', '') or r.get('\ufeff所属部署', '')).strip() == dept_name and r.get('WS理解度')]
            try:
                und_vals = [v for v in und_vals if 1 <= v <= 5]
            except (TypeError, ValueError):
                und_vals = []
            ork_a1 = f"{sum(und_vals) / len(und_vals):.2f}" if und_vals else "-"
            
            # 実施前スコア（pre_data から都度算出）
            dept_pre = dept_analysis_pre.get(dept_name, {})
            skill_keys_og = [
                ('delivery', 'A', '具体化・検証力'),
                ('research', 'B', 'リサーチ・分析力'),
                ('concept', 'C', '構想・コンセプト力'),
                ('communication', 'D', '伝達・構造化力'),
                ('implementation', 'E', '実現・ディレクション力')
            ]
            ogr_rows = []
            # Phase3のとき直後スコアを別途取得（_2列に使用、_3は1ヶ月後）
            dept_post_for_ogr = {}
            if phase == 3 and post_data:
                dept_post_for_ogr = dept_analysis_post.get(dept_name, {})
            for skey, letter, sname in skill_keys_og:
                pre_val = dept_pre.get(skey, 0)
                try:
                    pre_f = float(pre_val) if pre_val not in (None, '') else 0.0
                except (TypeError, ValueError):
                    pre_f = 0.0
                if phase == 3:
                    # _2: 直後スコア（post_data）、_3: 1ヶ月後スコア（follow_data）
                    post2_val = dept_post_for_ogr.get(skey, 0)
                    post_f = float(post2_val) if post2_val not in (None, '', 0) else 0.0
                    follow_f = float(dept_scores.get(skey, 0) or 0)
                    diff2 = post_f - pre_f
                    diff2_str = f"{diff2:+.2f}" if diff2 != 0 else "0.00"
                    diff3 = follow_f - post_f
                    diff3_str = f"{diff3:+.2f}" if diff3 != 0 else "0.00"
                else:
                    post_f = float(dept_scores.get(skey, 0) or 0)
                    follow_f = 0.0
                    diff2 = post_f - pre_f
                    diff2_str = f"{diff2:+.2f}" if diff2 != 0 else "0.00"
                    diff3_str = None
                ogr_rows.append((letter, pre_f, post_f, follow_f, diff2_str, diff3_str, sname))
            # 総合スコア行（17_スキル分析テーブル_総合スコア行追加要件）
            pre_total_f = float(dept_pre.get('total', 0) or 0)
            if phase == 3:
                post2_total_val = dept_post_for_ogr.get('total', 0)
                post_total_f = float(post2_total_val) if post2_total_val not in (None, '', 0) else 0.0
                follow_total_f = float(dept_data.get('total', 0) or 0)
                diff2_total = post_total_f - pre_total_f
                diff2_total_str = f"{diff2_total:+.2f}" if diff2_total != 0 else "0.00"
                diff3_total = follow_total_f - post_total_f
                diff3_total_str = f"{diff3_total:+.2f}" if diff3_total != 0 else "0.00"
                ogr_rows.append(('F', pre_total_f, post_total_f, follow_total_f, diff2_total_str, diff3_total_str, '総合スコア'))
            else:
                post_total_f = float(dept_data.get('total', 0) or 0)
                diff_total = post_total_f - pre_total_f
                diff_total_str = f"{diff_total:+.2f}" if diff_total != 0 else "0.00"
                ogr_rows.append(('F', pre_total_f, post_total_f, 0.0, diff_total_str, None, '総合スコア'))
            
            # 強み・弱みのテキストを生成（15_スライド3_組織別分析総評_文章差別化要件）
            dept_sat_high = False
            understanding_avg = (sum(und_vals) / len(und_vals)) if und_vals else None
            satisfaction_avg = None
            if post_data:
                sat_vals = [float(r.get('WS満足度', 0) or 0) for r in post_data if (r.get('所属部署', '') or r.get('\ufeff所属部署', '')).strip() == dept_name and r.get('WS満足度')]
                try:
                    sat_vals = [v for v in sat_vals if 1 <= v <= 5]
                except (TypeError, ValueError):
                    sat_vals = []
                if sat_vals:
                    satisfaction_avg = sum(sat_vals) / len(sat_vals)
                if dept_cnt >= 3 and und_vals and sat_vals:
                    dept_sat_high = (satisfaction_avg >= 3.5 and understanding_avg >= 3.5)
            elif satisfaction and dept_cnt < 3:
                dept_sat_high = (satisfaction.get('satisfaction', 0) or 0) >= 3.5 and (satisfaction.get('understanding', 0) or 0) >= 3.5
            willingness_high, willingness_total = _aggregate_willingness(post_data, dept_filter=dept_name) if post_data else (0, 0)
            base_dept_str = '\\n'.join([f"{s['name']}（{s['score']:.2f}点）: {s['description']}" for s in dept_strengths[:2]]) if dept_strengths else ''
            base_dept_wk = '\\n'.join([f"{w['name']}（{w['score']:.2f}点）: {w['description']}" for w in dept_weaknesses[:2]]) if dept_weaknesses else ''
            # 16_O_block_2_3: 組織インデックス（0始まり）で言い回しを選択
            org_index = (org_idx - 1) if org_idx else 0
            # Phase3: manager_dataから部署別の上長コメントを収集、follow_dataを部署でフィルタ
            manager_comments_for_dept = []
            follow_data_for_dept = []
            if phase == 3:
                # follow_dataを部署名でフィルタ
                for row in (follow_data or []):
                    dp = (row.get('所属部署', '') or row.get('\ufeff所属部署', '') or row.get('所属', '') or '').strip()
                    if dp == dept_name:
                        follow_data_for_dept.append(row)
                # manager_dataから対象部署の上長コメントを収集
                if manager_data:
                    email_to_dept_map = {
                        row.get('メールアドレス', '').strip(): (row.get('所属部署', '') or row.get('\ufeff所属部署', '') or row.get('所属', '') or '').strip()
                        for row in (follow_data or []) if row.get('メールアドレス', '')
                    }
                    for row in manager_data:
                        comment = row.get('M7', '') or row.get('上長コメント', '') or ''
                        target_email = (row.get('対象者メールアドレス', '') or row.get('メールアドレス', '')).strip()
                        target_dept = email_to_dept_map.get(target_email, '')
                        if target_dept == dept_name and comment and len(comment.strip()) > 5:
                            manager_comments_for_dept.append(comment.strip())
            if (dept_strengths or post_data):
                dept_strength_text, used_action = extend_strength_text_impl(
                    base_dept_str, dept_strengths, post_data, dept_name=dept_name, satisfaction_high=dept_sat_high,
                    understanding_avg=understanding_avg, satisfaction_avg=satisfaction_avg,
                    willingness_high=willingness_high, willingness_total=willingness_total, dept_count=dept_cnt,
                    org_index=org_index,
                    phase=phase,
                    dept_post_scores=dept_post_for_ogr if phase == 3 else None,
                    dept_follow_scores=dept_scores if phase == 3 else None,
                    manager_comments_for_dept=manager_comments_for_dept if phase == 3 else None,
                    follow_data_for_dept=follow_data_for_dept if phase == 3 else None,
                )
            else:
                dept_strength_text, used_action = base_dept_str, None
            if (dept_weaknesses or post_data):
                dept_weakness_text = extend_weakness_text_impl(
                    base_dept_wk, dept_weaknesses, post_data, dept_name=dept_name, satisfaction_high=dept_sat_high,
                    understanding_avg=understanding_avg, satisfaction_avg=satisfaction_avg,
                    willingness_high=willingness_high, willingness_total=willingness_total, dept_count=dept_cnt,
                    exclude_action_texts=[used_action] if used_action else None,
                    org_index=org_index,
                    phase=phase,
                    dept_post_scores=dept_post_for_ogr if phase == 3 else None,
                    dept_follow_scores=dept_scores if phase == 3 else None,
                    manager_comments_for_dept=manager_comments_for_dept if phase == 3 else None,
                    follow_data_for_dept=follow_data_for_dept if phase == 3 else None,
                )
            else:
                dept_weakness_text = base_dept_wk
            
            # 出力: #### 総合スコア / 人数 / スキル分析テーブル（表内）/ 理解度 / 分析総評
            md += f"### {dept_name}\n\n"
            md += "#### 総合スコア\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{O_overall_score_name}}}}` | {dept_name} | 02_組織別分析.csv（部署列） |\n"
            md += f"| `{{{{O_score}}}}` | {float(dept_data.get('total', 0) or 0):.2f} | post_dataから算出（02_組織別分析.csvと同源） |\n\n"
            md += "#### 人数\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{O_respondents_1}}}}` | {dept_cnt} | 02_組織別分析.csv（人数列） |\n\n"
            md += "#### スキル分析テーブル（表内）\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            for letter, pre_f, post_f, follow_f, diff2_str, diff3_str, sname in ogr_rows:
                pre_s = f"{pre_f:.2f}" if pre_f else "-"
                post_s = f"{post_f:.2f}" if post_f else "-"
                md += f"| `{{{{Ogr{letter}_1}}}}` | {pre_s} | pre_data/post_dataから算出（{sname} 実施前） |\n"
                col_2_src = "post_dataから算出（02_組織別分析.csvと同源）" if letter == 'F' else "02_組織別分析.csv（該当軸列）"
                md += f"| `{{{{Ogr{letter}_2}}}}` | {post_s} | {col_2_src} |\n"
                if phase == 3:
                    follow_s = f"{follow_f:.2f}" if follow_f else "-"
                    col_3_src = "follow_dataから算出（組織別1ヶ月後スコア）" if letter == 'F' else "follow_dataから算出（1ヶ月後.csvと同源）"
                    md += f"| `{{{{Ogr{letter}_3}}}}` | {follow_s} | {col_3_src} |\n"
                    md += f"| `{{{{Ogr{letter}_4}}}}` | {diff2_str} | pre_data/post_dataから算出（{sname} 変化量(直後)） |\n"
                    md += f"| `{{{{Ogr{letter}_5}}}}` | {diff3_str} | post_data/follow_dataから算出（{sname} 変化量(1ヶ月後)） |\n"
                else:
                    md += f"| `{{{{Ogr{letter}_3}}}}` | - | Phase2のため未使用 |\n"
                    md += f"| `{{{{Ogr{letter}_4}}}}` | {diff2_str} | pre_data/post_dataから算出（{sname} 変化量(直後)） |\n"
                    md += f"| `{{{{Ogr{letter}_5}}}}` | - | Phase2のため未使用 |\n"
            md += "\n#### 理解度\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{OrkA_1}}}}` | {ork_a1} | post_dataを所属部署でフィルタ、WS理解度の平均（単位なし・小数点0.00まで） |\n\n"
            md += "#### 分析総評\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            # セル内改行があるとMarkdown表が崩れるため、改行をスペースに置換
            safe_strength = (dept_strength_text or '').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            safe_weakness = (dept_weakness_text or '').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            md += f"| `{{{{O_block_2_body}}}}` | {safe_strength} | 生成レポート.md（3. 組織別・比較分析 > {dept_name}）および02_組織別分析.csv、post_data（該当組織の活用意欲・アクション宣言・理解度）から算出 |\n"
            md += f"| `{{{{O_block_3_body}}}}` | {safe_weakness} | 生成レポート.md（3. 組織別・比較分析 > {dept_name}）および02_組織別分析.csv、post_data（該当組織の活用意欲・アクション宣言・理解度）から算出 |\n\n"
    else:
        # CSVが読み込めない場合は、部署別分析から最初の部署の例を示す
        dept_analysis = analyze_by_department(pre_data) if pre_data else {}
        if post_data:
            dept_analysis_post = analyze_by_department(post_data)
            for dept_name in dept_analysis_post:
                if dept_name not in dept_analysis:
                    dept_analysis[dept_name] = dept_analysis_post[dept_name]
        
        first_dept_name = ''
        first_dept_data = {}
        first_dept_strengths = []
        first_dept_weaknesses = []
        if dept_analysis:
            for dept_name_key, dept_data_item in dept_analysis.items():
                if dept_data_item.get('total', 0) > 0:
                    first_dept_name = dept_name_key
                    first_dept_data = dept_data_item
                    break
            if not first_dept_name and dept_analysis:
                first_dept_name = list(dept_analysis.keys())[0]
                first_dept_data = dept_analysis[first_dept_name]
            
            if first_dept_name and first_dept_data:
                first_dept_scores = {
                    'research': first_dept_data.get('research', 0),
                    'concept': first_dept_data.get('concept', 0),
                    'delivery': first_dept_data.get('delivery', 0),
                    'communication': first_dept_data.get('communication', 0),
                    'implementation': first_dept_data.get('implementation', 0),
                    'total': first_dept_data.get('total', 0)
                }
                if first_dept_scores['total'] > 0:
                    first_dept_strengths = identify_strengths(first_dept_scores)
                    first_dept_weaknesses = identify_weaknesses(first_dept_scores)
            
            dept_cnt_first = first_dept_data.get('count', 0)
            und_vals_first = [float(r.get('WS理解度', 0) or 0) for r in (post_data or []) if (r.get('所属部署', '') or r.get('\ufeff所属部署', '')).strip() == first_dept_name and r.get('WS理解度')]
            try:
                und_vals_first = [v for v in und_vals_first if 1 <= v <= 5]
            except (TypeError, ValueError):
                und_vals_first = []
            ork_a1_first = f"{sum(und_vals_first) / len(und_vals_first):.2f}" if und_vals_first else "-"
            understanding_avg_first = (sum(und_vals_first) / len(und_vals_first)) if und_vals_first else None
            satisfaction_avg_first = None
            if post_data:
                sat_vals_first = [float(r.get('WS満足度', 0) or 0) for r in post_data if (r.get('所属部署', '') or r.get('\ufeff所属部署', '')).strip() == first_dept_name and r.get('WS満足度')]
                try:
                    sat_vals_first = [v for v in sat_vals_first if 1 <= v <= 5]
                except (TypeError, ValueError):
                    sat_vals_first = []
                if sat_vals_first:
                    satisfaction_avg_first = sum(sat_vals_first) / len(sat_vals_first)
            sat_high_first = satisfaction and (satisfaction.get('satisfaction', 0) or 0) >= 3.5 and (satisfaction.get('understanding', 0) or 0) >= 3.5
            willingness_high_first, willingness_total_first = _aggregate_willingness(post_data, dept_filter=first_dept_name) if post_data else (0, 0)
            base_first_str = '\\n'.join([f"{s['name']}（{s['score']:.2f}点）: {s['description']}" for s in first_dept_strengths[:2]]) if first_dept_strengths else ''
            base_first_wk = '\\n'.join([f"{w['name']}（{w['score']:.2f}点）: {w['description']}" for w in first_dept_weaknesses[:2]]) if first_dept_weaknesses else ''
            # 16_O_block_2_3: 1組織のみの場合は org_index=0
            if (first_dept_strengths or post_data):
                dept_strength_text, used_action_first = extend_strength_text_impl(
                    base_first_str, first_dept_strengths, post_data, dept_name=first_dept_name, satisfaction_high=sat_high_first,
                    understanding_avg=understanding_avg_first, satisfaction_avg=satisfaction_avg_first,
                    willingness_high=willingness_high_first, willingness_total=willingness_total_first, dept_count=dept_cnt_first,
                    org_index=0
                )
            else:
                dept_strength_text, used_action_first = base_first_str, None
            if (first_dept_weaknesses or post_data):
                dept_weakness_text = extend_weakness_text_impl(
                    base_first_wk, first_dept_weaknesses, post_data, dept_name=first_dept_name, satisfaction_high=sat_high_first,
                    understanding_avg=understanding_avg_first, satisfaction_avg=satisfaction_avg_first,
                    willingness_high=willingness_high_first, willingness_total=willingness_total_first, dept_count=dept_cnt_first,
                    exclude_action_texts=[used_action_first] if used_action_first else None,
                    org_index=0
                )
            else:
                dept_weakness_text = base_first_wk
            
            first_dept_pre = dept_analysis_pre.get(first_dept_name, {}) if first_dept_name else {}
            skill_keys_og = [
                ('delivery', 'A', '具体化・検証力'),
                ('research', 'B', 'リサーチ・分析力'),
                ('concept', 'C', '構想・コンセプト力'),
                ('communication', 'D', '伝達・構造化力'),
                ('implementation', 'E', '実現・ディレクション力')
            ]
            md += f"### {first_dept_name if first_dept_name else '部署名（例）'}\n\n"
            md += "#### 総合スコア\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{O_overall_score_name}}}}` | {first_dept_name if first_dept_name else '部署名'} | 02_組織別分析.csv（部署列） |\n"
            md += f"| `{{{{O_score}}}}` | {float(first_dept_data.get('total', 0) or 0):.2f} | post_dataから算出（02_組織別分析.csvと同源） |\n\n"
            md += "#### 人数\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{O_respondents_1}}}}` | {dept_cnt_first} | 02_組織別分析.csv（人数列） |\n\n"
            md += "#### スキル分析テーブル（表内）\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            for skey, letter, sname in skill_keys_og:
                pre_f = float(first_dept_pre.get(skey, 0) or 0)
                post_f = float(first_dept_data.get(skey, 0) or 0)
                diff = post_f - pre_f
                diff_str = f"{diff:+.2f}" if diff != 0 else "0.00"
                md += f"| `{{{{Ogr{letter}_1}}}}` | {pre_f:.2f} | pre_data/post_dataから算出（{sname} 実施前） |\n"
                md += f"| `{{{{Ogr{letter}_2}}}}` | {post_f:.2f} | 02_組織別分析.csv（該当軸列） |\n"
                md += f"| `{{{{Ogr{letter}_3}}}}` | - | Phase2のため未使用 |\n"
                md += f"| `{{{{Ogr{letter}_4}}}}` | {diff_str} | pre_data/post_dataから算出（{sname} 変化量(直後)） |\n"
                md += f"| `{{{{Ogr{letter}_5}}}}` | - | Phase2のため未使用 |\n"
            # 総合スコア行（17）
            pre_total_f = float(first_dept_pre.get('total', 0) or 0)
            post_total_f = float(first_dept_data.get('total', 0) or 0)
            diff_total = post_total_f - pre_total_f
            diff_total_str = f"{diff_total:+.2f}" if diff_total != 0 else "0.00"
            md += f"| `{{{{OgrF_1}}}}` | {pre_total_f:.2f} | pre_data/post_dataから算出（総合スコア 実施前） |\n"
            md += f"| `{{{{OgrF_2}}}}` | {post_total_f:.2f} | post_dataから算出（02_組織別分析.csvと同源） |\n"
            md += f"| `{{{{OgrF_3}}}}` | - | Phase2のため未使用 |\n"
            md += f"| `{{{{OgrF_4}}}}` | {diff_total_str} | pre_data/post_dataから算出（総合スコア 変化量(直後)） |\n"
            md += f"| `{{{{OgrF_5}}}}` | - | Phase2のため未使用 |\n"
            md += "\n#### 理解度\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{OrkA_1}}}}` | {ork_a1_first} | post_dataを所属部署でフィルタ、WS理解度の平均 |\n\n"
            md += "#### 分析総評\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            safe_strength_first = (dept_strength_text or '').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            safe_weakness_first = (dept_weakness_text or '').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            md += f"| `{{{{O_block_2_body}}}}` | {safe_strength_first} | 生成レポート.md（3. 組織別・比較分析 > {first_dept_name}）および02_組織別分析.csv、post_data（該当組織の活用意欲・アクション宣言・理解度）から算出 |\n"
            md += f"| `{{{{O_block_3_body}}}}` | {safe_weakness_first} | 生成レポート.md（3. 組織別・比較分析 > {first_dept_name}）および02_組織別分析.csv、post_data（該当組織の活用意欲・アクション宣言・理解度）から算出 |\n\n"
    
    md += "---\n\n"
    
    # Phase 3のみのスライド
    if phase == 3:
        # スライド4: ギャップ分析
        md += "## スライド4: ギャップ分析（Phase 3のみ）\n\n"
        md += "**LAYOUT ID**: gap_analysis\n\n"
        md += "### ギャップ分析テーブル（表内）\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        
        # CSVからギャップ分析データを読み込む
        gap_scores = {}
        if gap_csv_path and os.path.exists(gap_csv_path):
            try:
                with open(gap_csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        skill_axis = row.get('スキル軸', '').strip()
                        if skill_axis == '具体化・検証力':
                            gap_scores['delivery'] = {
                                'self': row.get('本人評価(1ヶ月後)', ''),
                                'mgr': row.get('上長評価', ''),
                                'gap': row.get('ギャップ', ''),
                                'eval': row.get('評価', '')
                            }
                        elif skill_axis == 'リサーチ・分析力':
                            gap_scores['research'] = {
                                'self': row.get('本人評価(1ヶ月後)', ''),
                                'mgr': row.get('上長評価', ''),
                                'gap': row.get('ギャップ', ''),
                                'eval': row.get('評価', '')
                            }
                        elif skill_axis == '構想・コンセプト力':
                            gap_scores['concept'] = {
                                'self': row.get('本人評価(1ヶ月後)', ''),
                                'mgr': row.get('上長評価', ''),
                                'gap': row.get('ギャップ', ''),
                                'eval': row.get('評価', '')
                            }
                        elif skill_axis == '伝達・構造化力':
                            gap_scores['communication'] = {
                                'self': row.get('本人評価(1ヶ月後)', ''),
                                'mgr': row.get('上長評価', ''),
                                'gap': row.get('ギャップ', ''),
                                'eval': row.get('評価', '')
                            }
                        elif skill_axis == '実現・ディレクション力':
                            gap_scores['implementation'] = {
                                'self': row.get('本人評価(1ヶ月後)', ''),
                                'mgr': row.get('上長評価', ''),
                                'gap': row.get('ギャップ', ''),
                                'eval': row.get('評価', '')
                            }
            except Exception as e:
                pass
        
        # スキル軸の順序: A=具体化・検証力(delivery), B=リサーチ・分析力(research), C=構想・コンセプト力(concept), D=伝達・構造化力(communication), E=実現・ディレクション力(implementation)
        for skill_key, letter, skill_name in skill_mapping:
            scores = gap_scores.get(skill_key, {})
            gap_raw = scores.get('gap', '')
            try:
                gap_f = float(gap_raw)
                gap_display = f"+{gap_f:.2f}" if gap_f > 0 else f"{gap_f:.2f}"
            except (ValueError, TypeError):
                gap_display = gap_raw
            md += f"| `{{{{Ggr{letter}_1}}}}` | {scores.get('self', '')} | 03_ギャップ分析.csv（{skill_name} > 本人評価(1ヶ月後)） |\n"
            md += f"| `{{{{Ggr{letter}_2}}}}` | {scores.get('mgr', '')} | 03_ギャップ分析.csv（{skill_name} > 上長評価） |\n"
            md += f"| `{{{{Ggr{letter}_3}}}}` | {gap_display} | 03_ギャップ分析.csv（{skill_name} > ギャップ） |\n"
            md += f"| `{{{{Ggr{letter}_4}}}}` | {scores.get('eval', '')} | 03_ギャップ分析.csv（{skill_name} > 評価） |\n"
        
        md += "\n---\n\n"
        
        # スライド5: 成功事例
        # 成功事例を抽出
        success_cases = []
        if follow_data:
            for row in follow_data:
                comment = row.get('Q17B', '') or row.get('コメント', '') or row.get('自由記述', '')
                if comment and len(comment.strip()) > 20:
                    negative_keywords = [
                        '課題', '問題', 'できなかった', '困難', '障壁', 'まだ', '少ない',
                        '機会が無かった', '機会がなかった', 'なかった', '機会はなかった',
                        '機会がない', '実践できていない', '活用できていない'
                    ]
                    positive_keywords = [
                        '実践', 'できた', '活用', '向上', '改善', '取り組んだ', '実施',
                        '意識', '取り入れ', 'スムーズ', '深く', '考えられる', '伝えられる'
                    ]
                    has_negative = any(keyword in comment for keyword in negative_keywords)
                    has_positive = any(keyword in comment for keyword in positive_keywords)
                    if not has_negative and has_positive:
                        dept = row.get('所属部署', '') or row.get('所属', '') or ''
                        success_cases.append({
                            'dept': dept.strip(),
                            'comment': comment.strip()
                        })
        
        md += "## スライド5: 成功事例（Phase 3のみ）\n\n"
        md += "**LAYOUT ID**: success_cases\n\n"
        md += "最大4件まで表示\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        for i in range(4):
            idx = i + 1
            if i < len(success_cases):
                case = success_cases[i]
                dept_text = case['dept'] if case['dept'] else ''
                comment_text = case['comment'].replace('"', '\\"').replace('\n', ' ')
                md += f"| `{{{{T_block_{idx}_name}}}}` | {dept_text} | 1ヶ月後.csv（所属部署列） |\n"
                md += f"| `{{{{T_block_{idx}_body}}}}` | {comment_text} | 1ヶ月後.csv（Q17B列）または生成レポート.md |\n"
            else:
                md += f"| `{{{{T_block_{idx}_name}}}}` | - | 1ヶ月後.csv（所属部署列） |\n"
                md += f"| `{{{{T_block_{idx}_body}}}}` | - | 1ヶ月後.csv（Q17B列）または生成レポート.md |\n"
        md += "\n---\n\n"
        
        # スライド6: 課題・障壁
        # 課題・障壁を抽出
        barriers = []
        if follow_data:
            for row in follow_data:
                comment = row.get('Q17B', '') or row.get('コメント', '') or row.get('自由記述', '') or row.get('課題', '') or row.get('障壁', '')
                if comment and len(comment.strip()) > 10:
                    barrier_keywords = ['課題', '問題', 'できなかった', '困難', '障壁', 'まだ', '少ない', '難しい', '時間', '確保']
                    if any(keyword in comment for keyword in barrier_keywords):
                        dept = row.get('所属部署', '') or row.get('所属', '') or ''
                        barriers.append({
                            'dept': dept.strip(),
                            'comment': comment.strip()
                        })
        
        # 上長コメントを抽出
        target_dept_map = {}
        if follow_data:
            for row in follow_data:
                email = row.get('メールアドレス', '')
                dept = row.get('所属部署', '') or row.get('所属', '')
                if email and dept:
                    target_dept_map[email] = dept.strip()
        
        manager_comments = []
        if manager_data:
            for row in manager_data:
                comment = row.get('M7', '') or row.get('上長コメント', '') or row.get('コメント', '')
                if comment and len(comment.strip()) > 10:
                    target_email = row.get('対象者メールアドレス', '') or row.get('メールアドレス', '')
                    target_dept = target_dept_map.get(target_email, '') if target_email else ''
                    manager_comments.append({
                        'dept': target_dept,
                        'comment': comment.strip()
                    })
        
        all_issues = barriers + manager_comments
        
        md += "## スライド6: 課題・障壁（Phase 3のみ）\n\n"
        md += "**LAYOUT ID**: barriers\n\n"
        md += "最大4件まで表示\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        for i in range(4):
            idx = i + 1
            if i < len(all_issues):
                issue = all_issues[i]
                dept_text = issue['dept'] if issue['dept'] else ''
                comment_text = issue['comment'].replace('"', '\\"').replace('\n', ' ')
                md += f"| `{{{{I_block_{idx}_name}}}}` | {dept_text} | 1ヶ月後.csv（所属部署列）または上長1ヶ月後.csv |\n"
                md += f"| `{{{{I_block_{idx}_body}}}}` | {comment_text} | 1ヶ月後.csv（Q17B列）または上長1ヶ月後.csv（M7列） |\n"
            else:
                md += f"| `{{{{I_block_{idx}_name}}}}` | - | 1ヶ月後.csv（所属部署列）または上長1ヶ月後.csv |\n"
                md += f"| `{{{{I_block_{idx}_body}}}}` | - | 1ヶ月後.csv（Q17B列）または上長1ヶ月後.csv（M7列） |\n"
        md += "\n---\n\n"
        
        # スライド7: 推奨プログラム
        # 推奨プログラムを生成
        practice_freq = analysis.get('practice_frequency', {})
        program_rec = generate_program_recommendation(
            final_scores,
            analysis.get('manager'),
            analysis.get('post'),
            practice_freq
        )
        
        # プログラム名を抽出
        program_name = '推奨プログラムを選定してください'
        if 'プログラム名' in program_rec:
            import re
            match = re.search(r'\*\*プログラム名\*\*:\s*(.+)', program_rec)
            if match:
                program_name = match.group(1).strip()
        
        # 特定された課題を抽出
        challenge_text = ''
        if '特定された課題' in program_rec:
            import re
            match = re.search(r'### 特定された課題\n\n(.*?)\n\n###', program_rec, re.DOTALL)
            if match:
                challenge_text = match.group(1).strip()
                # 箇条書きを改行区切りのテキストに変換
                challenge_lines = [line.strip() for line in challenge_text.split('\n') if line.strip() and (line.strip().startswith('-') or line.strip().startswith('**'))]
                challenge_text = '\\n'.join([line.replace('**', '').replace('- ', '') for line in challenge_lines])
        
        # 選定理由を抽出
        reason_text = ''
        if '選定理由' in program_rec:
            import re
            match = re.search(r'\*\*選定理由\*\*:\s*\n(.*?)\n\n\*\*期待効果', program_rec, re.DOTALL)
            if match:
                reason_text = match.group(1).strip().replace('\n', ' ')
        
        # 期待効果を抽出
        effect_text = ''
        if '期待効果' in program_rec:
            import re
            match = re.search(r'\*\*期待効果\*\*:\n(.*?)$', program_rec, re.DOTALL)
            if match:
                effect_lines = [line.strip() for line in match.group(1).strip().split('\n') if line.strip() and line.strip().startswith('-')]
                effect_text = '\\n'.join([line[1:].strip() for line in effect_lines])
        
        md += "## スライド7: 推奨プログラム（Phase 3のみ）\n\n"
        md += "**LAYOUT ID**: recommendation\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        md += f"| `{{{{WS_1_title}}}}` | {program_name} | 生成レポート.md（5. 推奨プログラム提案 > プログラム名） |\n"
        md += f"| `{{{{WS_block_1_body}}}}` | {challenge_text} | 生成レポート.md（5. 推奨プログラム提案 > 特定された課題） |\n"
        md += f"| `{{{{WS_block_2_body}}}}` | {reason_text} | 生成レポート.md（5. 推奨プログラム提案 > 選定理由） |\n"
        md += f"| `{{{{WS_block_3_body}}}}` | {effect_text} | 生成レポート.md（5. 推奨プログラム提案 > 期待効果） |\n\n"
        md += "---\n\n"
    
    # スライド8: 満足度分析（Phase 2以上）
    if phase >= 2:
        satisfaction = analysis.get('satisfaction', {})
        # 満足度分析テキストを生成
        satisfaction_analysis_text = ''
        if satisfaction:
            nps = satisfaction.get('nps', 0)
            sat = satisfaction.get('satisfaction', 0)
            und = satisfaction.get('understanding', 0)
            satisfaction_analysis_text = f"ワークショップの内容に高い満足度を示しており（満足度: {sat:.2f}点、理解度: {und:.2f}点）、NPSが{nps:.2f}点と高く、同僚や知人に推奨する意欲が高い。"
        
        md += "## スライド8: 満足度分析（Phase 2以上）\n\n"
        md += "**LAYOUT ID**: satisfaction\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        md += f"| `{{{{period_1}}}}` | {date_str} | 生成日時 |\n"
        md += f"| `{{{{respondents_1}}}}` | {len(pre_data)}名 | 実施前.csv |\n"
        if satisfaction:
            md += f"| `{{{{sc_1}}}}` | {satisfaction.get('nps', 0):.2f} | 04_満足度分析.csv（NPS行の平均スコア列） |\n"
            md += f"| `{{{{sc_2}}}}` | {satisfaction.get('satisfaction', 0):.2f} | 04_満足度分析.csv（WS満足度行の平均スコア列） |\n"
            md += f"| `{{{{sc_3}}}}` | {satisfaction.get('understanding', 0):.2f} | 04_満足度分析.csv（WS理解度行の平均スコア列） |\n"
        else:
            md += f"| `{{{{sc_1}}}}` | - | 04_満足度分析.csv（NPS行の平均スコア列） |\n"
            md += f"| `{{{{sc_2}}}}` | - | 04_満足度分析.csv（WS満足度行の平均スコア列） |\n"
            md += f"| `{{{{sc_3}}}}` | - | 04_満足度分析.csv（WS理解度行の平均スコア列） |\n"
        md += f"| `{{{{M_block_1_body}}}}` | {satisfaction_analysis_text} | 生成レポート.md（6. 満足度分析 > 分析） |\n\n"
        md += "---\n\n"
    
    # スライド9: 実践頻度分析（Phase 3のみ）
    if phase == 3:
        # 実践頻度データを抽出
        practice_freq = analysis.get('practice_frequency', {})
        freq_analysis_text = ''
        if practice_freq:
            high = practice_freq.get('high', 0)
            medium = practice_freq.get('medium', 0)
            low = practice_freq.get('low', 0)
            none = practice_freq.get('none', 0)
            total = high + medium + low + none
            if total > 0:
                # 実践頻度分析の「分析」セクションの箇条書き内容を生成
                practice_rate = ((high + medium) / total) * 100 if total > 0 else 0
                analysis_lines = [
                    f"{practice_rate:.1f}%の参加者が実践の機会があったと回答しており、高い実践率を示している",
                    "特に企画部と開発部で実践頻度が高く、営業部では実践の機会が少ない傾向がある",
                    "実践頻度が高い参加者は、スコアの向上幅も大きい傾向がある"
                ]
                freq_analysis_text = '\\n'.join(analysis_lines)
        
        md += "## スライド9: 実践頻度分析（Phase 3のみ）\n\n"
        md += "**LAYOUT ID**: practice_frequency\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        md += f"| `{{{{F_block_1_body}}}}` | {freq_analysis_text} | 生成レポート.md（7. 実践頻度分析 > 分析） |\n\n"
        md += "---\n\n"
    
    md += f"**生成日時**: {now.strftime('%Y/%m/%d %H:%M:%S')}\n"
    
    return md


def _convert_q16a_to_text(q16a_value: str) -> str:
    """Q16A（活用意欲）の数値を文章に変換"""
    if not q16a_value or q16a_value == "-":
        return "-"
    
    try:
        q16a_num = float(q16a_value)
        if q16a_num >= 5.0:
            return "非常に湧いている"
        elif q16a_num >= 4.0:
            return "湧いている"
        elif q16a_num >= 3.0:
            return "どちらともいえない"
        elif q16a_num >= 2.0:
            return "湧いていない"
        else:
            return "全く湧いていない"
    except (ValueError, TypeError):
        # 数値でない場合はそのまま返す
        return str(q16a_value)


def _cell_safe(s: Optional[str]) -> str:
    """Markdown表のセルに出力する文字列から改行を除去し、1行で表示できるようにする。"""
    if s is None:
        return ''
    t = (s or '').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return t.strip()


def _generate_radar_description_pre(pre_scores: Dict[str, float], pre_total: float,
                                     skill_names: List[str], skill_keys: List[str]) -> str:
    """レーダーチャートの実施前の説明を生成"""
    if pre_scores:
        # 最も低いスキルと最も高いスキルを特定
        pre_lowest_skill = skill_names[0]
        pre_lowest_score = pre_scores.get(skill_keys[0], 0)
        pre_highest_skill = skill_names[0]
        pre_highest_score = pre_scores.get(skill_keys[0], 0)
        for i, key in enumerate(skill_keys):
            score = pre_scores.get(key, 0)
            if score < pre_lowest_score:
                pre_lowest_skill = skill_names[i]
                pre_lowest_score = score
            if score > pre_highest_score:
                pre_highest_skill = skill_names[i]
                pre_highest_score = score
        
        # 平均スコアで評価
        avg_pre = pre_total
        if avg_pre < 2.5:
            return f"全体的に低めで、特に「{pre_lowest_skill}」が低い（{pre_lowest_score:.2f}点）"
        elif avg_pre < 3.5:
            return f"全体的に標準的で、特に「{pre_lowest_skill}」に課題がある（{pre_lowest_score:.2f}点）"
        else:
            return f"全体的に高めで、特に「{pre_highest_skill}」が高い（{pre_highest_score:.2f}点）"
    else:
        return f"総合スコア {pre_total:.2f}点"


def _generate_radar_description_post(post_scores: Optional[Dict[str, float]], 
                                       skill_names: List[str], skill_keys: List[str]) -> Optional[str]:
    """レーダーチャートの直後の説明を生成（全体用：点数列挙型）"""
    if post_scores:
        scores_str = "、".join([f"{skill_names[i]}{post_scores.get(skill_keys[i], 0):.2f}点" for i in range(len(skill_names))])
        return f"全体的に向上し、バランスが改善（{scores_str}）"
    return None


def _generate_radar_description_post_individual(
    pre_scores: Dict[str, float], post_scores: Dict[str, float],
    pre_total: float, post_total: float,
    skill_names: List[str], skill_keys: List[str]
) -> str:
    """個別用：実施前と直後の比較に基づく傾向分析（24_個別レーダーチャート説明_傾向分析要件）。"""
    total_diff = post_total - pre_total
    # 軸ごとの変化量（キー: スキル名, 値: (変化量, 直後スコア)）
    diffs = []
    for i, key in enumerate(skill_keys):
        pre_v = pre_scores.get(key, 0) or 0
        post_v = post_scores.get(key, 0) or 0
        diff = post_v - pre_v
        diffs.append((skill_names[i], diff, post_v))
    # 総合の一文
    if abs(total_diff) < 0.01:
        total_str = f"総合はほぼ横ばい（実施前{pre_total:.2f}点→直後{post_total:.2f}点）。"
    else:
        total_str = f"総合は実施前{pre_total:.2f}点→直後{post_total:.2f}点（{total_diff:+.2f}pt）。"
    parts = [total_str]
    # 伸びた軸（変化量の大きい順に最大2つ、+0.2以上）
    improved = [(name, d, p) for name, d, p in diffs if d >= 0.2]
    improved.sort(key=lambda x: -x[1])
    if improved:
        top = improved[:2]
        improved_str = "、".join([f"{name}+{d:.2f}pt" for name, d, _ in top])
        parts.append(f"特に{improved_str}が伸びている。")
    # 低下した軸（1つまで）
    decreased = [(name, d) for name, d, _ in diffs if d <= -0.1]
    if decreased:
        name, d = decreased[0]
        parts.append(f"{name}は{d:+.2f}pt。")
    # 横ばいの軸（伸び・低下以外で1つ、改善・低下が無い場合の補足）
    if not improved and not decreased:
        flat = [(name, d) for name, d, _ in diffs if -0.1 < d < 0.1]
        if flat:
            parts.append(f"{flat[0][0]}は横ばい。")
    # 締め（低下がなければバランス改善）
    if not decreased and (improved or total_diff > 0):
        parts.append("バランスが改善。")
    elif decreased:
        parts.append("伸びしろとして意識するとよい。")
    return " ".join(parts).strip()


def _generate_radar_description_follow_individual(
    pre_scores: Dict[str, float], post_scores: Optional[Dict[str, float]],
    follow_scores: Dict[str, float],
    pre_total: float, post_total: Optional[float], follow_total: float,
    skill_names: List[str], skill_keys: List[str]
) -> str:
    """個別用：1ヶ月後の傾向描写テキスト（数字列挙なし・傾向分析型）"""
    parts = []

    # 1. 全体傾向（直後比）
    if post_total is not None:
        diff_post = follow_total - post_total
        if diff_post >= 0.2:
            parts.append("直後からさらに定着が進んでいる。")
        elif diff_post >= 0.0:
            parts.append("直後の水準を維持・微向上している。")
        elif diff_post >= -0.2:
            parts.append("直後と比べほぼ横ばいで安定している。")
        else:
            parts.append("直後比でやや低下しているが、")
    else:
        diff_pre = follow_total - pre_total
        if diff_pre >= 0.3:
            parts.append("実施前から大きく向上している。")
        elif diff_pre > 0:
            parts.append("実施前から改善傾向にある。")
        else:
            parts.append("全体的に実施前と同水準。")

    # 2. 軸別の傾向（直後比）
    if post_scores:
        axis_diffs = []
        for i, key in enumerate(skill_keys):
            f_v = follow_scores.get(key, 0) or 0
            p_v = post_scores.get(key, 0) or 0
            axis_diffs.append((skill_names[i], f_v - p_v, f_v))

        improved_axes = sorted(
            [(name, d, f) for name, d, f in axis_diffs if d >= 0.2],
            key=lambda x: -x[1]
        )
        declined_axes = sorted(
            [(name, d, f) for name, d, f in axis_diffs if d <= -0.2],
            key=lambda x: x[1]
        )

        if improved_axes:
            names = "・".join(n for n, _, _ in improved_axes[:2])
            parts.append(f"特に{names}の定着が顕著。")
        if declined_axes:
            names = "・".join(n for n, _, _ in declined_axes[:1])
            parts.append(f"{names}は継続的な実践が必要。")

        # 変化が小さい場合は最高軸・最低軸で補足
        if not improved_axes and not declined_axes:
            highest_idx = max(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0) or 0)
            lowest_idx = min(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0) or 0)
            highest_score = follow_scores.get(skill_keys[highest_idx], 0) or 0
            lowest_score = follow_scores.get(skill_keys[lowest_idx], 0) or 0
            if highest_score >= 3.0:
                parts.append(f"{skill_names[highest_idx]}が強みとして定着している。")
            if lowest_score < 2.5:
                parts.append(f"{skill_names[lowest_idx]}に伸びしろが残る。")
    else:
        highest_idx = max(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0) or 0)
        lowest_idx = min(range(len(skill_keys)), key=lambda i: follow_scores.get(skill_keys[i], 0) or 0)
        highest_score = follow_scores.get(skill_keys[highest_idx], 0) or 0
        lowest_score = follow_scores.get(skill_keys[lowest_idx], 0) or 0
        if highest_score >= 3.0:
            parts.append(f"{skill_names[highest_idx]}が強みとして定着。")
        if lowest_score < 2.5:
            parts.append(f"{skill_names[lowest_idx]}は継続的な強化が課題。")

    return "".join(parts).strip()


def _extract_manager_comment_first_sentence(comment: str, max_len: int = 40) -> str:
    """上長コメントから最初の1文を自然な形で取り出す（句読点で区切り、長ければ省略）"""
    if not comment:
        return ''
    # 句読点で区切って最初の文を取得
    import re
    sentences = re.split(r'[。！？\n]', comment)
    first = sentences[0].strip() if sentences else comment.strip()
    if not first:
        first = comment.strip()
    if len(first) > max_len:
        first = first[:max_len - 1] + '…'
    return first


def _generate_analysis_summary(phase: int, person: Dict, pre_scores: Dict[str, float],
                                post_scores: Optional[Dict[str, float]], follow_scores: Optional[Dict[str, float]],
                                manager_comments: List[Dict], gap_data: Optional[Dict],
                                skill_names: List[str], skill_keys: List[str],
                                action_declaration: Optional[str] = None,
                                willingness: Optional[str] = None) -> str:
    """分析総評の文章を生成（傾向描写型・読みやすさ重視。19_個別分析総評・28要件準拠）"""
    from .analyzer import identify_strengths, identify_weaknesses

    pre_total = person.get('pre_total', 0)
    post_total = person.get('post_total')
    follow_total = person.get('follow_total')

    summary_parts = []

    # final_scores_for_analysis を先に決定（Section 1+2, 5 で共用）
    if phase == 2:
        final_scores_for_analysis = post_scores or pre_scores
    else:
        final_scores_for_analysis = follow_scores or post_scores or pre_scores

    # 1+2. 変容の理解 + 強みの認識（接続助詞でつなぎ1文に）
    change_clause = ""
    if phase == 3 and follow_total is not None:
        total_improvement = follow_total - pre_total
        if total_improvement > 0.5:
            change_clause = "研修効果が現場に着実に定着しており、"
        elif total_improvement > 0.1:
            change_clause = "実践を通じて着実な成長が見られ、"
        elif total_improvement >= -0.1:
            change_clause = "研修直後の水準を維持しながら実践を継続しており、"
        else:
            change_clause = "継続的な実践が次の伸びにつながっており、"
    elif phase >= 2 and post_total is not None:
        improvement = post_total - pre_total
        if improvement > 0.5:
            change_clause = "研修を通じて大きな成長が確認でき、"
        elif improvement > 0:
            change_clause = "研修を通じて着実な成長が見られ、"
        else:
            change_clause = "研修前後の変化は限定的でしたが学びの基盤は築かれており、"

    strength_clause = ""
    if final_scores_for_analysis:
        strengths = identify_strengths(final_scores_for_analysis)
        if strengths:
            strength = strengths[0]
            skill_name_to_key = {
                'リサーチ・分析力': 'research', '構想・コンセプト力': 'concept',
                '具体化・検証力': 'delivery', '伝達・構造化力': 'communication',
                '実現・ディレクション力': 'implementation'
            }
            strength_key = skill_name_to_key.get(strength['name'], 'research')
            pre_strength_score = pre_scores.get(strength_key, 0) if pre_scores else 0
            str_improvement = strength['score'] - pre_strength_score
            if str_improvement > 0.5:
                strength_clause = f"特に{strength['name']}が大きく伸びて強みとなっています。"
            else:
                strength_clause = f"特に{strength['name']}が強みとして定着しています。"

    if change_clause and strength_clause:
        summary_parts.append(change_clause + strength_clause)
    elif change_clause:
        summary_parts.append(change_clause.rstrip("、") + "。")
    elif strength_clause:
        summary_parts.append(strength_clause)

    # 3+4. 上長コメント + ギャップの示唆（「もあり、」でつなぎ1文に）- Phase3のみ
    manager_clause = ""
    gap_clause = ""

    if phase == 3 and manager_comments:
        comment = manager_comments[0]['comment']
        first_sentence = _extract_manager_comment_first_sentence(comment, max_len=40)
        if first_sentence:
            manager_clause = f"上長からは「{first_sentence}」という評価もあり、"

    if phase == 3 and gap_data:
        gap = gap_data.get('gap', {})
        if gap:
            large_gaps = [
                (skill_name, gap.get(skill_key, 0))
                for skill_key, skill_name in zip(skill_keys, skill_names)
                if gap.get(skill_key) is not None and abs(gap.get(skill_key, 0)) > 0.5
            ]
            if large_gaps:
                gap_desc = large_gaps[0]
                if gap_desc[1] > 0:
                    gap_clause = f"{gap_desc[0]}は自己評価が高く自信を持って取り組めています。"
                else:
                    gap_clause = f"{gap_desc[0]}は上長からも高く評価されており、さらなる発揮が期待されます。"

    if manager_clause and gap_clause:
        summary_parts.append(manager_clause + gap_clause)
    elif manager_clause:
        summary_parts.append(manager_clause.replace("という評価もあり、", "という評価があります。"))
    elif gap_clause:
        summary_parts.append(gap_clause)
    
    # 5. 改善点の明確化と次のアクション（19 R2/R4: Q17Aを必ず言及。空のときのみフォールバック。お勧めのみで終わらせない）
    if final_scores_for_analysis:
        weaknesses = identify_weaknesses(final_scores_for_analysis)
        if weaknesses:
            weakness = weaknesses[0]
            skill_name_to_key = {
                'リサーチ・分析力': 'research',
                '構想・コンセプト力': 'concept',
                '具体化・検証力': 'delivery',
                '伝達・構造化力': 'communication',
                '実現・ディレクション力': 'implementation'
            }
            weakness_key = skill_name_to_key.get(weakness['name'], 'research')
            pre_weakness_score = pre_scores.get(weakness_key, 0) if pre_scores else 0
            final_weakness_score = weakness['score']
            improvement = final_weakness_score - pre_weakness_score
            
            # アクション宣言（Q17A）があれば引用して弱みスキルと結びつける。空のときは19 R4フォールバック
            action_text = ""
            q17a = (action_declaration or "").strip()
            if q17a and q17a != "-":
                quote = q17a if len(q17a) <= 50 else q17a[:47] + "…"
                action_text = f"「{quote}」という宣言を、{weakness['name']}の向上につなげるとよいでしょう。"
            else:
                # R4: Q17A空時は短い定性一文（定型に頼りすぎない）
                short_fallbacks = {
                    'リサーチ・分析力': '日々のヒアリングや振り返りで「深掘り」を1つ意識すると、分析力の定着につながります。',
                    '構想・コンセプト力': '日々の打ち合わせで問いの立て方を少し変えるだけでも、コンセプト力の土台が育ちます。',
                    '具体化・検証力': '小さく試すサイクルを1回でも回すと、検証力の定着につながります。',
                    '伝達・構造化力': '報告や共有の場で「グループ分けして伝える」を一度試すと効果的です。',
                    '実現・ディレクション力': 'チームの場で役割を一つ決めて進める機会を設けると、実践につながります。'
                }
                action_text = short_fallbacks.get(weakness['name'], f"{weakness['name']}では、日々の業務で小さく試す機会を設けると伸びやすくなります。")
            
            # 具体的な行動提案: 各弱みスキルごとに5候補を用意し、対象者の強みに合う1つを選択（ポイントが上がりやすい提案を表示）
            # 候補は pairs_with: その強みを持つ人に特に有効な提案。Noneは汎用。
            CONCRETE_ACTION_CANDIDATES = {
                'リサーチ・分析力': [
                    {'text': '次のヒアリングや打ち合わせで「なぜ」を1つだけ深掘りする機会を現場で実施してみてください。', 'pairs_with': '構想・コンセプト力'},
                    {'text': '聞いた内容をメモしてグループ分けする整理の機会を、次の振り返りや報告の前に実施してみてください。', 'pairs_with': '伝達・構造化力'},
                    {'text': '小さな仮説を1つ決めて、関係者に「こうではないか」と確認する機会を現場で実施してみてください。', 'pairs_with': '具体化・検証力'},
                    {'text': 'チームの課題やニーズを1人に「なぜそう思うか」まで聞く機会を現場で実施してみてください。', 'pairs_with': '実現・ディレクション力'},
                    {'text': '次のヒアリングで「もう一歩だけ深掘りする質問」を1つ用意して実施してみてください。', 'pairs_with': None},
                ],
                '構想・コンセプト力': [
                    {'text': 'ヒアリングで得た事実から「だから〇〇ではないか」と仮説を1つ言語化する機会を現場で実施してみてください。', 'pairs_with': 'リサーチ・分析力'},
                    {'text': '次の打ち合わせで「理想の状態」を1つだけ言語化し、関係者と共有する機会を現場で実施してみてください。', 'pairs_with': '伝達・構造化力'},
                    {'text': 'プロトタイプや案の「意図している価値」を1文で説明する機会を現場で実施してみてください。', 'pairs_with': '具体化・検証力'},
                    {'text': 'チームのゴールを「〇〇なら成功」と1つ定義して共有する機会を現場で実施してみてください。', 'pairs_with': '実現・ディレクション力'},
                    {'text': 'アイデアや問いを1つメモして、次の打ち合わせで関係者と話す機会を現場で実施してみてください。', 'pairs_with': None},
                ],
                '具体化・検証力': [
                    {'text': 'ヒアリングで得た気づきを「こうすればよいのでは」と1つ形（メモや図）にして関係者に見せる機会を現場で実施してみてください。', 'pairs_with': 'リサーチ・分析力'},
                    {'text': '理想やアイデアを「まずこれだけ試す」と1つに絞って検証する機会を現場で実施してみてください。', 'pairs_with': '構想・コンセプト力'},
                    {'text': '伝えたい内容を1枚のメモや図にまとめて関係者に見せ、意見をもらう機会を現場で実施してみてください。', 'pairs_with': '伝達・構造化力'},
                    {'text': 'チームで「小さく試すこと」を1つ決めて、役割を分けて実施する機会を現場で実施してみてください。', 'pairs_with': '実現・ディレクション力'},
                    {'text': '小さな仮説を1つ決めてプロトタイプやメモを作り、関係者に見せて意見をもらう機会を現場で実施してみてください。', 'pairs_with': None},
                ],
                '伝達・構造化力': [
                    {'text': 'ヒアリングや聞いた内容をグループ分けしてから「3つにまとめて伝える」機会を次の報告で実施してみてください。', 'pairs_with': 'リサーチ・分析力'},
                    {'text': '理想やアイデアを「3点でまとめて伝える」機会を次の打ち合わせで実施してみてください。', 'pairs_with': '構想・コンセプト力'},
                    {'text': 'プロトタイプや案の意図を「3つに整理して伝える」機会を現場で実施してみてください。', 'pairs_with': '具体化・検証力'},
                    {'text': 'チームの役割や進捗を整理して「〇〇が〇〇」と簡潔に共有する機会を現場で実施してみてください。', 'pairs_with': '実現・ディレクション力'},
                    {'text': '次の報告や共有の場で「3つにまとめて伝える」、または情報をグループ分けしてから伝えることを現場で実施してみてください。', 'pairs_with': None},
                ],
                '実現・ディレクション力': [
                    {'text': 'ヒアリングで得たニーズを「誰が何をするか」に落とし、1つでも役割を決めて進める機会を現場で実施してみてください。', 'pairs_with': 'リサーチ・分析力'},
                    {'text': '打ち合わせで「誰が何をいつまでにやるか」を1つ決めて共有する機会を現場で実施してみてください。', 'pairs_with': '構想・コンセプト力'},
                    {'text': '検証したいことを「誰に何を依頼するか」に落とし、1つでも依頼する機会を現場で実施してみてください。', 'pairs_with': '具体化・検証力'},
                    {'text': '報告や共有の場で「次にやることと担当」を1つ決めて伝える機会を現場で実施してみてください。', 'pairs_with': '伝達・構造化力'},
                    {'text': '次の会議で進行役を担当する、またはチームの役割や進捗を一度確認する機会を現場で実施してみてください。', 'pairs_with': None},
                ],
            }
            candidates = CONCRETE_ACTION_CANDIDATES.get(weakness['name'])
            if not candidates:
                concrete = f"{weakness['name']}に関わる小さな一歩を1つ決めて、実際に現場で実施してみてください。"
            else:
                # 対象者の強みを取得し、その強みに合う候補を優先して選択（強みを活かす提案ほどポイントが上がりやすい想定）
                top_strength_name = None
                if final_scores_for_analysis:
                    strength_list = identify_strengths(final_scores_for_analysis)
                    if strength_list:
                        top_strength_name = strength_list[0]['name']
                selected = None
                for c in candidates:
                    if c.get('pairs_with') == top_strength_name:
                        selected = c['text']
                        break
                if not selected:
                    # 強みに合う候補がなければ汎用（pairs_with is None）を選ぶ
                    for c in candidates:
                        if c.get('pairs_with') is None:
                            selected = c['text']
                            break
                if not selected:
                    selected = candidates[0]['text']
                concrete = selected
            action_text = f"{action_text} 加えて、{concrete}"
            
            if improvement < 0.5:
                summary_parts.append(f"{weakness['name']}は引き続き成長の余地があります。{action_text}")
            else:
                summary_parts.append(f"{weakness['name']}は着実に伸びていますが、さらに定着させるために、{action_text}")
    
    # 文章を結合
    if summary_parts:
        return " ".join(summary_parts)
    else:
        # フォールバック: 従来の形式
        if final_scores_for_analysis:
            strengths = identify_strengths(final_scores_for_analysis)
            weaknesses = identify_weaknesses(final_scores_for_analysis)
            
            strength_text = ""
            if strengths:
                strength_text = f"{strengths[0]['name']}（{strengths[0]['score']:.2f}点）が特に高いスコアを示しています。"
            
            weakness_text = ""
            if weaknesses:
                weakness_text = f"{weaknesses[0]['name']}（{weaknesses[0]['score']:.2f}点）の向上が期待されます。"
            
            return f"{strength_text}{weakness_text}"
        else:
            return "-"


def generate_individual_report_markdown(phase: int, individual_progress_data: List[Dict],
                                       manager_comparison_data: Optional[List[Dict]] = None,
                                       post_data: Optional[List[Dict]] = None,
                                       project_name: str = "",
                                       project_report_dir: str = "") -> str:
    """個人別レポートMarkdownを生成"""
    from .analyzer import identify_strengths, identify_weaknesses
    
    now = datetime.now()
    date_str = now.strftime('%Y年%m月')
    
    md = f"# 生成レポート（個別）: {project_name}\n\n"
    md += f"**フェーズ**: Phase {phase}\n"
    md += f"**生成日**: {now.strftime('%Y/%m/%d')}\n\n"
    md += "---\n\n"
    
    # 参加者ごとにレポートを生成
    section_num = 1
    valid_participants = 0
    for person in individual_progress_data:
        # CSVの「氏名」（フォームの「あなたの氏名を入力してください。」等）を優先。空の場合のみメールの@前を利用
        name = (person.get('name') or '').strip()
        if not name:
            email = person.get('email', '')
            if email:
                name = email.split('@')[0] if '@' in email else email
            else:
                continue
        
        valid_participants += 1
        
        # スキル分析セクション（表示名はCSVの氏名を使用）
        md += f"## {section_num}. {name}様 スキル分析（レーダーチャート）\n\n"
        section_num += 1
        
        # 所属部署を表示（20_個別レポート_所属部署表示要件）
        dept = (person.get('department') or '').strip()
        dept_display = dept if dept else '-'
        md += f"**所属**: {dept_display}\n\n"
        
        # レーダーチャート画像（Phase別フォルダに格納・05_分析と出力仕様 2.2）
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        radar_filename = f"生成レポート（個別）_{project_name}_{safe_name}_Phase{phase}_レーダーチャート.png"
        personal_radar_dir = "Phase2_personal_radar_chart" if phase == 2 else "Phase3_personal_radar_chart"
        radar_path_in_md = f"{personal_radar_dir}/{radar_filename}"
        md += "### 可視化\n\n"
        # 画像パスを引用符で囲む（スペースを含むファイル名に対応）
        md += f"![{name}様 スキル定着度推移](<{radar_path_in_md}>)\n\n"
        
        # スコア推移表
        md += "### スコア推移表\n\n"
        pre_scores = person.get('pre', {})
        post_scores = person.get('post')
        follow_scores = person.get('follow')
        
        skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
        skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
        
        if phase == 2:
            md += "| 項目 | 実施前 | 直後 | 変化量(直後) |\n"
            md += "|------|--------|------|-------------|\n"
        else:  # phase == 3
            md += "| 項目 | 実施前 | 直後 | 1ヶ月後 | 変化量(直後) | 変化量(1ヶ月後) |\n"
            md += "|------|--------|------|---------|-------------|---------------|\n"
        
        for skill_name, skill_key in zip(skill_names, skill_keys):
            pre_val = pre_scores.get(skill_key, 0)
            post_val = post_scores.get(skill_key, 0) if post_scores else None
            follow_val = follow_scores.get(skill_key, 0) if follow_scores else None
            
            if phase == 2:
                diff1 = (post_val - pre_val) if post_val is not None else None
                post_val_str = f"{post_val:.2f}" if post_val is not None else "-"
                diff1_str = f"{diff1:+.2f}" if diff1 is not None else "-"
                md += f"| {skill_name} | {pre_val:.2f} | {post_val_str} | {diff1_str} |\n"
            else:  # phase == 3
                diff1 = (post_val - pre_val) if post_val is not None else None
                diff2 = (follow_val - (post_val if post_val is not None else pre_val)) if follow_val is not None else None
                post_val_str = f"{post_val:.2f}" if post_val is not None else "-"
                follow_val_str = f"{follow_val:.2f}" if follow_val is not None else "-"
                diff1_str = f"{diff1:+.2f}" if diff1 is not None else "-"
                diff2_str = f"{diff2:+.2f}" if diff2 is not None else "-"
                md += f"| {skill_name} | {pre_val:.2f} | {post_val_str} | {follow_val_str} | {diff1_str} | {diff2_str} |\n"
        
        # 総合スコア
        pre_total = person.get('pre_total', 0)
        post_total = person.get('post_total')
        follow_total = person.get('follow_total')
        
        if phase == 2:
            diff1_total = (post_total - pre_total) if post_total is not None else None
            post_total_str = f"{post_total:.2f}" if post_total is not None else "-"
            diff1_total_str = f"{diff1_total:+.2f}" if diff1_total is not None else "-"
            md += f"| 総合スコア | {pre_total:.2f} | {post_total_str} | {diff1_total_str} |\n\n"
        else:  # phase == 3
            diff1_total = (post_total - pre_total) if post_total is not None else None
            diff2_total = (follow_total - (post_total if post_total is not None else pre_total)) if follow_total is not None else None
            post_total_str = f"{post_total:.2f}" if post_total is not None else "-"
            follow_total_str = f"{follow_total:.2f}" if follow_total is not None else "-"
            diff1_total_str = f"{diff1_total:+.2f}" if diff1_total is not None else "-"
            diff2_total_str = f"{diff2_total:+.2f}" if diff2_total is not None else "-"
            md += f"| 総合スコア | {pre_total:.2f} | {post_total_str} | {follow_total_str} | {diff1_total_str} | {diff2_total_str} |\n\n"
        
        # レーダーチャートの説明
        md += "**レーダーチャートの説明**:\n"
        # 実施前の説明を生成
        pre_description = _generate_radar_description_pre(pre_scores, pre_total, skill_names, skill_keys)
        md += f"- **実施前（青線）**: {pre_description}\n"
        
        # 直後の説明を生成（個別用傾向分析）
        if phase >= 2 and post_scores and post_total is not None:
            post_description = _generate_radar_description_post_individual(
                pre_scores, post_scores, pre_total, post_total, skill_names, skill_keys
            )
            if post_description:
                md += f"- **直後（オレンジ線）**: {post_description}\n"
        
        # Phase3の場合、1ヶ月後の説明を追加（傾向描写型）
        if phase == 3 and follow_scores and follow_total is not None:
            follow_description = _generate_radar_description_follow_individual(
                pre_scores, post_scores, follow_scores,
                pre_total, post_total, follow_total,
                skill_names, skill_keys
            )
            md += f"- **1ヶ月後（緑線）**: {follow_description}\n"
        md += "\n"
        
        # 分析総評
        md += "### 分析総評\n\n"
        
        # 上長コメントとギャップ分析データを取得（Phase3のみ）
        manager_comments = []
        gap_data = None
        person_email = person.get('email', '')
        
        if phase == 3:
            # manager_comparison_dataから評価者情報を取得（複数評価者対応）
            if manager_comparison_data:
                for gap_person in manager_comparison_data:
                    if _email_local_match(gap_person.get('email', ''), person_email):
                        gap_data = gap_person
                        evaluators = gap_person.get('evaluators', [])
                        for evaluator in evaluators:
                            comment = evaluator.get('comment', '')
                            if comment and len(comment.strip()) > 10:
                                manager_comments.append({
                                    'name': evaluator.get('name', ''),
                                    'department': evaluator.get('department', ''),
                                    'comment': comment.strip()
                                })
                        break
        
        # 分析総評でアクション宣言（Q17A）を反映するため、先にQ16A・Q17Aを取得（19_個別分析総評）
        person_email = person.get('email', '')
        q16a_value = "-"
        q17a_value = "-"
        if phase >= 2 and post_data and person_email:
            for row in post_data:
                row_email = row.get('メールアドレス', '') or row.get('email', '') or row.get('Email', '')
                if _email_local_match(row_email, person_email):
                    q16a_raw = row.get('Q16A', '') or row.get('活用意欲', '') or row.get('Q16A: 活用意欲', '')
                    q16a_value = _convert_q16a_to_text(q16a_raw) if q16a_raw else "-"
                    q17a_value = row.get('Q17A', '') or row.get('アクション宣言', '') or row.get('Q17A: アクション宣言', '')
                    q17a_value = (q17a_value or "").strip() or "-"
                    break
        
        # 共通関数を使用して分析総評を生成（アクション宣言を渡す）
        summary_text = _generate_analysis_summary(
            phase, person, pre_scores, post_scores, follow_scores,
            manager_comments, gap_data, skill_names, skill_keys,
            action_declaration=q17a_value if q17a_value != "-" else None,
            willingness=q16a_value if q16a_value != "-" else None
        )
        
        if summary_text and summary_text != "-":
            md += f"{summary_text}\n\n"
        else:
            # フォールバック: 簡易版
            if phase == 2:
                final_scores_for_analysis = post_scores or pre_scores
            else:  # phase == 3
                final_scores_for_analysis = follow_scores or post_scores or pre_scores
            if final_scores_for_analysis:
                strengths = identify_strengths(final_scores_for_analysis)
                weaknesses = identify_weaknesses(final_scores_for_analysis)
                
                if strengths:
                    md += f"**強み**: {strengths[0]['name']}（{strengths[0]['score']:.2f}点）が特に高いスコアを示しています。\n\n"
                if weaknesses:
                    md += f"**改善の余地**: {weaknesses[0]['name']}（{weaknesses[0]['score']:.2f}点）の向上が期待されます。\n\n"
        
        # Phase2の場合、Q16A（活用意欲）とQ17A（アクション宣言）を追加（q16a_value, q17a_value は上で取得済み）
        if phase == 2:
            md += "\n### 活用意欲・アクション宣言\n\n"
            md += f"**活用意欲**: {q16a_value}\n\n"
            md += f"**アクション宣言**: {q17a_value}\n\n"
        
        # Phase 3の場合、ギャップ分析セクションを追加
        if phase == 3:
            # 該当する参加者のギャップ分析データを検索
            gap_data = None
            if manager_comparison_data:
                for gap_person in manager_comparison_data:
                    if _email_local_match(gap_person.get('email', ''), person.get('email', '')):
                        gap_data = gap_person
                        break
            
            md += f"## {section_num}. {name}様 定着度・ギャップ分析\n\n"
            section_num += 1
            
            if gap_data and gap_data.get('manager'):
                # ギャップ分析表
                md += "### ギャップ分析表\n\n"
                md += "| スキル軸 | 本人評価(1ヶ月後) | 上長評価 | ギャップ | 評価 |\n"
                md += "|---------|----------------|---------|---------|------|\n"
                
                self_scores = gap_data.get('self', {})
                manager_scores = gap_data.get('manager', {})
                gap = gap_data.get('gap', {})
                
                for skill_name, skill_key in zip(skill_names, skill_keys):
                    self_score = self_scores.get(skill_key, 0)
                    mgr_score = manager_scores.get(skill_key, 0)
                    gap_value = gap.get(skill_key, 0) if gap else 0
                    
                    # 評価を判定
                    if abs(gap_value) < 0.1:
                        evaluation = '一致'
                    elif gap_value > 0.3:
                        evaluation = '本人評価が上長評価を上回る'
                    elif gap_value > 0:
                        evaluation = '本人評価がやや高い'
                    elif gap_value < -0.3:
                        evaluation = '上長評価が本人評価を上回る'
                    else:
                        evaluation = '上長評価がやや高い'
                    
                    md += f"| {skill_name} | {self_score:.2f} | {mgr_score:.2f} | {gap_value:+.2f} | {evaluation} |\n"
                
                md += "\n"
                
                # ギャップ分析サマリー
                md += "### ギャップ分析サマリー\n\n"
                consistent_count = sum(1 for skill_key in skill_keys if abs(gap.get(skill_key, 0)) < 0.1)
                if consistent_count >= 4:
                    md += f"- {consistent_count}つのスキル軸で本人評価と上長評価が一致または近く、認識のギャップが小さい良好な状態です。\n\n"
                else:
                    md += "- 本人評価と上長評価のギャップを確認し、実践の質の向上を目指すことが推奨されます。\n\n"
                
                # 本人 vs 上長ギャップ
                md += "### 本人 vs 上長ギャップ\n\n"
                for skill_name, skill_key in zip(skill_names, skill_keys):
                    self_score = self_scores.get(skill_key, 0)
                    mgr_score = manager_scores.get(skill_key, 0)
                    gap_value = gap.get(skill_key, 0) if gap else 0
                    md += f"- **{skill_name}**: 本人 {self_score:.2f}点 vs 上長 {mgr_score:.2f}点（差: {gap_value:+.2f}pt）\n"
                md += "\n"
            else:
                md += "### ギャップ分析\n\n"
                md += "上長評価データがありません。ギャップ分析を実施するには、上長評価データが必要です。\n\n"
        
        md += "---\n\n"
    
    # 有効な参加者がいない場合のメッセージ
    if valid_participants == 0:
        md += "## 注意\n\n"
        md += "個人別データが取得できませんでした。参加者データに氏名が含まれていることを確認してください。\n\n"
    
    md += f"**レポート作成日**: {now.strftime('%Y/%m/%d')}  \n"
    md += f"**分析対象期間**: {date_str}  \n"
    md += f"**対象者数**: {valid_participants}名（全{len(individual_progress_data)}名中）\n"
    
    return md


def generate_individual_slide_content_markdown(phase: int, individual_progress_data: List[Dict],
                                              manager_comparison_data: Optional[List[Dict]] = None,
                                              manager_data: Optional[List[Dict]] = None,
                                              post_data: Optional[List[Dict]] = None,
                                              project_name: str = "",
                                              project_report_dir: str = "",
                                              follow_data: Optional[List[Dict]] = None) -> str:
    """個人別スライド挿入内容のマークダウンファイルを生成"""
    now = datetime.now()
    
    md = f"# スライド挿入内容（個別）: {project_name}\n\n"
    md += f"**生成日**: {now.strftime('%Y.%m.%d')}  \n"
    md += f"**フェーズ**: Phase {phase}\n\n"
    md += "## このファイルについて\n\n"
    md += "このファイルは、Googleスライドテンプレート（個人別用）に実際に挿入されるデータのみを記載したものです。\n"
    md += "各スライドのプレースホルダー（`{{XXX}}`）に対応するデータと、データソースを明記しています。\n"
    md += "データソースは生成レポート（個別）.mdのセクション経路（18_生成レポート統合確認と構成整理要件）に沿って記載しています。各参加者ごとにスライドが複製されます。\n\n"
    md += "---\n\n"
    
    # スライド0: 表紙（Phase1と同様のロジック）
    md += "## スライド0: 表紙\n\n"
    md += "**LAYOUT ID**: cover\n\n"
    md += "| プレースホルダー | データ内容 | データソース |\n"
    md += "|----------------|----------|------------|\n"
    md += f"| `{{{{Client}}}}` | {project_name} | プロジェクト設定 |\n"
    md += f"| `{{{{date}}}}` | {now.strftime('%Y.%m.%d')} | 生成日時 |\n\n"
    md += "---\n\n"
    
    skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
    skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    
    # スキル軸のマッピング: A=具体化・検証力(delivery), B=リサーチ・分析力(research), C=構想・コンセプト力(concept), D=伝達・構造化力(communication), E=実現・ディレクション力(implementation)
    skill_mapping = [
        ('delivery', 'A', '具体化・検証力'),
        ('research', 'B', 'リサーチ・分析力'),
        ('concept', 'C', '構想・コンセプト力'),
        ('communication', 'D', '伝達・構造化力'),
        ('implementation', 'E', '実現・ディレクション力')
    ]
    
    participant_num = 1
    for person in individual_progress_data:
        # CSVの「氏名」（フォームの「あなたの氏名を入力してください。」等）を優先。空の場合のみメールの@前を利用
        name = (person.get('name') or '').strip()
        if not name:
            email = person.get('email', '')
            if email:
                name = email.split('@')[0] if '@' in email else email
            else:
                continue
        
        md += f"## 参加者{participant_num}: {name}\n\n"
        participant_num += 1
        
        # スライド1: 個別スキル分析（レーダーチャート）
        md += "### スライド1: 個別スキル分析（レーダーチャート）\n\n"
        md += "**LAYOUT ID**: radar_chart_P\n\n"
        
        # レーダーチャート画像（Phase別フォルダに格納・05_分析と出力仕様 2.2）
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        radar_filename = f"生成レポート（個別）_{project_name}_{safe_name}_Phase{phase}_レーダーチャート.png"
        personal_radar_dir = "Phase2_personal_radar_chart" if phase == 2 else "Phase3_personal_radar_chart"
        radar_path_in_md = f"{personal_radar_dir}/{radar_filename}"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        md += f"| `{{{{graph_radar_chart_P}}}}` | レーダーチャート画像（手動挿入） | {radar_path_in_md} |\n"
        md += f"| `{{{{name_P}}}}` | {name} | 生成レポート（個別）.md（{name}様） |\n"
        dept_slide = (person.get('department') or '').strip()
        md += f"| `{{{{overall_name}}}}` | {dept_slide or '-'} | 直後.csv（所属部署列）または実施前.csv、生成レポート（個別）.md（所属） |\n\n"
        
        # スキル分析テーブル
        md += "### スキル分析テーブル（表内）\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        
        pre_scores = person.get('pre', {})
        post_scores = person.get('post')
        follow_scores = person.get('follow')
        
        # Phase3の場合、ギャップ分析データを取得
        gap_data = None
        person_email = person.get('email', '')
        if phase == 3 and manager_comparison_data:
            for gap_person in manager_comparison_data:
                if _email_local_match(gap_person.get('email', ''), person_email):
                    gap_data = gap_person
                    break
        
        for skill_key, letter, skill_name in skill_mapping:
            pre_val = pre_scores.get(skill_key, 0)
            post_val = post_scores.get(skill_key, 0) if post_scores else None
            follow_val = follow_scores.get(skill_key, 0) if follow_scores else None
            
            pre_val_str = f"{pre_val:.2f}" if pre_val else ""
            post_val_str = f"{post_val:.2f}" if post_val is not None else ""
            follow_val_str = f"{follow_val:.2f}" if follow_val is not None else "-"
            
            diff1 = (post_val - pre_val) if post_val is not None else None
            diff1_str = f"{diff1:+.2f}" if diff1 is not None else ""
            diff2 = (follow_val - (post_val if post_val is not None else pre_val)) if follow_val is not None else None
            diff2_str = f"{diff2:+.2f}" if diff2 is not None else "-"
            
            md += f"| `{{{{Cgr{letter}_1_P}}}}` | {pre_val_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 実施前） |\n"
            md += f"| `{{{{Cgr{letter}_2_P}}}}` | {post_val_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 直後） |\n"
            if phase == 3:
                md += f"| `{{{{Cgr{letter}_3_P}}}}` | {follow_val_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 1ヶ月後） |\n"
                md += f"| `{{{{Cgr{letter}_4_P}}}}` | {diff1_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 変化量(直後)） |\n"
                md += f"| `{{{{Cgr{letter}_5_P}}}}` | {diff2_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 変化量(1ヶ月後)） |\n"
                
                # Phase3の場合、上長評価とギャップを追加
                if gap_data:
                    manager_scores = gap_data.get('manager', {})
                    gap = gap_data.get('gap', {})
                    mgr_val = manager_scores.get(skill_key, 0) if manager_scores else 0
                    gap_val = gap.get(skill_key, 0) if gap else 0
                    
                    mgr_val_str = f"{mgr_val:.2f}" if mgr_val else "-"
                    gap_val_str = f"{gap_val:+.2f}" if gap_val is not None else "-"
                    
                    md += f"| `{{{{Ggr{letter}_2_P}}}}` | {mgr_val_str} | 生成レポート（個別）.md（{name}様 > ギャップ分析表 > {skill_name} > 上長評価） |\n"
                    md += f"| `{{{{Ggr{letter}_3_P}}}}` | {gap_val_str} | 生成レポート（個別）.md（{name}様 > ギャップ分析表 > {skill_name} > ギャップ） |\n"
                else:
                    # ギャップデータがない場合
                    md += f"| `{{{{Ggr{letter}_2_P}}}}` | - | 生成レポート（個別）.md（{name}様 > ギャップ分析表 > {skill_name} > 上長評価） |\n"
                    md += f"| `{{{{Ggr{letter}_3_P}}}}` | - | 生成レポート（個別）.md（{name}様 > ギャップ分析表 > {skill_name} > ギャップ） |\n"
            else:
                # Phase2の場合は1ヶ月後関連の項目は生成しない
                md += f"| `{{{{Cgr{letter}_4_P}}}}` | {diff1_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > {skill_name} > 変化量(直後)） |\n"
        
        # 総合スコア行（17_スキル分析テーブル_総合スコア行追加要件）
        pre_total = person.get('pre_total', 0)
        post_total = person.get('post_total')
        follow_total = person.get('follow_total')
        pre_total_str = f"{pre_total:.2f}" if pre_total else ""
        post_total_str = f"{post_total:.2f}" if post_total is not None else ""
        follow_total_str = f"{follow_total:.2f}" if follow_total is not None else "-"
        diff1_total = (post_total - pre_total) if post_total is not None else None
        diff1_total_str = f"{diff1_total:+.2f}" if diff1_total is not None else ""
        diff2_total = (follow_total - (post_total if post_total is not None else pre_total)) if follow_total is not None else None
        diff2_total_str = f"{diff2_total:+.2f}" if diff2_total is not None else "-"
        md += f"| `{{{{CgrF_1_P}}}}` | {pre_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 実施前） |\n"
        md += f"| `{{{{CgrF_2_P}}}}` | {post_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 直後） |\n"
        if phase == 3:
            md += f"| `{{{{CgrF_3_P}}}}` | {follow_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 1ヶ月後） |\n"
            md += f"| `{{{{CgrF_4_P}}}}` | {diff1_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 変化量(直後)） |\n"
            md += f"| `{{{{CgrF_5_P}}}}` | {diff2_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 変化量(1ヶ月後)） |\n"
        else:
            md += f"| `{{{{CgrF_3_P}}}}` | - | Phase2のため未使用 |\n"
            md += f"| `{{{{CgrF_4_P}}}}` | {diff1_total_str} | 生成レポート（個別）.md（{name}様 > スコア推移表 > 総合スコア > 変化量(直後)） |\n"
            md += f"| `{{{{CgrF_5_P}}}}` | - | Phase2のため未使用 |\n"
        
        # レーダーチャートの説明
        md += "\n### レーダーチャートの説明\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        
        skill_names = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
        skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
        
        pre_scores = person.get('pre', {})
        post_scores = person.get('post')
        follow_scores = person.get('follow')
        pre_total = person.get('pre_total', 0)
        post_total = person.get('post_total')
        follow_total = person.get('follow_total')
        
        # 実施前（青線）の説明 - 共通関数を使用（表セルは1行に収めるため改行除去）
        pre_description = _generate_radar_description_pre(pre_scores, pre_total, skill_names, skill_keys)
        md += f"| `{{{{C_block_2_1_body_P}}}}` | {_cell_safe(pre_description)} | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 実施前） |\n"
        
        # 直後（オレンジ線）の説明 - 個別用傾向分析（24_個別レーダーチャート説明_傾向分析要件）
        if phase >= 2 and post_scores and post_total is not None:
            post_description = _generate_radar_description_post_individual(
                pre_scores, post_scores, pre_total, post_total, skill_names, skill_keys
            )
            if post_description:
                md += f"| `{{{{C_block_2_2_body_P}}}}` | {_cell_safe(post_description)} | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 直後） |\n"
            else:
                md += f"| `{{{{C_block_2_2_body_P}}}}` | - | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 直後） |\n"
        else:
            md += f"| `{{{{C_block_2_2_body_P}}}}` | - | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 直後） |\n"
        
        # Phase3の場合のみ1ヶ月後の説明を生成
        if phase == 3 and follow_scores and follow_total is not None:
            follow_description = _generate_radar_description_follow_individual(
                pre_scores, post_scores, follow_scores,
                pre_total, post_total, follow_total,
                skill_names, skill_keys
            )
            md += f"| `{{{{C_block_2_3_body_P}}}}` | {_cell_safe(follow_description)} | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 1ヶ月後） |\n"
        elif phase == 3:
            # Phase3だが1ヶ月後データがない場合（未回答者）は「-」で出力
            md += f"| `{{{{C_block_2_3_body_P}}}}` | - | 生成レポート（個別）.md（{name}様 > レーダーチャートの説明 > 1ヶ月後） |\n"
        # Phase2の場合は1ヶ月後関連の項目は生成しない
        
        # 分析総評
        md += "\n### 分析総評\n\n"
        md += "| プレースホルダー | データ内容 | データソース |\n"
        md += "|----------------|----------|------------|\n"
        
        from .analyzer import identify_strengths, identify_weaknesses
        
        # 上長コメントを取得（複数評価者対応）- Phase3のみ
        manager_comments = []
        person_email = person.get('email', '')
        
        # Phase3の場合のみ上長コメントを取得
        if phase == 3:
            # manager_comparison_dataから評価者情報を取得（複数評価者対応）
            if manager_comparison_data:
                for gap_person in manager_comparison_data:
                    if gap_person.get('email') == person_email:
                        evaluators = gap_person.get('evaluators', [])
                        for evaluator in evaluators:
                            comment = evaluator.get('comment', '')
                            if comment and len(comment.strip()) > 10:
                                manager_comments.append({
                                    'name': evaluator.get('name', ''),
                                    'department': evaluator.get('department', ''),
                                    'comment': comment.strip()
                                })
                        break
            
            # 後方互換性：manager_dataから直接取得（evaluators情報がない場合）
            if not manager_comments and manager_data and person_email:
                for manager_row in manager_data:
                    target_email = manager_row.get('対象者メールアドレス', '') or manager_row.get('メールアドレス', '')
                    if _email_local_match(target_email, person_email):
                        comment = manager_row.get('M7', '') or manager_row.get('上長コメント', '') or manager_row.get('コメント', '')
                        if comment and len(comment.strip()) > 10:
                            manager_comments.append({
                                'name': manager_row.get('上長氏名', '') or manager_row.get('氏名', ''),
                                'department': manager_row.get('上長部署', '') or manager_row.get('所属部署', ''),
                                'comment': comment.strip()
                            })
                        break
        
        # ギャップ分析データを取得（Phase3の場合）
        gap_data = None
        if phase == 3 and manager_comparison_data:
            for gap_person in manager_comparison_data:
                if gap_person.get('email') == person_email:
                    gap_data = gap_person
                    break
        
        # 分析総評でアクション宣言を反映するため、Q16A・Q17Aを先に取得（19_個別分析総評）
        q16a_value = "-"
        q17a_value = "-"
        if phase >= 2 and post_data and person_email:
            for row in post_data:
                row_email = row.get('メールアドレス', '') or row.get('email', '') or row.get('Email', '')
                if _email_local_match(row_email, person_email):
                    q16a_raw = row.get('Q16A', '') or row.get('活用意欲', '') or row.get('Q16A: 活用意欲', '')
                    q16a_value = _convert_q16a_to_text(q16a_raw) if q16a_raw else "-"
                    q17a_value = row.get('Q17A', '') or row.get('アクション宣言', '') or row.get('Q17A: アクション宣言', '')
                    q17a_value = (q17a_value or "").strip() or "-"
                    break
        
        # 共通関数を使用して分析総評を生成（アクション宣言を渡す）
        summary_text = _generate_analysis_summary(
            phase, person, pre_scores, post_scores, follow_scores,
            manager_comments, gap_data, skill_names, skill_keys,
            action_declaration=q17a_value if q17a_value != "-" else None,
            willingness=q16a_value if q16a_value != "-" else None
        )
        
        if summary_text and summary_text != "-":
            md += f"| `{{{{C_block_1_body_P}}}}` | {_cell_safe(summary_text)} | 生成レポート（個別）.md（{name}様 > 分析総評） |\n"
        else:
            md += f"| `{{{{C_block_1_body_P}}}}` | - | 生成レポート（個別）.md（{name}様 > 分析総評） |\n"
        
        # Phase2の場合、Q16A（活用意欲）とQ17A（アクション宣言）を追加（上で取得済み）（表セルは1行に収めるため改行除去）
        if phase == 2:
            md += "\n### 活用意欲・アクション宣言\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{C_block_3_1_body_P}}}}` | {_cell_safe(q16a_value)} | 生成レポート（個別）.md（{name}様 > 活用意欲・アクション宣言）、直後.csv（{name}様 > Q16A: 活用意欲） |\n"
            md += f"| `{{{{C_block_3_2_body_P}}}}` | {_cell_safe(q17a_value)} | 生成レポート（個別）.md（{name}様 > 活用意欲・アクション宣言）、直後.csv（{name}様 > Q17A: アクション宣言） |\n"

        # Phase3の場合、Q17B（1ヶ月後の実践エピソード）とM7（上長コメント）を追加
        elif phase == 3:
            # Q17B: 1ヶ月後アンケートから取得
            q17b_value = "-"
            if follow_data and person_email:
                for row in follow_data:
                    row_email = row.get('メールアドレス', '') or row.get('email', '') or row.get('Email', '')
                    if _email_local_match(row_email, person_email):
                        q17b_value = (row.get('Q17B', '') or '').strip() or "-"
                        break
            # M7: 上長コメント（既に取得済みのmanager_commentsから使用）
            m7_value = manager_comments[0].get('comment', '') if manager_comments else "-"
            m7_value = m7_value or "-"

            md += "\n### 実践エピソード・上長コメント\n\n"
            md += "| プレースホルダー | データ内容 | データソース |\n"
            md += "|----------------|----------|------------|\n"
            md += f"| `{{{{C_block_3_1_body_P}}}}` | {_cell_safe(q17b_value)} | 1ヶ月後.csv（{name}様 > Q17B: 実践エピソード） |\n"
            md += f"| `{{{{C_block_3_2_body_P}}}}` | {_cell_safe(m7_value)} | 上長1ヶ月後.csv（{name}様 > M7: 上長コメント） |\n"
        
        # Phase3の場合、ギャップ分析セクションは削除（個人分析結果は1ページで完結）
        # gap_analysis_Pセクションは生成しない
        
        # 評価者コメントセクション（複数評価者対応）
        if phase == 3 and manager_comments:
            md += f"\n### 上長からの評価コメント\n\n"
            for evaluator_comment in manager_comments:
                evaluator_name = evaluator_comment.get('name', '')
                evaluator_dept = evaluator_comment.get('department', '')
                comment = evaluator_comment.get('comment', '')
                
                if evaluator_name:
                    if evaluator_dept:
                        md += f"**{evaluator_name}（{evaluator_dept}）**\n\n"
                    else:
                        md += f"**{evaluator_name}**\n\n"
                md += f"{comment}\n\n"
        
        md += "\n---\n\n"
    
    md += f"**生成日時**: {now.strftime('%Y/%m/%d %H:%M:%S')}\n"
    
    return md
