"""
GASコード生成モジュール
生成されたレポートデータからGoogleスライド用のGASコードを生成
レポートデータをGASコード内に直接埋め込む
"""
import os
import csv
import base64
import json
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 安全なprint関数（BrokenPipeErrorを無視）
def safe_print(*args, **kwargs):
    """安全なprint関数（BrokenPipeErrorを無視）"""
    try:
        print(*args, **kwargs, file=sys.stderr)
    except (BrokenPipeError, OSError):
        # パイプが閉じられている場合は無視
        pass


def parse_report_markdown(report_path: str) -> Dict:
    """Markdownレポートを解析してデータを抽出"""
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"レポートファイルが見つかりません: {report_path}")
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"レポートファイルの読み込みに失敗しました: {report_path}, エラー: {e}")
    
    data = {
        'clientName': '',
        'project': '',
        'reportDate': '',
        'period': '',
        'respondents': '',
        'phase': '',
        'overallComment': '',
        'goodPoints': '',
        'weakPoints': '',
        'skillSummary': '',
        'skillTrends': ''
    }
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # プロジェクト名
        if line.startswith('# プロジェクト:'):
            data['project'] = line.replace('# プロジェクト:', '').strip()
            data['clientName'] = data['project']
        
        # 日付
        if '2025.' in line or '2024.' in line or '2026.' in line:
            import re
            date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
            if date_match:
                data['reportDate'] = date_match.group(1)
        
        # 期間（**対象期間**: や 対象期間: の両方に対応）
        if '対象期間:' in line or '期間:' in line:
            period_match = line.split(':', 1)
            if len(period_match) > 1:
                period_value = period_match[1].strip()
                # Markdownの**形式を除去
                period_value = period_value.replace('**', '').replace('  ', ' ').strip()
                if period_value:
                    data['period'] = period_value
        
        # 回答者数（**回答者数**: や 回答者数: の両方に対応）
        if '回答者数:' in line:
            respondents_match = line.split(':', 1)
            if len(respondents_match) > 1:
                respondents_value = respondents_match[1].strip()
                # Markdownの**形式を除去
                respondents_value = respondents_value.replace('**', '').replace('名', '').replace('  ', ' ').strip()
                if respondents_value:
                    data['respondents'] = respondents_value
        
        # フェーズ
        if 'Phase' in line or 'フェーズ' in line:
            import re
            phase_match = re.search(r'Phase\s*(\d+)', line, re.IGNORECASE)
            if phase_match:
                data['phase'] = f"Phase {phase_match.group(1)}"
        
        # 総評コメント
        if line == '### 総評コメント':
            # 次のセクションまでを取得
            comment_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line.startswith('##') or next_line.startswith('###'):
                    break
                if next_line and not next_line.startswith('**'):
                    # Markdownのリスト記号を除去
                    cleaned_line = next_line.lstrip('- ').lstrip('* ')
                    if cleaned_line:
                        comment_lines.append(cleaned_line)
            data['overallComment'] = '\n'.join(comment_lines)
        
        # 強み
        if line == '**強み**:':
            good_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line.startswith('**弱み**') or next_line.startswith('##'):
                    break
                if next_line and not next_line.startswith('**'):
                    # Markdownのフォーマットを除去
                    cleaned_line = next_line
                    # **xxx** 形式を除去
                    import re
                    cleaned_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_line)
                    # リスト記号を除去
                    cleaned_line = cleaned_line.lstrip('- ').lstrip('* ')
                    if cleaned_line:
                        good_lines.append(cleaned_line)
            data['goodPoints'] = '\n'.join(good_lines)
        
        # 弱み
        if line == '**弱み**:':
            weak_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line.startswith('##') or next_line.startswith('---'):
                    break
                if next_line and not next_line.startswith('**'):
                    # Markdownのフォーマットを除去
                    cleaned_line = next_line
                    # **xxx** 形式を除去
                    import re
                    cleaned_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_line)
                    # リスト記号を除去
                    cleaned_line = cleaned_line.lstrip('- ').lstrip('* ')
                    if cleaned_line:
                        weak_lines.append(cleaned_line)
            data['weakPoints'] = '\n'.join(weak_lines)
        
        # スキル分析（分析総評を取得）
        if line == '### 分析総評':
            skill_lines = []
            for j in range(i + 1, min(i + 30, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('##') or next_line.startswith('###') or next_line.startswith('---'):
                    break
                if next_line:
                    # Markdownのフォーマットを除去
                    cleaned_line = next_line
                    import re
                    cleaned_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_line)
                    cleaned_line = cleaned_line.lstrip('- ').lstrip('* ')
                    if cleaned_line:
                        skill_lines.append(cleaned_line)
            if skill_lines:
                data['skillSummary'] = '\n'.join(skill_lines)
        
        # スキル分析（後方互換性のため、全社スキル分析セクションも確認）
        if line == '## 2. 全社スキル分析（レーダーチャート）' or line == '## 2. 全社スキル分析':
            if not data['skillSummary']:
                skill_lines = []
                for j in range(i + 1, min(i + 30, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if next_line.startswith('### 分析総評'):
                        # 分析総評を取得
                        for k in range(j + 1, min(j + 20, len(lines))):
                            summary_line = lines[k].strip()
                            if summary_line.startswith('##') or summary_line.startswith('###') or summary_line.startswith('---'):
                                break
                            if summary_line:
                                cleaned_line = summary_line
                                import re
                                cleaned_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_line)
                                if cleaned_line:
                                    skill_lines.append(cleaned_line)
                        break
                if skill_lines:
                    data['skillSummary'] = '\n'.join(skill_lines)
        
        # ギャップ分析（Phase 3）
        if line == '## 4. 定着度・ギャップ分析' or '定着度・ギャップ分析' in line:
            gap_lines = []
            in_voice_section = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                # 次のセクション（## 5.）またはレポート作成日まで
                if next_line.startswith('## 5.') or next_line.startswith('**レポート作成日') or (j > i + 150):
                    break
                # 現場の声セクションに到達したら別途処理
                if next_line == '### 現場の声':
                    in_voice_section = True
                    # 現場の声セクションから成功事例と障壁を抽出
                    # 成功事例を抽出
                    for k in range(j + 1, min(j + 100, len(lines))):
                        if lines[k].strip() == '#### 実践の成功事例':
                            success_lines = []
                            for m in range(k + 1, min(k + 30, len(lines))):
                                next_line2 = lines[m].strip()
                                if next_line2.startswith('####') or next_line2.startswith('##') or next_line2.startswith('---'):
                                    break
                                if next_line2 and next_line2.startswith('>'):
                                    # > を除去して引用符も除去
                                    cleaned = next_line2.lstrip('> ').strip().strip('"').strip()
                                    if cleaned:
                                        success_lines.append(cleaned)
                            if success_lines:
                                data['successCases'] = '\n\n'.join(success_lines)
                            break
                    
                    # 障壁・課題を抽出
                    for k in range(j + 1, min(j + 100, len(lines))):
                        if '実践の課題・障壁' in lines[k].strip() or '課題・障壁' in lines[k].strip():
                            barrier_lines = []
                            for m in range(k + 1, min(k + 30, len(lines))):
                                next_line2 = lines[m].strip()
                                if next_line2.startswith('####') or next_line2.startswith('##') or next_line2.startswith('---'):
                                    break
                                if next_line2 and next_line2.startswith('>'):
                                    # > を除去して引用符も除去
                                    cleaned = next_line2.lstrip('> ').strip().strip('"').strip()
                                    if cleaned:
                                        barrier_lines.append(cleaned)
                            if barrier_lines:
                                data['barriers'] = '\n\n'.join(barrier_lines)
                            break
                    continue
                # 現場の声セクション以外の内容をギャップ分析として記録
                if not in_voice_section and next_line:
                    gap_lines.append(next_line)
            if gap_lines:
                data['gapAnalysis'] = '\n'.join(gap_lines[:80])  # 最初の80行まで
        
        # 推奨プログラム（Phase 3）
        if line == '## 5. 推奨プログラム提案' or '推奨プログラム' in line:
            rec_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line.startswith('##') or next_line.startswith('---') or next_line.startswith('**レポート作成日'):
                    break
                if next_line:
                    rec_lines.append(next_line)
            if rec_lines:
                data['recommendation'] = '\n'.join(rec_lines[:150])  # 最初の150行まで
    
    # 日付が取得できなかった場合
    if not data['reportDate']:
        now = datetime.now()
        data['reportDate'] = now.strftime('%Y.%m.%d')
    
    return data


def parse_csv_file(csv_path: str) -> List[Dict]:
    """CSVファイルを解析"""
    data = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        safe_print(f"CSV解析エラー: {e}")
    return data


# 画像のBase64エンコードは使用しない（コードが長くなりすぎるため）


def parse_placeholder_mapping_from_markdown(slide_content_path: str) -> Dict[str, str]:
    """
    スライド挿入内容Markdownから、プレースホルダーIDとデータ内容のマッピングを直接抽出
    
    Returns:
        Dict[プレースホルダーID, データ内容]
        例: {'{{S_score_1}}': '3.57点', '{{S_score_2}}': '+0.69pt（vs 実施前）', ...}
    """
    placeholder_map = {}
    
    if not os.path.exists(slide_content_path):
        return placeholder_map
    
    try:
        with open(slide_content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        import re
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # テーブル行を検出（`{{XXX}}`を含む行）
            if '`{{' in line and '}}`' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    # プレースホルダー列（インデックス1）からIDを抽出
                    placeholder_cell = parts[1].strip()
                    # データ内容列（インデックス2）から値を取得
                    data_value = parts[2].strip()
                    
                    # プレースホルダーIDを抽出（`{{XXX}}`の形式）
                    match = re.search(r'`\{\{([^}]+)\}\}`', placeholder_cell)
                    if match:
                        placeholder_id = '{{' + match.group(1) + '}}'
                        # データ内容列ヘッダー以外は追加（空・'-'も追加して置換する。17 CgrF_3/CgrF_5等）
                        if data_value != 'データ内容':
                            # 組織別のプレースホルダーは後で個別に処理するため、最初のもののみ記録
                            if placeholder_id.startswith(('{{O_', '{{Ogr', '{{Ork')) and placeholder_id in placeholder_map:
                                # 組織別のプレースホルダーは既に存在する場合はスキップ（最初の組織の情報のみ保持）
                                continue
                            placeholder_map[placeholder_id] = data_value if data_value else ''
                            if data_value and len(data_value) > 50:
                                safe_print(f"  抽出: {placeholder_id} = {data_value[:50]}...")
                            elif data_value:
                                safe_print(f"  抽出: {placeholder_id} = {data_value}")
    
    except Exception as e:
        safe_print(f"プレースホルダーマッピング抽出エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    return placeholder_map


def parse_organization_data_from_markdown(slide_content_path: str) -> List[Dict[str, str]]:
    """
    スライド挿入内容Markdownから組織別の情報を抽出
    
    Returns:
        List[Dict]: 各組織の情報のリスト
        例: [
            {'name': '営業部', 'O_overall_score_name': '営業部', 'O_score': '3.13', ...},
            {'name': '企画部', 'O_overall_score_name': '企画部', 'O_score': '3.84', ...},
            ...
        ]
    """
    org_data_list = []
    
    if not os.path.exists(slide_content_path):
        return org_data_list
    
    try:
        with open(slide_content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        import re
        current_org = None
        current_org_data = {}
        in_org_section = False  # 組織別分析セクション内かどうか
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # 組織別分析セクションの開始を検出
            if '## スライド3: 組織別分析' in line_stripped or '## スライド3' in line_stripped:
                in_org_section = True
                continue
            
            # 組織別分析セクションが終了したら処理を停止
            if in_org_section and line_stripped.startswith('## スライド') and '組織別分析' not in line_stripped:
                in_org_section = False
                # 最後の組織のデータを保存
                if current_org and current_org_data:
                    current_org_data['name'] = current_org
                    org_data_list.append(current_org_data.copy())
                    current_org = None
                    current_org_data = {}
                continue
            
            # 組織別分析セクション内でのみ組織名を検出（### 営業部、### 企画部、### コーポレートなど）
            if in_org_section and line_stripped.startswith('### ') and not line_stripped.startswith('### スライド'):
                org_name_match = re.search(r'^###\s+(.+)$', line_stripped)
                if org_name_match:
                    org_name = org_name_match.group(1).strip()
                    # 組織名として有効なもの（部署名のパターン）
                    # 「営業部」「企画部」「開発部」「コーポレート」などの形式を想定
                    # 「データソース」などのテーブルヘッダー行を除外
                    if org_name and org_name not in ['データ内容', 'データソース', 'プレースホルダー']:
                        # 前の組織のデータを保存
                        if current_org and current_org_data:
                            current_org_data['name'] = current_org
                            org_data_list.append(current_org_data.copy())
                        
                        # 新しい組織の開始
                        current_org = org_name
                        current_org_data = {}
                        safe_print(f"  組織を検出: {current_org}")
                        continue
            
            # テーブル行を検出（組織別のプレースホルダーを含む行。O_, Ogr*, Ork* をすべて拾う）
            if current_org and '`{{O' in line and '}}`' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    # プレースホルダー列（インデックス1）からIDを抽出
                    placeholder_cell = parts[1].strip()
                    # データ内容列（インデックス2）から値を取得
                    data_value = parts[2].strip()
                    
                    # プレースホルダーIDを抽出（`{{XXX}}`の形式）
                    match = re.search(r'`\{\{([^}]+)\}\}`', placeholder_cell)
                    if match:
                        placeholder_id = match.group(1)  # {{}}なし
                        # データ内容が「データ内容」列ヘッダーでなければ追加（値が'-'や空でも追加）
                        if data_value != 'データ内容':
                            current_org_data[placeholder_id] = data_value if data_value else ''
                            if len(data_value) > 50:
                                safe_print(f"    {placeholder_id} = {data_value[:50]}...")
                            else:
                                safe_print(f"    {placeholder_id} = {data_value}")
        
        # 最後の組織のデータを保存
        if current_org and current_org_data:
            current_org_data['name'] = current_org
            org_data_list.append(current_org_data.copy())
        
        safe_print(f"組織別データ抽出完了: {len(org_data_list)}組織")
    
    except Exception as e:
        safe_print(f"組織別データ抽出エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    return org_data_list


def parse_slide_content_markdown(slide_content_path: str) -> Dict:
    """スライド挿入内容Markdownから全ての必要なデータを抽出"""
    data = {
        'clientName': '',
        'reportDate': '',
        'period': '',
        'respondents': '',
        # スライド1: エグゼクティブサマリー
        'S_score_1': '',
        'S_score_2': '',
        'S_block_1_body': '',
        'S_block_2_body': '',
        'S_block_3_body': '',
        # スライド2: スキル分析
        'C_block_1_body': '',
        'C_block_2_1_body': '',  # 実施前（青線）の説明
        'C_block_2_2_body': '',  # 直後（オレンジ線）の説明
        'C_block_2_3_body': '',  # 1ヶ月後（緑線）の説明
        'skill_scores': {},  # {'CgrA_1': '', 'CgrA_2': '', ...}
        # スライド5: 成功事例
        'success_cases': [],  # [{'name': '', 'body': ''}, ...]
        # スライド6: 課題・障壁
        'barriers': [],  # [{'name': '', 'body': ''}, ...]
        # スライド7: 推奨プログラム
        'recommendation': {
            'title': '',
            'issues': '',
            'reason': '',
            'effect': ''
        },
        # スライド8: 満足度分析
        'satisfaction': {
            'period': '',
            'respondents': '',
            'score_1': '',
            'score_2': '',
            'score_3': '',
            'M_block_1_body': ''
        },
        # スライド9: 実践頻度分析
        'F_block_1_body': ''
    }
    
    if not os.path.exists(slide_content_path):
        return data
    
    try:
        with open(slide_content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        import re
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # プロジェクト名と日付の抽出（スライド0）
            if '`{{Client}}`' in line:
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        value = parts[2].strip()
                        if value and value != 'データ内容':
                            data['clientName'] = value
                if not data['clientName'] and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line and '---' not in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            value = parts[2].strip()
                            if value and value != 'データ内容':
                                data['clientName'] = value
            
            if '`{{date}}`' in line:
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        value = parts[2].strip()
                        if value and value != 'データ内容':
                            data['reportDate'] = value
                if not data['reportDate'] and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line and '---' not in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            value = parts[2].strip()
                            if value and value != 'データ内容':
                                data['reportDate'] = value
            
            # period_1のデータ内容を抽出（テーブル形式）
            if '`{{period_1}}`' in line or 'period_1' in line:
                # 同じ行からデータ内容を抽出
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    # プレースホルダー列、データ内容列、データソース列の順
                    if len(parts) >= 3:
                        # データ内容列を取得（インデックス2）
                        period_value = parts[2].strip()
                        if period_value and period_value != 'データ内容':
                            data['period'] = period_value
                # 次の行を確認（テーブルの次の行にデータがある場合）
                if not data['period'] and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line and '---' not in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            period_value = parts[2].strip()
                            if period_value and period_value != 'データ内容':
                                data['period'] = period_value
            
            # respondents_1のデータ内容を抽出（テーブル形式）
            if '`{{respondents_1}}`' in line or 'respondents_1' in line:
                # 同じ行からデータ内容を抽出
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    # プレースホルダー列、データ内容列、データソース列の順
                    if len(parts) >= 3:
                        # データ内容列を取得（インデックス2）
                        respondents_value = parts[2].strip()
                        if respondents_value and respondents_value != 'データ内容':
                            data['respondents'] = respondents_value
                # 次の行を確認（テーブルの次の行にデータがある場合）
                if not data['respondents'] and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line and '---' not in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            respondents_value = parts[2].strip()
                            if respondents_value and respondents_value != 'データ内容':
                                data['respondents'] = respondents_value
            
            # 成功事例の抽出（スライド5）
            if '## スライド5: 成功事例' in line or 'スライド5: 成功事例' in line:
                # 次のテーブルからデータを抽出
                import re
                for j in range(i + 1, min(i + 50, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{T_block_' in next_line and '}}`' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                # T_block_X_name または T_block_X_body を判定
                                match = re.search(r'T_block_(\d+)_(name|body)', placeholder)
                                if match:
                                    idx = int(match.group(1))
                                    field = match.group(2)
                                    while len(data['success_cases']) < idx:
                                        data['success_cases'].append({'name': '', 'body': ''})
                                    if field == 'name':
                                        data['success_cases'][idx - 1]['name'] = value
                                    elif field == 'body':
                                        data['success_cases'][idx - 1]['body'] = value
            
            # 課題・障壁の抽出（スライド6）
            if '## スライド6: 課題・障壁' in line or 'スライド6: 課題・障壁' in line:
                # 次のテーブルからデータを抽出
                import re
                for j in range(i + 1, min(i + 50, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{I_block_' in next_line and '}}`' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                # I_block_X_name または I_block_X_body を判定
                                match = re.search(r'I_block_(\d+)_(name|body)', placeholder)
                                if match:
                                    idx = int(match.group(1))
                                    field = match.group(2)
                                    while len(data['barriers']) < idx:
                                        data['barriers'].append({'name': '', 'body': ''})
                                    if field == 'name':
                                        data['barriers'][idx - 1]['name'] = value
                                    elif field == 'body':
                                        data['barriers'][idx - 1]['body'] = value
            
            # スライド1: エグゼクティブサマリーの抽出
            if '## スライド1: エグゼクティブサマリー' in line or 'スライド1: エグゼクティブサマリー' in line:
                for j in range(i + 1, min(i + 50, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{' in next_line and '}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                if 'S_score_1}}`' in placeholder:
                                    data['S_score_1'] = value
                                elif 'S_score_2}}`' in placeholder:
                                    data['S_score_2'] = value
                                elif 'S_block_1_body}}`' in placeholder:
                                    data['S_block_1_body'] = value
                                elif 'S_block_2_body}}`' in placeholder:
                                    data['S_block_2_body'] = value
                                elif 'S_block_3_body}}`' in placeholder:
                                    data['S_block_3_body'] = value
            
            # スライド2: スキル分析の抽出
            if '## スライド2: スキル分析' in line or 'スライド2: スキル分析' in line:
                in_skill_table = False
                in_analysis_summary = False
                in_radar_description = False
                for j in range(i + 1, min(i + 150, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    # レーダーチャートの説明セクションの検出
                    if '### レーダーチャートの説明' in next_line:
                        in_radar_description = True
                        in_skill_table = False
                        in_analysis_summary = False
                        continue
                    # スキル分析テーブルセクションの検出
                    if '### スキル分析テーブル' in next_line or 'スキル分析テーブル（表内）' in next_line:
                        in_skill_table = True
                        in_analysis_summary = False
                        in_radar_description = False
                        continue
                    # 分析総評セクションの検出
                    if '### 分析総評' in next_line:
                        in_skill_table = False
                        in_analysis_summary = True
                        in_radar_description = False
                        continue
                    # スキル分析テーブルからCgrX_Yを抽出
                    if in_skill_table and '`{{Cgr' in next_line and '}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value != 'データ内容':
                                # CgrA_1〜CgrE_5 および CgrF_1〜CgrF_5（総合スコア。17）を抽出
                                match = re.search(r'Cgr([A-F])_(\d+)', placeholder)
                                if match:
                                    key = f"Cgr{match.group(1)}_{match.group(2)}"
                                    data['skill_scores'][key] = value if value else ''
                    # 分析総評からC_block_1_bodyを抽出
                    elif in_analysis_summary and '`{{C_block_1_body}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                data['C_block_1_body'] = value
                    # レーダーチャートの説明を抽出
                    elif '### レーダーチャートの説明' in next_line:
                        in_radar_description = True
                    elif in_radar_description and '`{{C_block_2_' in next_line and '}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                if 'C_block_2_1_body}}`' in placeholder:
                                    data['C_block_2_1_body'] = value
                                elif 'C_block_2_2_body}}`' in placeholder:
                                    data['C_block_2_2_body'] = value
                                elif 'C_block_2_3_body}}`' in placeholder:
                                    data['C_block_2_3_body'] = value
                    elif in_radar_description and next_line.startswith('###'):
                        in_radar_description = False
            
            # 推奨プログラムの抽出（スライド7）
            if '## スライド7: 推奨プログラム' in line or 'スライド7: 推奨プログラム' in line:
                # 次のテーブルからデータを抽出
                for j in range(i + 1, min(i + 30, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{WS_' in next_line and '}}`' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                if 'WS_1_title}}`' in placeholder:
                                    data['recommendation']['title'] = value
                                elif 'WS_block_1_body}}`' in placeholder:
                                    data['recommendation']['issues'] = value
                                elif 'WS_block_2_body}}`' in placeholder:
                                    data['recommendation']['reason'] = value
                                elif 'WS_block_3_body}}`' in placeholder:
                                    data['recommendation']['effect'] = value
            
            # スライド8: 満足度分析の抽出
            if '## スライド8: 満足度分析' in line or 'スライド8: 満足度分析' in line:
                for j in range(i + 1, min(i + 30, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{' in next_line and '}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            placeholder = parts[1].strip()
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                if 'period_1}}`' in placeholder:
                                    data['satisfaction']['period'] = value
                                elif 'respondents_1}}`' in placeholder:
                                    data['satisfaction']['respondents'] = value
                                elif 'sc_1}}`' in placeholder:
                                    data['satisfaction']['score_1'] = value
                                elif 'sc_2}}`' in placeholder:
                                    data['satisfaction']['score_2'] = value
                                elif 'sc_3}}`' in placeholder:
                                    data['satisfaction']['score_3'] = value
                                # 後方互換性のため残す
                                elif 'score_1}}`' in placeholder:
                                    data['satisfaction']['score_1'] = value
                                elif 'score_2}}`' in placeholder:
                                    data['satisfaction']['score_2'] = value
                                elif 'score_3}}`' in placeholder:
                                    data['satisfaction']['score_3'] = value
                                elif 'M_block_1_body}}`' in placeholder:
                                    data['satisfaction']['M_block_1_body'] = value
            
            # スライド9: 実践頻度分析の抽出
            if '## スライド9: 実践頻度分析' in line or 'スライド9: 実践頻度分析' in line:
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('##'):
                        break
                    if '`{{F_block_1_body}}`' in next_line and '|' in next_line:
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 3:
                            value = parts[2].strip()
                            if value and value != 'データ内容' and value != '-':
                                data['F_block_1_body'] = value
    except Exception as e:
        safe_print(f"スライド挿入内容Markdown解析エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    return data


def generate_gas_code(project_id: str, project_name: str, phase: int, 
                     report_path: str, radar_path: str, 
                     export_files: List[tuple], slide_content_path: Optional[str] = None) -> str:
    """
    GASコードを生成（レポートデータを直接埋め込む）
    
    Args:
        project_id: プロジェクトID
        project_name: プロジェクト名
        phase: フェーズ（1, 2, 3）
        report_path: レポートMarkdownファイルのパス
        radar_path: レーダーチャートPNGファイルのパス
        export_files: エクスポートファイルのリスト [(label, path), ...]
    
    Returns:
        生成されたGASコード（文字列）
    """
    
    # テンプレートスライドID（Phase別）
    # Phase 1用: https://docs.google.com/presentation/d/1Q09EsrVTDF-TQQbmiLpKvo2maTJyyvWV356Jk8c5rYs/edit
    # Phase 2用: https://docs.google.com/presentation/d/1lBDBCjMu9iiRcdTSgUwNycDbTPAXfZLT6cPtT87EWcw/edit
    # Phase 3用: https://docs.google.com/presentation/d/1G_xm3KH66QQCNsUOcY4JdF7zaeXh0JXQO9IntvAH8ag/edit
    if phase == 1:
        template_slide_id = '1Q09EsrVTDF-TQQbmiLpKvo2maTJyyvWV356Jk8c5rYs'
    elif phase == 2:
        template_slide_id = '1lBDBCjMu9iiRcdTSgUwNycDbTPAXfZLT6cPtT87EWcw'
    else:
        template_slide_id = '1G_xm3KH66QQCNsUOcY4JdF7zaeXh0JXQO9IntvAH8ag'
    
    # スライド挿入内容MarkdownからプレースホルダーIDとデータ内容のマッピングを直接抽出
    if not slide_content_path:
        raise ValueError("スライド挿入内容Markdownファイルのパスが指定されていません")
    
    placeholder_mapping = {}
    try:
        placeholder_mapping = parse_placeholder_mapping_from_markdown(slide_content_path)
        safe_print(f"スライド挿入内容Markdownから{len(placeholder_mapping)}個のプレースホルダーマッピングを抽出しました")
    except Exception as e:
        safe_print(f"スライド挿入内容Markdownの解析エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
        raise
    
    # 後方互換性のため、従来のparse_slide_content_markdownも実行（組織別分析などで使用）
    slide_data = {}
    try:
        slide_data = parse_slide_content_markdown(slide_content_path)
        safe_print(f"スライド挿入内容Markdownから構造化データを抽出しました")
    except Exception as e:
        safe_print(f"スライド挿入内容Markdownの構造化データ解析エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    # 組織別の情報を抽出（スライド挿入内容Markdownから）
    organization_data_from_markdown = []
    try:
        organization_data_from_markdown = parse_organization_data_from_markdown(slide_content_path)
        safe_print(f"スライド挿入内容Markdownから{len(organization_data_from_markdown)}組織のデータを抽出しました")
        # 表プレースホルダー（Ogr* / OrkA_1）が含まれているか検証（14_組織別スライド_表プレースホルダー置換要件）
        if organization_data_from_markdown and 'OgrA_1' not in organization_data_from_markdown[0]:
            safe_print("警告: ORGANIZATION_DATAにスキル分析テーブル（Ogr*）が含まれていません。スライド挿入内容MDに「#### スキル分析テーブル（表内）」の表があるか確認し、GASを再生成してください。")
        if organization_data_from_markdown and 'OrkA_1' not in organization_data_from_markdown[0]:
            safe_print("警告: ORGANIZATION_DATAに理解度（OrkA_1）が含まれていません。スライド挿入内容MDに「#### 理解度」の表があるか確認してください。")
    except Exception as e:
        safe_print(f"組織別データ抽出エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    # CSVデータを読み込む
    csv_data = {}
    safe_print(f"GASコード生成: {len(export_files)}個のCSVファイルを処理します")
    for label, file_path in export_files:
        try:
            if 'エグゼクティブサマリー' in label:
                csv_data['executiveSummary'] = parse_csv_file(file_path)
                safe_print(f"  ✓ エグゼクティブサマリー: {len(csv_data['executiveSummary'])}行")
            elif '組織別分析' in label:
                csv_data['organizationAnalysis'] = parse_csv_file(file_path)
                safe_print(f"  ✓ 組織別分析: {len(csv_data['organizationAnalysis'])}行")
            elif 'ギャップ分析' in label:
                csv_data['gapAnalysis'] = parse_csv_file(file_path)
                safe_print(f"  ✓ ギャップ分析: {len(csv_data['gapAnalysis'])}行")
            elif '満足度分析' in label:
                csv_data['satisfactionAnalysis'] = parse_csv_file(file_path)
                safe_print(f"  ✓ 満足度分析: {len(csv_data['satisfactionAnalysis'])}行")
            elif '実践頻度分析' in label:
                csv_data['practiceFrequency'] = parse_csv_file(file_path)
                safe_print(f"  ✓ 実践頻度分析: {len(csv_data['practiceFrequency'])}行")
            # 個人情報を含むCSVはスライド生成に不要なため、読み込まない
            # elif '個人別スコア推移' in label:
            #     csv_data['individualProgress'] = parse_csv_file(file_path)
            #     print(f"  ✓ 個人別スコア推移: {len(csv_data['individualProgress'])}行")
            # elif '本人上長比較' in label:
            #     csv_data['managerComparison'] = parse_csv_file(file_path)
            #     print(f"  ✓ 本人上長比較: {len(csv_data['managerComparison'])}行")
            # elif 'アンケート項目別' in label or '平均比較表' in label:
            #     csv_data['questionComparison'] = parse_csv_file(file_path)
            #     print(f"  ✓ アンケート項目別平均比較表: {len(csv_data['questionComparison'])}行")
            else:
                safe_print(f"  ⚠ 未処理のCSVファイル: {label}（スライド生成には不要な可能性があります）")
        except Exception as e:
            safe_print(f"CSV解析エラー ({label}, {file_path}): {e}")
            import traceback
            try:
                traceback.print_exc(file=sys.stderr)
            except (BrokenPipeError, OSError):
                pass
            # エラーが発生した場合は空のリストを設定
            if 'エグゼクティブサマリー' in label:
                csv_data['executiveSummary'] = []
            elif '組織別分析' in label:
                csv_data['organizationAnalysis'] = []
            elif 'ギャップ分析' in label:
                csv_data['gapAnalysis'] = []
            elif '満足度分析' in label:
                csv_data['satisfactionAnalysis'] = []
            elif '実践頻度分析' in label:
                csv_data['practiceFrequency'] = []
            # 個人情報を含むCSVはスライド生成に不要なため、空リストも設定しない
            # elif '個人別スコア推移' in label:
            #     csv_data['individualProgress'] = []
            # elif '本人上長比較' in label:
            #     csv_data['managerComparison'] = []
            # elif 'アンケート項目別' in label or '平均比較表' in label:
            #     csv_data['questionComparison'] = []
    
    # 現在の日付を取得
    now = datetime.now()
    date_str = now.strftime('%Y.%m.%d')
    
    # 成功事例、課題・障壁、推奨プログラムのデータをスライド挿入内容Markdownから取得
    success_cases = slide_data.get('success_cases', [])
    barriers = slide_data.get('barriers', [])
    recommendation_data = slide_data.get('recommendation', {})
    skill_scores = slide_data.get('skill_scores', {})
    satisfaction_data = slide_data.get('satisfaction', {})
    
    # JSON形式でデータを埋め込む（スライド挿入内容Markdownを主データソースとして使用）
    report_data_dict = {
        'clientName': slide_data.get('clientName', project_name) or '',
        'project': project_name,
        'reportDate': slide_data.get('reportDate', date_str) or '',
        'period': slide_data.get('period', '') or '',
        'respondents': slide_data.get('respondents', '') or '',
        'phase': f'Phase {phase}',
        # スライド1: エグゼクティブサマリー（スライド挿入内容Markdownから直接取得）
        'S_score_1': slide_data.get('S_score_1', '') or '',
        'S_score_2': slide_data.get('S_score_2', '') or '',
        'S_block_1_body': slide_data.get('S_block_1_body', '') or '',
        'S_block_2_body': slide_data.get('S_block_2_body', '') or '',
        'S_block_3_body': slide_data.get('S_block_3_body', '') or '',
        # スライド2: スキル分析（スライド挿入内容Markdownから直接取得）
        'C_block_1_body': slide_data.get('C_block_1_body', '') or '',
        'C_block_2_1_body': slide_data.get('C_block_2_1_body', '') or '',
        'C_block_2_2_body': slide_data.get('C_block_2_2_body', '') or '',
        'C_block_2_3_body': slide_data.get('C_block_2_3_body', '') or '',
        # スキルスコア（CgrA_1からCgrE_5まで）
        'skill_scores': skill_scores,
        # 成功事例の個別データ（最大4件）
        'successCase1Name': success_cases[0]['name'] if len(success_cases) > 0 else '',
        'successCase1Body': success_cases[0]['body'] if len(success_cases) > 0 else '',
        'successCase2Name': success_cases[1]['name'] if len(success_cases) > 1 else '',
        'successCase2Body': success_cases[1]['body'] if len(success_cases) > 1 else '',
        'successCase3Name': success_cases[2]['name'] if len(success_cases) > 2 else '',
        'successCase3Body': success_cases[2]['body'] if len(success_cases) > 2 else '',
        'successCase4Name': success_cases[3]['name'] if len(success_cases) > 3 else '',
        'successCase4Body': success_cases[3]['body'] if len(success_cases) > 3 else '',
        # 課題・障壁の個別データ（最大4件）
        'barrier1Name': barriers[0]['name'] if len(barriers) > 0 else '',
        'barrier1Body': barriers[0]['body'] if len(barriers) > 0 else '',
        'barrier2Name': barriers[1]['name'] if len(barriers) > 1 else '',
        'barrier2Body': barriers[1]['body'] if len(barriers) > 1 else '',
        'barrier3Name': barriers[2]['name'] if len(barriers) > 2 else '',
        'barrier3Body': barriers[2]['body'] if len(barriers) > 2 else '',
        'barrier4Name': barriers[3]['name'] if len(barriers) > 3 else '',
        'barrier4Body': barriers[3]['body'] if len(barriers) > 3 else '',
        # 推奨プログラムの個別データ
        'recommendationTitle': recommendation_data.get('title', '') or '',
        'recommendationIssues': recommendation_data.get('issues', '') or '',
        'recommendationReason': recommendation_data.get('reason', '') or '',
        'recommendationEffect': recommendation_data.get('effect', '') or '',
        # スライド8: 満足度分析
        'satisfaction_period': satisfaction_data.get('period', '') or '',
        'satisfaction_respondents': satisfaction_data.get('respondents', '') or '',
        'satisfaction_score_1': satisfaction_data.get('score_1', '') or '',
        'satisfaction_score_2': satisfaction_data.get('score_2', '') or '',
        'satisfaction_score_3': satisfaction_data.get('score_3', '') or '',
        'satisfaction_M_block_1_body': satisfaction_data.get('M_block_1_body', '') or '',
        # スライド9: 実践頻度分析
        'F_block_1_body': slide_data.get('F_block_1_body', '') or '',
        # 後方互換性のため残す（空文字列）
        'overallComment': '',
        'goodPoints': '',
        'weakPoints': '',
        'skillSummary': '',
        'gapAnalysis': '',
        'successCases': '',
        'barriers': '',
        'recommendation': ''
    }
    
    # REPORT_DATA と PLACEHOLDER_DATA の一致のため、C_block_* が空のときは placeholder_mapping から補完
    for key in ('C_block_1_body', 'C_block_2_1_body', 'C_block_2_2_body', 'C_block_2_3_body'):
        if not (report_data_dict.get(key) or '').strip():
            ph_key = '{{' + key + '}}'
            report_data_dict[key] = placeholder_mapping.get(ph_key, '') or ''
    
    # JSON形式でシリアライズ（ensure_ascii=Falseで日本語をそのまま保持）
    report_data_js = json.dumps(report_data_dict, ensure_ascii=False, indent=2)
    
    # CSVデータをJSON形式で埋め込む（スライド生成に必要なもののみ）
    # 個人情報を含むCSV（individualProgress, managerComparison, questionComparison）は除外
    csv_data_dict = {
        'executiveSummary': csv_data.get('executiveSummary', []) or [],
        'organizationAnalysis': csv_data.get('organizationAnalysis', []) or [],
        'gapAnalysis': csv_data.get('gapAnalysis', []) or [],
        'satisfactionAnalysis': csv_data.get('satisfactionAnalysis', []) or [],
        'practiceFrequency': csv_data.get('practiceFrequency', []) or []
    }
    
    # データの確認ログ
    safe_print(f"GASコード生成: CSVデータのサマリー:")
    for key, value in csv_data_dict.items():
        if isinstance(value, list):
            safe_print(f"  {key}: {len(value)}行")
        else:
            safe_print(f"  {key}: {type(value)}")
    
    # CSVデータをJSON形式でシリアライズ
    csv_data_js = json.dumps(csv_data_dict, ensure_ascii=False, indent=2)
    
    # プレースホルダーマッピングをJSON形式でシリアライズ
    placeholder_mapping_js = json.dumps(placeholder_mapping, ensure_ascii=False, indent=2)
    
    # 組織別データをJSON形式でシリアライズ
    organization_data_js = json.dumps(organization_data_from_markdown, ensure_ascii=False, indent=2)
    
    # レーダーチャート画像のファイル名（ユーザーがGoogleドライブにアップロードする）
    radar_filename = os.path.basename(radar_path) if os.path.exists(radar_path) else ''
    
    # レーダーチャート画像が存在するか確認
    radar_file_exists = os.path.exists(radar_path) if radar_path else False
    
    gas_code = f'''/**
 * 実践スキル定着度レポート スライド自動生成
 * プロジェクト: {project_name}
 * 生成日: {date_str}
 * 
 * 使用方法:
 * 1. マスターテンプレートのスライドを開く
 *    - Phase 1用: https://docs.google.com/presentation/d/1Q09EsrVTDF-TQQbmiLpKvo2maTJyyvWV356Jk8c5rYs/edit
 *    - Phase 2用: https://docs.google.com/presentation/d/1lBDBCjMu9iiRcdTSgUwNycDbTPAXfZLT6cPtT87EWcw/edit
 *    - Phase 3用: https://docs.google.com/presentation/d/1G_xm3KH66QQCNsUOcY4JdF7zaeXh0JXQO9IntvAH8ag/edit
 * 2. 拡張機能 > Apps Script を開く
 * 3. このコードを貼り付けて保存
 * 4. 実行 > generateSlides を実行（開いているスライドにデータが挿入されます）
 * 5. レーダーチャート画像は手動でスライドに挿入してください（{{graph_radar_chart}}の位置に画像を配置）
 * 
 * データ要件（分析アプリで検証済み）:
 * - 実施前.csvと直後.csvでは、同一参加者が同じメールアドレスを使用すること
 * - メールアドレスの重複や不一致があると分析は実行されない
 * 
 * 注意: 
 * - レーダーチャート画像は手動で挿入してください（自動挿入は行いません）
 * - テンプレートスライドを複製して新しいスライドを作成したい場合は、generateSlidesFromTemplate()関数を使用してください
 * - Phase 1では、満足度分析とPhase 3専用のスライド（ギャップ分析、成功事例、課題・障壁、推奨プログラム、実践頻度分析）はスキップされます
 * - Phase 2では、Phase 3専用のスライド（ギャップ分析、成功事例、課題・障壁、推奨プログラム、実践頻度分析）はスキップされます
 * - 満足度分析（satisfaction）のデータは 04_満足度分析.csv を参照。直後フォームの「今回のワークショップの内容に対する満足度はどの程度ですか？」／「今回のワークショップの内容をどの程度理解できましたか？」／「このワークショップを、同僚や知人にどの程度おすすめしたいですか？」の3問から生成される。
 */

// ============================================
// 設定
// ============================================
const TEMPLATE_SLIDE_ID = '{template_slide_id}';

// ============================================
// レポートデータ（埋め込み）
// ============================================
const REPORT_DATA = {report_data_js};

const CSV_DATA = {csv_data_js};

// ============================================
// 組織別データ（スライド挿入内容Markdownから直接抽出）
// ============================================
const ORGANIZATION_DATA = {organization_data_js};

// ============================================
// プレースホルダーとデータ内容のマッピング（スライド挿入内容Markdownから直接抽出）
// ============================================
const PLACEHOLDER_DATA = {placeholder_mapping_js};

// ============================================
// レーダーチャート画像設定
// ============================================
// 注意: レーダーチャート画像は手動でスライドに挿入してください
// {{graph_radar_chart}}の位置に画像を配置してください

// ============================================
// プレースホルダーマッピング
// ============================================
const PLACEHOLDER_MAP = {{
  CLIENT: '{{{{Client}}}}',
  PERIOD_1: '{{{{period_1}}}}',
  RESPONDENTS_1: '{{{{respondents_1}}}}',
  PHASE_1: '{{{{phase_1}}}}',
  // エグゼクティブサマリー（PDF形式）
  S_SCORE_1: '{{{{S_score_1}}}}',
  S_SCORE_2: '{{{{S_score_2}}}}',
  S_BLOCK_1_BODY: '{{{{S_block_1_body}}}}',
  S_BLOCK_2_BODY: '{{{{S_block_2_body}}}}',
  S_BLOCK_3_BODY: '{{{{S_block_3_body}}}}',
  // スキル分析（PDF形式）
  C_BLOCK_1_BODY: '{{{{C_block_1_body}}}}',
  C_BLOCK_2_1_BODY: '{{{{C_block_2_1_body}}}}',
  C_BLOCK_2_2_BODY: '{{{{C_block_2_2_body}}}}',
  C_BLOCK_2_3_BODY: '{{{{C_block_2_3_body}}}}',
  // 組織別分析（PDF形式）LAYOUT: analysis_by_organization（O_block_1_bodyは廃止・空で置換）
  O_BLOCK_1_BODY: '{{{{O_block_1_body}}}}',
  O_BLOCK_2_BODY: '{{{{O_block_2_body}}}}',
  O_BLOCK_3_BODY: '{{{{O_block_3_body}}}}',
  O_OVERALL_SCORE_NAME: '{{{{O_overall_score_name}}}}',
  O_OVERALL_SCORE: '{{{{O_overall_score}}}}',
  O_SCORE: '{{{{O_score}}}}',
  O_RESPONDENTS_1: '{{{{O_respondents_1}}}}',
  OrkA_1: '{{{{OrkA_1}}}}',
  // 組織別スキル分析テーブル（OgrA_1〜OgrE_5、OgrF_1〜OgrF_5=総合スコア。17）
  OgrA_1: '{{{{OgrA_1}}}}', OgrA_2: '{{{{OgrA_2}}}}', OgrA_3: '{{{{OgrA_3}}}}', OgrA_4: '{{{{OgrA_4}}}}', OgrA_5: '{{{{OgrA_5}}}}',
  OgrB_1: '{{{{OgrB_1}}}}', OgrB_2: '{{{{OgrB_2}}}}', OgrB_3: '{{{{OgrB_3}}}}', OgrB_4: '{{{{OgrB_4}}}}', OgrB_5: '{{{{OgrB_5}}}}',
  OgrC_1: '{{{{OgrC_1}}}}', OgrC_2: '{{{{OgrC_2}}}}', OgrC_3: '{{{{OgrC_3}}}}', OgrC_4: '{{{{OgrC_4}}}}', OgrC_5: '{{{{OgrC_5}}}}',
  OgrD_1: '{{{{OgrD_1}}}}', OgrD_2: '{{{{OgrD_2}}}}', OgrD_3: '{{{{OgrD_3}}}}', OgrD_4: '{{{{OgrD_4}}}}', OgrD_5: '{{{{OgrD_5}}}}',
  OgrE_1: '{{{{OgrE_1}}}}', OgrE_2: '{{{{OgrE_2}}}}', OgrE_3: '{{{{OgrE_3}}}}', OgrE_4: '{{{{OgrE_4}}}}', OgrE_5: '{{{{OgrE_5}}}}',
  OgrF_1: '{{{{OgrF_1}}}}', OgrF_2: '{{{{OgrF_2}}}}', OgrF_3: '{{{{OgrF_3}}}}', OgrF_4: '{{{{OgrF_4}}}}', OgrF_5: '{{{{OgrF_5}}}}',
  // 成功事例（PDF形式）
  T_BLOCK_1_NAME: '{{{{T_block_1_name}}}}',
  T_BLOCK_1_BODY: '{{{{T_block_1_body}}}}',
  T_BLOCK_2_NAME: '{{{{T_block_2_name}}}}',
  T_BLOCK_2_BODY: '{{{{T_block_2_body}}}}',
  T_BLOCK_3_NAME: '{{{{T_block_3_name}}}}',
  T_BLOCK_3_BODY: '{{{{T_block_3_body}}}}',
  T_BLOCK_4_NAME: '{{{{T_block_4_name}}}}',
  T_BLOCK_4_BODY: '{{{{T_block_4_body}}}}',
  // 課題・障壁（PDF形式）
  I_BLOCK_1_NAME: '{{{{I_block_1_name}}}}',
  I_BLOCK_1_BODY: '{{{{I_block_1_body}}}}',
  I_BLOCK_2_NAME: '{{{{I_block_2_name}}}}',
  I_BLOCK_2_BODY: '{{{{I_block_2_body}}}}',
  I_BLOCK_3_NAME: '{{{{I_block_3_name}}}}',
  I_BLOCK_3_BODY: '{{{{I_block_3_body}}}}',
  I_BLOCK_4_NAME: '{{{{I_block_4_name}}}}',
  I_BLOCK_4_BODY: '{{{{I_block_4_body}}}}',
  // 推奨プログラム（PDF形式）
  WS_1_TITLE: '{{{{WS_1_title}}}}',
  WS_BLOCK_1_BODY: '{{{{WS_block_1_body}}}}',
  WS_BLOCK_2_BODY: '{{{{WS_block_2_body}}}}',
  WS_BLOCK_3_BODY: '{{{{WS_block_3_body}}}}',
  // 満足度分析（PDF形式）
  M_BLOCK_1_BODY: '{{{{M_block_1_body}}}}',
  // 実践頻度分析（PDF形式）
  F_BLOCK_1_BODY: '{{{{F_block_1_body}}}}',
  // その他（後方互換性のため残す）
  BLOCK_1_BODY: '{{{{block_1_body}}}}',
  BLOCK_2_BODY: '{{{{block_2_body}}}}',
  BLOCK_3_BODY: '{{{{block_3_body}}}}',
  BLOCK_4_BODY: '{{{{block_4_body}}}}',
  GRAPH_OVERALL_SCORE: '{{{{graph_overall_score}}}}',
  GRAPH_RADAR_CHART: '{{{{graph_radar_chart}}}}',
  GRAPH_GAP: '{{{{graph_gap}}}}',
  GRAPH_PIE_CHART: '{{{{graph_pie_chart}}}}',
  ORGANIZATION_NAME: '{{{{organization_name}}}}',
  OVERALL_SCORE: '{{{{overall_score}}}}',
  SCORE_1: '{{{{score_1}}}}',
  SCORE_2: '{{{{score_2}}}}',
  SCORE_3: '{{{{score_3}}}}',
  // スキル軸スコア（レーダーチャートスライドの表用）- PDF形式（CgrX_Y形式）
  // A=具体化・検証力、B=リサーチ・分析力、C=構想・コンセプト力、D=伝達・構造化力、E=実現・ディレクション力
  // 1=実施前、2=直後、3=1ヶ月後、4=変化量(直後)、5=変化量(1ヶ月後)
  SKILL_CGRA_1: '{{{{CgrA_1}}}}', // 具体化・検証力 実施前
  SKILL_CGRA_2: '{{{{CgrA_2}}}}', // 具体化・検証力 直後
  SKILL_CGRA_3: '{{{{CgrA_3}}}}', // 具体化・検証力 1ヶ月後
  SKILL_CGRA_4: '{{{{CgrA_4}}}}', // 具体化・検証力 変化量(直後)
  SKILL_CGRA_5: '{{{{CgrA_5}}}}', // 具体化・検証力 変化量(1ヶ月後)
  SKILL_CGRB_1: '{{{{CgrB_1}}}}', // リサーチ・分析力 実施前
  SKILL_CGRB_2: '{{{{CgrB_2}}}}', // リサーチ・分析力 直後
  SKILL_CGRB_3: '{{{{CgrB_3}}}}', // リサーチ・分析力 1ヶ月後
  SKILL_CGRB_4: '{{{{CgrB_4}}}}', // リサーチ・分析力 変化量(直後)
  SKILL_CGRB_5: '{{{{CgrB_5}}}}', // リサーチ・分析力 変化量(1ヶ月後)
  SKILL_CGRC_1: '{{{{CgrC_1}}}}', // 構想・コンセプト力 実施前
  SKILL_CGRC_2: '{{{{CgrC_2}}}}', // 構想・コンセプト力 直後
  SKILL_CGRC_3: '{{{{CgrC_3}}}}', // 構想・コンセプト力 1ヶ月後
  SKILL_CGRC_4: '{{{{CgrC_4}}}}', // 構想・コンセプト力 変化量(直後)
  SKILL_CGRC_5: '{{{{CgrC_5}}}}', // 構想・コンセプト力 変化量(1ヶ月後)
  SKILL_CGRD_1: '{{{{CgrD_1}}}}', // 伝達・構造化力 実施前
  SKILL_CGRD_2: '{{{{CgrD_2}}}}', // 伝達・構造化力 直後
  SKILL_CGRD_3: '{{{{CgrD_3}}}}', // 伝達・構造化力 1ヶ月後
  SKILL_CGRD_4: '{{{{CgrD_4}}}}', // 伝達・構造化力 変化量(直後)
  SKILL_CGRD_5: '{{{{CgrD_5}}}}', // 伝達・構造化力 変化量(1ヶ月後)
  SKILL_CGRE_1: '{{{{CgrE_1}}}}', // 実現・ディレクション力 実施前
  SKILL_CGRE_2: '{{{{CgrE_2}}}}', // 実現・ディレクション力 直後
  SKILL_CGRE_3: '{{{{CgrE_3}}}}', // 実現・ディレクション力 1ヶ月後
  SKILL_CGRE_4: '{{{{CgrE_4}}}}', // 実現・ディレクション力 変化量(直後)
  SKILL_CGRE_5: '{{{{CgrE_5}}}}', // 実現・ディレクション力 変化量(1ヶ月後)
  // 総合スコア（17_スキル分析テーブル_総合スコア行追加要件）
  SKILL_CGRF_1: '{{{{CgrF_1}}}}', SKILL_CGRF_2: '{{{{CgrF_2}}}}', SKILL_CGRF_3: '{{{{CgrF_3}}}}', SKILL_CGRF_4: '{{{{CgrF_4}}}}', SKILL_CGRF_5: '{{{{CgrF_5}}}}',
  // ギャップ分析テーブル用プレースホルダー（GgrX_Y形式）
  // A=具体化・検証力、B=リサーチ・分析力、C=構想・コンセプト力、D=伝達・構造化力、E=実現・ディレクション力
  // 1=本人評価(1ヶ月後)、2=上長評価、3=ギャップ、4=解釈（評価）
  GAP_GGRA_1: '{{{{GgrA_1}}}}', // 具体化・検証力 本人評価(1ヶ月後)
  GAP_GGRA_2: '{{{{GgrA_2}}}}', // 具体化・検証力 上長評価
  GAP_GGRA_3: '{{{{GgrA_3}}}}', // 具体化・検証力 ギャップ
  GAP_GGRA_4: '{{{{GgrA_4}}}}', // 具体化・検証力 解釈（評価）
  GAP_GGRB_1: '{{{{GgrB_1}}}}', // リサーチ・分析力 本人評価(1ヶ月後)
  GAP_GGRB_2: '{{{{GgrB_2}}}}', // リサーチ・分析力 上長評価
  GAP_GGRB_3: '{{{{GgrB_3}}}}', // リサーチ・分析力 ギャップ
  GAP_GGRB_4: '{{{{GgrB_4}}}}', // リサーチ・分析力 解釈（評価）
  GAP_GGRC_1: '{{{{GgrC_1}}}}', // 構想・コンセプト力 本人評価(1ヶ月後)
  GAP_GGRC_2: '{{{{GgrC_2}}}}', // 構想・コンセプト力 上長評価
  GAP_GGRC_3: '{{{{GgrC_3}}}}', // 構想・コンセプト力 ギャップ
  GAP_GGRC_4: '{{{{GgrC_4}}}}', // 構想・コンセプト力 解釈（評価）
  GAP_GGRD_1: '{{{{GgrD_1}}}}', // 伝達・構造化力 本人評価(1ヶ月後)
  GAP_GGRD_2: '{{{{GgrD_2}}}}', // 伝達・構造化力 上長評価
  GAP_GGRD_3: '{{{{GgrD_3}}}}', // 伝達・構造化力 ギャップ
  GAP_GGRD_4: '{{{{GgrD_4}}}}', // 伝達・構造化力 解釈（評価）
  GAP_GGRE_1: '{{{{GgrE_1}}}}', // 実現・ディレクション力 本人評価(1ヶ月後)
  GAP_GGRE_2: '{{{{GgrE_2}}}}', // 実現・ディレクション力 上長評価
  GAP_GGRE_3: '{{{{GgrE_3}}}}', // 実現・ディレクション力 ギャップ
  GAP_GGRE_4: '{{{{GgrE_4}}}}' // 実現・ディレクション力 解釈（評価）
}};

// ============================================
// スライドインデックス（Phase別）
// ============================================
// Phaseを取得（REPORT_DATAから）
const CURRENT_PHASE = REPORT_DATA.phase ? parseInt(REPORT_DATA.phase.replace(/[^0-9]/g, '')) : 3;

// Phaseに応じたスライドインデックスを返す関数
function getSlideIndex(phase) {{
  if (phase === 1) {{
    // Phase 1のスライド構造
    return {{
      COVER: 0,
      OVERALL_SCORE: 1,
      SKILL_ANALYSIS: 2,
      ORG_ANALYSIS: 3
      // Phase 1では満足度分析は含まれない（ワークショップをまだ実施していないため）
    }};
  }} else if (phase === 2) {{
    // Phase 2のスライド構造
    return {{
      COVER: 0,
      OVERALL_SCORE: 1,
      SKILL_ANALYSIS: 2,
      ORG_ANALYSIS: 3,
      // Phase 2では満足度分析は組織別分析の後に動的に配置される（スライド8相当）
      // 組織別分析スライド数に応じて動的に決定されるため、固定インデックスは使用しない
      SATISFACTION: -1  // 動的に決定（組織別分析スライドの後）
    }};
  }} else {{
    // Phase 3のスライド構造
    return {{
      COVER: 0,
      OVERALL_SCORE: 1,
      SKILL_ANALYSIS: 2,
      ORG_ANALYSIS: 3,
      GAP_ANALYSIS: 4,
      SUCCESS_CASES: 5,
      BARRIERS: 6,
      RECOMMENDATION: 7,
      SATISFACTION: 8,
      PRACTICE_FREQ: 9
    }};
  }}
}}

// 後方互換性のため、従来のSLIDE_INDEXも定義（現在のPhase用）
const SLIDE_INDEX = getSlideIndex(CURRENT_PHASE);

// ============================================
// メイン処理
// ============================================

/**
 * スライドを生成（実行中のスライドにデータを挿入）
 * テンプレートスライドを複製して新しいスライドを作成する場合は、generateSlidesFromTemplate()を使用
 */
function generateSlides() {{
  try {{
    const ui = SlidesApp.getUi();
    const presentation = SlidesApp.getActivePresentation(); // 実行中のスライドに適用
    
    Logger.log('=== GASスライド生成開始 ===');
    
    // スライドにデータを配置（レーダーチャートは手動挿入のため、nullを渡す）
    const startTime = new Date().getTime();
    applyDataToSlides_(presentation, REPORT_DATA, CSV_DATA, null);
    const endTime = new Date().getTime();
    const elapsedTime = ((endTime - startTime) / 1000).toFixed(2);
    
    Logger.log('=== スライドデータ挿入完了（処理時間: ' + elapsedTime + '秒） ===');
    
    ui.alert('完了', 'スライドにデータを挿入しました。\\n\\n処理時間: ' + elapsedTime + '秒\\n\\nレーダーチャート画像は手動で挿入してください。', ui.ButtonSet.OK);
    
    return presentation;
    
  }} catch (error) {{
    const ui = SlidesApp.getUi();
    ui.alert('エラー', 'スライド生成中にエラーが発生しました:\\n' + error.message + '\\n\\nスタック: ' + error.stack, ui.ButtonSet.OK);
    Logger.log('generateSlides エラー: ' + error.message);
    Logger.log('スタック: ' + error.stack);
    throw error;
  }}
}}

/**
 * テンプレートスライドを複製して新しいスライドを作成（オプション）
 */
function generateSlidesFromTemplate() {{
  try {{
    // テンプレートを複製して新しいスライドを作成
    const clientName = REPORT_DATA.clientName || REPORT_DATA.project || '{project_name}';
    const reportDate = REPORT_DATA.reportDate || '{date_str}';
    const newFileName = clientName + '_レポート_' + reportDate.replace(/\\./g, '');
    
    // テンプレートファイルを取得
    const templateFile = DriveApp.getFileById(TEMPLATE_SLIDE_ID);
    
    // テンプレートと同じフォルダに新しいスライドを作成
    const parentFolder = templateFile.getParents().next();
    const newFile = templateFile.makeCopy(newFileName, parentFolder);
    const presentation = SlidesApp.openById(newFile.getId());
    
    // スライドにデータを配置（レーダーチャートは手動挿入のため、nullを渡す）
    applyDataToSlides_(presentation, REPORT_DATA, CSV_DATA, null);
    
    // スライドのURLを取得
    const slideUrl = presentation.getUrl();
    
    const ui = SlidesApp.getUi();
    ui.alert(
      '完了',
      'スライドを生成しました。\\n\\nファイル名: ' + newFileName + '\\nURL: ' + slideUrl + '\\n\\nレーダーチャート画像は手動で挿入してください。',
      ui.ButtonSet.OK
    );
    
    return presentation;
    
  }} catch (error) {{
    const ui = SlidesApp.getUi();
    ui.alert('エラー', 'スライド生成中にエラーが発生しました:\\n' + error.message, ui.ButtonSet.OK);
    Logger.log('generateSlidesFromTemplate エラー: ' + error.message);
    throw error;
  }}
}}


// ============================================
// スライドへのデータ配置
// ============================================

/**
 * スライドにデータを配置
 * PLACEHOLDER_DATAから直接データを取得して置換（スライド挿入内容Markdownから直接抽出されたマッピングを使用）
 */
function applyDataToSlides_(presentation, reportData, csvData, radarChartBlob) {{
  Logger.log('=== スライドデータ挿入開始 ===');
  
  // Phaseを判定（REPORT_DATAから取得）
  const phase = reportData.phase ? parseInt(reportData.phase.replace(/[^0-9]/g, '')) : 3;
  Logger.log('Phase: ' + phase);
  
  // Phaseに応じたスライドインデックスを取得
  const SLIDE_INDEX = getSlideIndex(phase);
  
  // ステップ1: 組織別分析スライドを先に生成（ORGテンプレがプレースホルダーのままの状態で）
  // これにより、ORGテンプレート上のプレースホルダーが先に「開発部」に確定されるのを防ぐ
  if (csvData.organizationAnalysis && csvData.organizationAnalysis.length > 0) {{
    Logger.log('=== 組織別分析スライドを生成中（先に実行） ===');
    buildOrgSlidesFromCSV_(presentation, csvData.organizationAnalysis, phase);
  }}
  
  // ステップ2: 全スライドに対して、PLACEHOLDER_DATAから直接データを取得して置換
  // ただし、ORG_ANALYSISテンプレートと生成されたORGスライドは除外（既に置換済み）
  // Phase 1では満足度分析とPhase 3専用のスライドをスキップ
  // Phase 2ではPhase 3専用のスライド（ギャップ分析、成功事例、課題・障壁、推奨プログラム、実践頻度分析）をスキップ
  const slides = presentation.getSlides();
  Logger.log('総スライド数: ' + slides.length);
  Logger.log('PLACEHOLDER_DATAのキー数: ' + Object.keys(PLACEHOLDER_DATA).length);
  
  // 組織別スライドのインデックスを収集（除外対象）
  const orgSlideIndices = new Set();
  orgSlideIndices.add(SLIDE_INDEX.ORG_ANALYSIS); // テンプレートスライド
  
  // Phase 2では満足度分析のスライド番号を動的に決定（組織別分析スライド生成後）
  if (phase === 2) {{
    // 組織別分析スライドのインデックスを取得
    const orgAnalysisIndex = SLIDE_INDEX.ORG_ANALYSIS;
    // 組織別スライド数をカウント（ORG_ANALYSISテンプレート + 生成された組織別スライド）
    let orgSlideCount = 1; // テンプレートスライドを含む
    for (let i = 0; i < slides.length; i++) {{
      if (i === orgAnalysisIndex) continue;
      try {{
        const notes = slides[i].getNotesPage();
        const notesText = notes.getSpeakerNotesShape().getText().asString();
        if (notesText.indexOf('[AUTO_ORG_SLIDE]') !== -1) {{
          orgSlideCount++;
        }}
      }} catch (e) {{
        // スピーカーノート取得エラーは無視
      }}
    }}
    // 満足度分析のスライド番号を決定（組織別分析テンプレート + 生成された組織別スライド数）
    const satisfactionSlideIndex = orgAnalysisIndex + orgSlideCount;
    Logger.log('Phase 2: 満足度分析スライドのインデックスを動的に決定: ' + satisfactionSlideIndex + ' (組織別スライド数: ' + orgSlideCount + ')');
    
    // Phase 2の満足度分析スライドのインデックスを設定
    SLIDE_INDEX.SATISFACTION = satisfactionSlideIndex;
  }}
  
  // Phase 1とPhase 2ではPhase 3専用スライドをスキップするためのインデックス
  const skipSlideIndices = new Set();
  if (phase === 1 || phase === 2) {{
    // Phase 1とPhase 2では以下のスライドをスキップ（存在する場合）
    // Phase 3専用スライドのインデックス（Phase 3のスライド構造から取得）
    const phase3Index = getSlideIndex(3);
    if (phase3Index.GAP_ANALYSIS !== undefined && phase3Index.GAP_ANALYSIS < slides.length) {{
      skipSlideIndices.add(phase3Index.GAP_ANALYSIS);
    }}
    if (phase3Index.SUCCESS_CASES !== undefined && phase3Index.SUCCESS_CASES < slides.length) {{
      skipSlideIndices.add(phase3Index.SUCCESS_CASES);
    }}
    if (phase3Index.BARRIERS !== undefined && phase3Index.BARRIERS < slides.length) {{
      skipSlideIndices.add(phase3Index.BARRIERS);
    }}
    if (phase3Index.RECOMMENDATION !== undefined && phase3Index.RECOMMENDATION < slides.length) {{
      skipSlideIndices.add(phase3Index.RECOMMENDATION);
    }}
    if (phase3Index.PRACTICE_FREQ !== undefined && phase3Index.PRACTICE_FREQ < slides.length) {{
      skipSlideIndices.add(phase3Index.PRACTICE_FREQ);
    }}
    
    // Phase 1では満足度分析もスキップ（ワークショップをまだ実施していないため）
    if (phase === 1) {{
      const phase2Index = getSlideIndex(2);
      if (phase2Index.SATISFACTION !== undefined && phase2Index.SATISFACTION !== -1 && phase2Index.SATISFACTION < slides.length) {{
        skipSlideIndices.add(phase2Index.SATISFACTION);
      }}
      // Phase 2の満足度分析スライドが動的に配置される可能性があるため、スライドをチェック
      for (let i = 0; i < slides.length; i++) {{
        try {{
          const slide = slides[i];
          const layout = slide.getLayout();
          const layoutName = layout.getLayoutName().toLowerCase();
          if (layoutName.indexOf('satisfaction') !== -1 || layoutName.indexOf('満足度') !== -1) {{
            skipSlideIndices.add(i);
            Logger.log('Phase 1: 満足度分析スライドをスキップ: インデックス ' + i);
          }}
        }} catch (e) {{
          // エラーは無視
        }}
      }}
    }}
  }}
  
  // 生成された組織別スライドを検出（スピーカーノートに[AUTO_ORG_SLIDE]または[AUTO_ORG_SLIDE_TEMPLATE]マーカーがある）
  for (let i = 0; i < slides.length; i++) {{
    if (i === SLIDE_INDEX.ORG_ANALYSIS) {{
      // テンプレートスライドもチェック（マーカーが付いている場合は除外）
      try {{
        const notes = slides[i].getNotesPage();
        const notesText = notes.getSpeakerNotesShape().getText().asString();
        if (notesText.indexOf('[AUTO_ORG_SLIDE_TEMPLATE]') !== -1 || notesText.indexOf('[AUTO_ORG_SLIDE]') !== -1) {{
          orgSlideIndices.add(i);
          Logger.log('組織別スライド（テンプレート）を検出（除外対象）: インデックス ' + i);
        }}
      }} catch (e) {{
        // スピーカーノート取得エラーは無視
      }}
      continue;
    }}
    try {{
      const notes = slides[i].getNotesPage();
      const notesText = notes.getSpeakerNotesShape().getText().asString();
      if (notesText.indexOf('[AUTO_ORG_SLIDE]') !== -1 || notesText.indexOf('[AUTO_ORG_SLIDE_TEMPLATE]') !== -1) {{
        orgSlideIndices.add(i);
        Logger.log('組織別スライドを検出（除外対象）: インデックス ' + i);
      }}
    }} catch (e) {{
      // スピーカーノート取得エラーは無視
    }}
  }}
  
  // 全スライドをループして置換（ORGスライドとPhase 2ではPhase 3専用スライドを除外）
  for (let slideIndex = 0; slideIndex < slides.length; slideIndex++) {{
    if (orgSlideIndices.has(slideIndex)) {{
      Logger.log('=== スライド' + slideIndex + '（組織別分析）はスキップ（既に置換済み） ===');
      continue;
    }}
    
    // Phase 1とPhase 2ではPhase 3専用スライドと満足度分析（Phase 1のみ）をスキップ
    if (skipSlideIndices.has(slideIndex)) {{
      Logger.log('=== スライド' + slideIndex + '（Phase ' + phase + 'では使用しないスライド）はスキップ ===');
      continue;
    }}
    
    const slide = slides[slideIndex];
    Logger.log('=== スライド' + slideIndex + 'を処理中 ===');
    
    // PLACEHOLDER_DATAから直接データを取得して置換
    replacePlaceholdersInSlide_(slide, PLACEHOLDER_DATA);
  }}
  
  Logger.log('=== 全スライドデータ挿入処理完了 ===');
}}

/**
 * CSVデータから組織別スライドを生成
 */
function buildOrgSlidesFromCSV_(presentation, orgData, phase) {{
  if (!orgData || orgData.length === 0) {{
    return;
  }}
  
  // Phaseに応じたスライドインデックスを取得
  const SLIDE_INDEX = getSlideIndex(phase || 3);
  
  const slides = presentation.getSlides();
  const templateSlideIndex = SLIDE_INDEX.ORG_ANALYSIS;
  
  if (templateSlideIndex >= slides.length) {{
    Logger.log('組織別分析テンプレートスライドが見つかりません（インデックス: ' + templateSlideIndex + '）');
    return;
  }}
  
  // 前回生成した組織別スライドを削除（[AUTO_ORG_SLIDE]のスライドを削除。[AUTO_ORG_SLIDE_TEMPLATE]はテンプレートとして残し、templateSlideIndexへ移動）
  Logger.log('=== 前回生成した組織別スライドを削除中 ===');
  const slidesToDelete = [];
  let templateSlideRef = null;  // テンプレートスライド（マーカーで識別）
  for (let i = 0; i < slides.length; i++) {{
    try {{
      const notes = slides[i].getNotesPage();
      const notesText = notes.getSpeakerNotesShape().getText().asString();
      if (notesText.indexOf('[AUTO_ORG_SLIDE_TEMPLATE]') !== -1) {{
        templateSlideRef = slides[i];
        continue;  // テンプレートは削除しない
      }}
      if (notesText.indexOf('[AUTO_ORG_SLIDE]') !== -1) {{
        slidesToDelete.push(i);
      }}
    }} catch (e) {{
      // スピーカーノート取得エラーは無視
    }}
  }}
  // マーカーが無い場合は templateSlideIndex のスライドをテンプレートとする（初回実行時）
  if (!templateSlideRef && templateSlideIndex < slides.length) {{
    templateSlideRef = slides[templateSlideIndex];
  }}

  // 後ろから削除（インデックスがずれないように）
  for (let i = slidesToDelete.length - 1; i >= 0; i--) {{
    try {{
      slides[slidesToDelete[i]].remove();
      Logger.log('組織別スライドを削除: インデックス ' + slidesToDelete[i]);
    }} catch (e) {{
      Logger.log('スライド削除エラー: ' + e.message);
    }}
  }}

  // スライドを再取得（削除後）
  const updatedSlides = presentation.getSlides();
  let templateSlide = templateSlideRef;
  // テンプレートを templateSlideIndex に移動（プレースホルダー入りテンプレを常に同じ位置に置く）
  if (templateSlide) {{
    try {{
      const idx = updatedSlides.indexOf(templateSlide);
      if (idx !== -1 && idx !== templateSlideIndex) {{
        templateSlide.move(templateSlideIndex);
        Logger.log('テンプレートスライドをインデックス ' + templateSlideIndex + ' に移動');
      }}
    }} catch (e) {{ Logger.log('テンプレート移動エラー: ' + e.message); }}
    // 再取得（move 後）
    const afterSlides = presentation.getSlides();
    templateSlide = afterSlides[templateSlideIndex];
  }}
  if (!templateSlide) {{
    templateSlide = updatedSlides[templateSlideIndex];
  }}

  // 組織別スライド上の「強み・弱み」ブロックの現在テキストを取得（getOrgBlockTextsFromSlide_ はフォールバック用に残す）
  const getOrgBlockTextsFromSlide_ = function(slide) {{
    let block2 = null, block3 = null;
    const longTexts = [];
    const ph2 = PLACEHOLDER_MAP.O_BLOCK_2_BODY || '{{{{O_block_2_body}}}}';
    const ph3 = PLACEHOLDER_MAP.O_BLOCK_3_BODY || '{{{{O_block_3_body}}}}';
    try {{
      const shapes = slide.getShapes();
      for (let si = 0; si < shapes.length; si++) {{
        try {{
          const tr = shapes[si].getText();
          if (!tr) continue;
          const t = tr.asString().trim();
          if (!t) continue;
          if (t.indexOf(ph2) !== -1) block2 = t;
          else if (t.indexOf(ph3) !== -1) block3 = t;
          else if (t.length > 80 && t.indexOf('{{{{') === -1) longTexts.push({{ text: t, top: shapes[si].getTop() }});
        }} catch (e) {{}}
      }}
      const tables = slide.getTables();
      if (tables && tables.length > 0) {{
        for (let ti = 0; ti < tables.length; ti++) {{
          const table = tables[ti];
          for (let row = 0; row < table.getNumRows(); row++) {{
            for (let col = 0; col < table.getNumColumns(); col++) {{
              try {{
                const cell = table.getCell(row, col);
                const t = (cell.getText() && cell.getText().asString()) ? cell.getText().asString().trim() : '';
                if (!t) continue;
                if (t.indexOf(ph2) !== -1) block2 = t;
                else if (t.indexOf(ph3) !== -1) block3 = t;
                else if (t.length > 80 && t.indexOf('{{{{') === -1) longTexts.push({{ text: t, top: row * 1000 + col }});
              }} catch (e) {{}}
            }}
          }}
        }}
      }}
      if (!block2 || !block3) {{
        longTexts.sort(function(a, b) {{ return a.top - b.top; }});
        if (longTexts.length >= 1 && !block2) block2 = longTexts[0].text;
        if (longTexts.length >= 2 && !block3) block3 = longTexts[1].text;
      }}
    }} catch (e) {{ Logger.log('getOrgBlockTextsFromSlide_エラー: ' + e.message); }}
    return {{ block2: block2, block3: block3 }};
  }};

  // 組織別分析の特徴・強み・弱みを生成する関数
  const generateOrgCharacteristics = function(org) {{
    // 組織の特徴を生成（簡易版、BOM対応）
    const orgName = getVal_(org, ['部署', '\\uFEFF部署', '組織名', '\\uFEFF組織名']) || '';
    const totalScore = parseFloat(getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || '0');
    return orgName + 'の総合スコアは' + totalScore + '点です。';
  }};
  
  const identifyOrgStrengths = function(org) {{
    // 各スキル軸のスコアを取得（CSVの列名に合わせる、BOM対応）
    const skillNames = {{
      research: 'リサーチ・分析力',
      concept: '構想・コンセプト力',
      delivery: '具体化・検証力',
      communication: '伝達・構造化力',
      implementation: '実現・ディレクション力'
    }};
    const skillDescs = {{
      research: '顧客や関係者へのヒアリングで深い洞察を得る能力が高く、課題の本質を把握できている',
      concept: '独自の視点から解決策を定義する能力が向上し、革新的なアイデア創出が可能になっている',
      delivery: 'プロトタイプを素早く作成し、検証サイクルを効果的に回す能力が高い',
      communication: '会議やプレゼンテーションでの合意形成がスムーズで、ファシリテーションスキルが確立されている',
      implementation: 'プロジェクト推進におけるリーダーシップが発揮され、他者を巻き込む能力が向上している'
    }};
    const skills = [
      {{ key: 'research', name: skillNames.research, score: parseFloat(getVal_(org, ['リサーチ', '\\uFEFFリサーチ', 'リサーチ・分析力']) || '0'), desc: skillDescs.research }},
      {{ key: 'concept', name: skillNames.concept, score: parseFloat(getVal_(org, ['構想', '\\uFEFF構想', '構想・コンセプト力']) || '0'), desc: skillDescs.concept }},
      {{ key: 'delivery', name: skillNames.delivery, score: parseFloat(getVal_(org, ['具体化', '\\uFEFF具体化', '具体化・検証力']) || '0'), desc: skillDescs.delivery }},
      {{ key: 'communication', name: skillNames.communication, score: parseFloat(getVal_(org, ['伝達', '\\uFEFF伝達', '伝達・構造化力']) || '0'), desc: skillDescs.communication }},
      {{ key: 'implementation', name: skillNames.implementation, score: parseFloat(getVal_(org, ['実現', '\\uFEFF実現', '実現・ディレクション力']) || '0'), desc: skillDescs.implementation }}
    ];
    const valid = skills.filter(function(s) {{ return s.score > 0; }});
    if (valid.length === 0) return '';
    const avg = valid.reduce(function(a, s) {{ return a + s.score; }}, 0) / valid.length;
    let strengths = valid.filter(function(s) {{ return s.score > avg; }}).sort(function(a, b) {{ return b.score - a.score; }});
    if (strengths.length === 0) {{
      strengths = [valid.reduce(function(a, b) {{ return a.score >= b.score ? a : b; }})];
    }}
    return strengths.slice(0, 2).map(function(s) {{ return s.name + '（' + s.score.toFixed(2) + '点）: ' + s.desc; }}).join('\\n');
  }};
  
  const identifyOrgWeaknesses = function(org) {{
    // 各スキル軸のスコアを取得（CSVの列名に合わせる、BOM対応）
    const scores = {{
      research: parseFloat(getVal_(org, ['リサーチ', '\\uFEFFリサーチ', 'リサーチ・分析力']) || '0'),
      concept: parseFloat(getVal_(org, ['構想', '\\uFEFF構想', '構想・コンセプト力']) || '0'),
      delivery: parseFloat(getVal_(org, ['具体化', '\\uFEFF具体化', '具体化・検証力']) || '0'),
      communication: parseFloat(getVal_(org, ['伝達', '\\uFEFF伝達', '伝達・構造化力']) || '0'),
      implementation: parseFloat(getVal_(org, ['実現', '\\uFEFF実現', '実現・ディレクション力']) || '0')
    }};
    
    // 最低スコアのスキルを弱みとして返す
    let minScore = 999;
    let minSkill = '';
    for (const skill in scores) {{
      if (scores[skill] < minScore && scores[skill] > 0) {{
        minScore = scores[skill];
        const skillNames = {{
          research: 'リサーチ・分析力',
          concept: '構想・コンセプト力',
          delivery: '具体化・検証力',
          communication: '伝達・構造化力',
          implementation: '実現・ディレクション力'
        }};
        minSkill = skillNames[skill] || skill;
      }}
    }}
    
    if (minScore < 999) {{
      return minSkill + '（' + minScore.toFixed(2) + '点）';
    }}
    return '';
  }};
  
  // 全ての組織についてスライドを生成（CSVの順序通り：営業→企画→開発）
  // 各組織の情報をORGANIZATION_DATAから取得して、直接置換する
  for (let i = 0; i < orgData.length; i++) {{
    const org = orgData[i];
    const orgName = getVal_(org, ['部署', '\\uFEFF部署', '組織名', '\\uFEFF組織名']) || '';
    Logger.log('組織別スライドを生成中: ' + orgName + ' (インデックス: ' + i + ')');
    
    // ORGANIZATION_DATAから組織の情報を取得（スライド挿入内容Markdownから）
    let orgDataFromMarkdown = null;
    if (ORGANIZATION_DATA && ORGANIZATION_DATA.length > 0) {{
      // CSVの組織名と一致する組織データを探す
      for (let j = 0; j < ORGANIZATION_DATA.length; j++) {{
        if (ORGANIZATION_DATA[j].name === orgName || 
            ORGANIZATION_DATA[j].O_overall_score_name === orgName) {{
          orgDataFromMarkdown = ORGANIZATION_DATA[j];
          Logger.log('組織データを発見（Markdown）: ' + orgName);
          Logger.log('  O_overall_score_name: ' + (orgDataFromMarkdown.O_overall_score_name || 'N/A'));
          Logger.log('  O_score: ' + (orgDataFromMarkdown.O_score || 'N/A'));
          break;
        }}
      }}
      if (!orgDataFromMarkdown) {{
        Logger.log('警告: 組織データが見つかりません（Markdown）: ' + orgName);
        Logger.log('  ORGANIZATION_DATAの組織名: ' + ORGANIZATION_DATA.map(function(org) {{ return org.name || org.O_overall_score_name; }}).join(', '));
      }}
    }} else {{
      Logger.log('警告: ORGANIZATION_DATAが空です');
    }}
    
    // スライド挿入内容Markdownから取得したデータを使用（なければCSVから生成）
    const getOgr = (letter, num) => orgDataFromMarkdown ? (orgDataFromMarkdown['Ogr' + letter + '_' + num] || '') : '';
    const orgDict = {{
      [PLACEHOLDER_MAP.O_OVERALL_SCORE_NAME]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_overall_score_name || orgName) : orgName,
      [PLACEHOLDER_MAP.O_OVERALL_SCORE]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_score || getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || '') : (getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || ''),
      [PLACEHOLDER_MAP.O_SCORE]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_score || getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || '') : (getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || ''),
      [PLACEHOLDER_MAP.O_RESPONDENTS_1]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_respondents_1 || '') : (getVal_(org, ['人数', '\\uFEFF人数']) || ''),
      [PLACEHOLDER_MAP.OrkA_1]: orgDataFromMarkdown ? (orgDataFromMarkdown.OrkA_1 || '') : '',
      [PLACEHOLDER_MAP.OgrA_1]: getOgr('A', 1), [PLACEHOLDER_MAP.OgrA_2]: getOgr('A', 2), [PLACEHOLDER_MAP.OgrA_3]: getOgr('A', 3), [PLACEHOLDER_MAP.OgrA_4]: getOgr('A', 4), [PLACEHOLDER_MAP.OgrA_5]: getOgr('A', 5),
      [PLACEHOLDER_MAP.OgrB_1]: getOgr('B', 1), [PLACEHOLDER_MAP.OgrB_2]: getOgr('B', 2), [PLACEHOLDER_MAP.OgrB_3]: getOgr('B', 3), [PLACEHOLDER_MAP.OgrB_4]: getOgr('B', 4), [PLACEHOLDER_MAP.OgrB_5]: getOgr('B', 5),
      [PLACEHOLDER_MAP.OgrC_1]: getOgr('C', 1), [PLACEHOLDER_MAP.OgrC_2]: getOgr('C', 2), [PLACEHOLDER_MAP.OgrC_3]: getOgr('C', 3), [PLACEHOLDER_MAP.OgrC_4]: getOgr('C', 4), [PLACEHOLDER_MAP.OgrC_5]: getOgr('C', 5),
      [PLACEHOLDER_MAP.OgrD_1]: getOgr('D', 1), [PLACEHOLDER_MAP.OgrD_2]: getOgr('D', 2), [PLACEHOLDER_MAP.OgrD_3]: getOgr('D', 3), [PLACEHOLDER_MAP.OgrD_4]: getOgr('D', 4), [PLACEHOLDER_MAP.OgrD_5]: getOgr('D', 5),
      [PLACEHOLDER_MAP.OgrE_1]: getOgr('E', 1), [PLACEHOLDER_MAP.OgrE_2]: getOgr('E', 2), [PLACEHOLDER_MAP.OgrE_3]: getOgr('E', 3), [PLACEHOLDER_MAP.OgrE_4]: getOgr('E', 4), [PLACEHOLDER_MAP.OgrE_5]: getOgr('E', 5),
      [PLACEHOLDER_MAP.OgrF_1]: getOgr('F', 1), [PLACEHOLDER_MAP.OgrF_2]: getOgr('F', 2), [PLACEHOLDER_MAP.OgrF_3]: getOgr('F', 3), [PLACEHOLDER_MAP.OgrF_4]: getOgr('F', 4), [PLACEHOLDER_MAP.OgrF_5]: getOgr('F', 5),
      [PLACEHOLDER_MAP.O_BLOCK_1_BODY]: '',  // 廃止（空で置換）
      [PLACEHOLDER_MAP.O_BLOCK_2_BODY]: (orgDataFromMarkdown && orgDataFromMarkdown.O_block_2_body) ? formatText_(orgDataFromMarkdown.O_block_2_body) : formatText_(identifyOrgStrengths(org)),
      [PLACEHOLDER_MAP.O_BLOCK_3_BODY]: orgDataFromMarkdown ? formatText_(orgDataFromMarkdown.O_block_3_body || '') : formatText_(identifyOrgWeaknesses(org)),
      [PLACEHOLDER_MAP.ORGANIZATION_NAME]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_overall_score_name || orgName) : orgName,
      [PLACEHOLDER_MAP.BLOCK_1_BODY]: '',  // 廃止（空で置換）
      [PLACEHOLDER_MAP.OVERALL_SCORE]: orgDataFromMarkdown ? (orgDataFromMarkdown.O_score || getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || '') : (getVal_(org, ['総合スコア', '\\uFEFF総合スコア']) || ''),
      [PLACEHOLDER_MAP.BLOCK_2_BODY]: (orgDataFromMarkdown && orgDataFromMarkdown.O_block_2_body) ? formatText_(orgDataFromMarkdown.O_block_2_body) : formatText_(identifyOrgStrengths(org)),
      [PLACEHOLDER_MAP.BLOCK_3_BODY]: orgDataFromMarkdown ? formatText_(orgDataFromMarkdown.O_block_3_body || '') : formatText_(identifyOrgWeaknesses(org))
    }};
    
    // 全組織で「プレースホルダー入りテンプレート」を複製し、複製にだけプレースホルダー置換（値ベース replaceAllText は行わない）
    Logger.log('  -> テンプレートスライドを複製してプレースホルダー置換');
    const newSlide = templateSlide.duplicate();
    replacePlaceholdersInSlide_(newSlide, orgDict);

    try {{
      const newNotes = newSlide.getNotesPage();
      const newNotesText = newNotes.getSpeakerNotesShape().getText().asString();
      if (newNotesText.indexOf('[AUTO_ORG_SLIDE]') === -1) {{
        newNotes.getSpeakerNotesShape().getText().appendText('\\n[AUTO_ORG_SLIDE]');
      }}
    }} catch (e) {{
      Logger.log('新規スライドのスピーカーノート設定エラー: ' + e.message);
    }}

    if (i === 0) {{
      // 1枚目: 複製を templateSlideIndex に、テンプレートをその次に移動（テンプレは常にプレースホルダー残す）
      try {{
        const tn = templateSlide.getNotesPage().getSpeakerNotesShape().getText();
        if (tn.asString().indexOf('[AUTO_ORG_SLIDE_TEMPLATE]') === -1) {{
          tn.appendText('\\n[AUTO_ORG_SLIDE_TEMPLATE]');
        }}
      }} catch (e) {{ Logger.log('テンプレートマーカー追加: ' + e.message); }}
      templateSlide.move(templateSlideIndex + 1);
      newSlide.move(templateSlideIndex);
      templateSlide = presentation.getSlides()[templateSlideIndex + 1];  // 以降のループで複製元を参照
    }} else {{
      // 2枚目以降: 複製を templateSlideIndex+i に、テンプレートをその次に
      const targetIdx = templateSlideIndex + i;
      newSlide.move(targetIdx);
      templateSlide.move(targetIdx + 1);
      templateSlide = presentation.getSlides()[targetIdx + 1];
    }}
  }}
  
  Logger.log('=== 組織別分析スライド生成完了: ' + orgData.length + '枚 ===');
}}

/**
 * テキストをフォーマット（Markdown記号を除去してプレーンテキストに変換）
 */
function formatText_(text) {{
  if (!text) {{
    return '';
  }}
  
  let formatted = text.toString();
  
  // Markdownのリスト記号を除去（行頭の - や * を除去）
  formatted = formatted.replace(/^[-*]\\s+/gm, '');
  
  // **太字** を除去（内容は残す）
  formatted = formatted.replace(/\\*\\*([^*]+)\\*\\*/g, '$1');
  
  // コードブロック記号を除去
  formatted = formatted.replace(/```[\\s\\S]*?```/g, '');
  formatted = formatted.replace(/`([^`]+)`/g, '$1');
  
  // リンク形式を除去 [text](url) -> text
  formatted = formatted.replace(/\\[([^\\]]+)\\]\\([^\\)]+\\)/g, '$1');
  
  // 余分な空白行を削減（3つ以上の連続した改行を2つに）
  formatted = formatted.replace(/\\n{3,}/g, '\\n\\n');
  
  // 前後の空白を除去
  formatted = formatted.trim();
  
  return formatted;
}}

// ============================================
// プレースホルダー置換
// ============================================

/**
 * 特定のスライド内のプレースホルダーを置換（簡素化版：slide.replaceAllText()ベース）
 * テーブル・グループ内でも確実に置換される
 */
function replacePlaceholdersInSlide_(slide, dict) {{
  let replacedCount = 0;
  
  // 各プレースホルダーを slide.replaceAllText() で置換
  // replaceAllText() はスライド内の全要素（テキストボックス、テーブル、グループ）を自動的に処理する
  // 空文字でも置換する（廃止プレースホルダー {{O_block_1_body}} 等を空で置換するため。14_組織別スライド_表プレースホルダー置換要件 R4）
  for (const key in dict) {{
    let value = dict[key];
    if (value !== null && value !== undefined) {{
      // \\n を実際の改行文字に変換（スライド上で改行として表示するため）
      if (typeof value === 'string') {{
        value = value.replace(/\\\\n/g, '\\n');
      }}
      try {{
        // slide.replaceAllText() を使用（テーブル・グループ内も自動的に処理される）
        slide.replaceAllText(key, value);
        replacedCount++;
      }} catch (e) {{
        Logger.log('replaceAllText()エラー: ' + key + ' - ' + e.message);
        // エラーが発生した場合は、個別のShape/Tableを処理（フォールバック）
        try {{
          const shapes = slide.getShapes();
          for (let i = 0; i < shapes.length; i++) {{
            const shape = shapes[i];
            const shapeType = shape.getShapeType();
            
            // テーブルの処理
            if (shapeType === SlidesApp.ShapeType.TABLE) {{
              try {{
                const table = shape.asTable();
                const numRows = table.getNumRows();
                const numCols = table.getNumColumns();
                
                for (let row = 0; row < numRows; row++) {{
                  for (let col = 0; col < numCols; col++) {{
                    try {{
                      const cell = table.getCell(row, col);
                      const textRange = cell.getText();
                      if (textRange) {{
                        textRange.replaceAllText(key, value);
                      }}
                    }} catch (e) {{
                      // セル取得エラーは無視
                    }}
                  }}
                }}
              }} catch (e) {{
                Logger.log('テーブル処理エラー: ' + e.message);
              }}
            }} else {{
              // 通常のShapeの処理
              try {{
                const textRange = shape.getText();
                if (textRange) {{
                  textRange.replaceAllText(key, value);
                }}
              }} catch (e) {{
                // テキストがないShapeは無視
              }}
            }}
          }}
          
          // テーブルを直接取得して処理（getShapes()で取得できない場合に備える）
          try {{
            const tables = slide.getTables();
            if (tables && tables.length > 0) {{
              for (let t = 0; t < tables.length; t++) {{
                const table = tables[t];
                const numRows = table.getNumRows();
                const numCols = table.getNumColumns();
                
                for (let row = 0; row < numRows; row++) {{
                  for (let col = 0; col < numCols; col++) {{
                    try {{
                      const cell = table.getCell(row, col);
                      const textRange = cell.getText();
                      if (textRange) {{
                        textRange.replaceAllText(key, value);
                      }}
                    }} catch (e) {{
                      // セル取得エラーは無視
                    }}
                  }}
                }}
              }}
            }}
          }} catch (e) {{
            Logger.log('getTables()エラー: ' + e.message);
          }}
        }} catch (e2) {{
          Logger.log('フォールバック処理エラー: ' + e2.message);
        }}
      }}
    }}
  }}
  
  if (replacedCount > 0) {{
    Logger.log('置換完了: ' + replacedCount + '種類のプレースホルダー');
  }}
}}

/**
 * BOM対応：オブジェクトから値を安全に取得（複数のキー候補を試す）
 */
function getVal_(obj, keys) {{
  if (!obj || !keys || keys.length === 0) {{
    return undefined;
  }}
  
  for (let i = 0; i < keys.length; i++) {{
    const key = keys[i];
    if (obj.hasOwnProperty(key)) {{
      return obj[key];
    }}
  }}
  
  return undefined;
}}

/**
 * 正規表現の特殊文字をエスケープ
 */
function escapeRegExp_(str) {{
  return str.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
}}

/**
 * 表紙の日付を置換（テーブル内も含む、最適化版）
 */
function replaceDateOnCover_(presentation, reportDate) {{
  const coverSlide = presentation.getSlides()[SLIDE_INDEX.COVER];
  if (!coverSlide) {{
    return;
  }}
  
  // 日付のプレースホルダーを事前にコンパイル（パフォーマンス向上）
  const datePlaceholders = [
    '{{{{date}}}}',
    '{{{{reportDate}}}}',
    '{{{{日付}}}}'
  ];
  const dateRegexes = datePlaceholders.map(function(placeholder) {{
    return new RegExp(escapeRegExp_(placeholder), 'g');
  }});
  
  // 日付形式のパターン（例: 2025.01.01 *変えてね）
  const datePatternRegex = /\\d{{4}}\\.\\d{{2}}\\.\\d{{2}}[\\s\\*]*変えてね/g;
  
  // テキスト置換関数
  const replaceDateInText = function(textRange, text) {{
    if (!text || text.trim() === '') {{
      return false;
    }}
    
    let modifiedText = text;
    let hasChanges = false;
    
    // プレースホルダーを置換
    for (let i = 0; i < dateRegexes.length; i++) {{
      if (text.indexOf(datePlaceholders[i]) !== -1) {{
        modifiedText = modifiedText.replace(dateRegexes[i], reportDate);
        hasChanges = true;
      }}
    }}
    
    // 日付形式のパターンも置換
    if (datePatternRegex.test(modifiedText)) {{
      modifiedText = modifiedText.replace(datePatternRegex, reportDate);
      hasChanges = true;
    }}
    
    if (hasChanges) {{
      try {{
        textRange.setText(modifiedText);
        return true;
      }} catch (e) {{
        Logger.log('日付テキスト設定エラー: ' + e.message);
        return false;
      }}
    }}
    return false;
  }};
  
  const shapes = coverSlide.getShapes();
  for (let i = 0; i < shapes.length; i++) {{
    const shape = shapes[i];
    const shapeType = shape.getShapeType();
    
    // テーブル内の日付プレースホルダーも処理
    if (shapeType === SlidesApp.ShapeType.TABLE) {{
      try {{
        const table = shape.asTable();
        const numRows = table.getNumRows();
        const numCols = table.getNumColumns();
        
        for (let row = 0; row < numRows; row++) {{
          for (let col = 0; col < numCols; col++) {{
            try {{
              const cell = table.getCell(row, col);
              const textRange = cell.getText();
              if (textRange) {{
                const text = textRange.asString();
                replaceDateInText(textRange, text);
              }}
            }} catch (e) {{
              // セル取得エラーは無視
            }}
          }}
        }}
      }} catch (e) {{
        Logger.log('テーブル内日付置換エラー: ' + e.message);
      }}
    }}
    // 通常のShape（テキストボックスなど）の日付プレースホルダーを処理
    else if (shapeType === SlidesApp.ShapeType.TEXT_BOX ||
        shapeType === SlidesApp.ShapeType.AUTO_SHAPE ||
        shapeType === SlidesApp.ShapeType.SHAPE) {{
      try {{
        const textRange = shape.getText();
        if (textRange) {{
          const text = textRange.asString();
          replaceDateInText(textRange, text);
        }}
      }} catch (e) {{
        // エラーのみログ出力
        // Logger.log('日付置換エラー: ' + e.message);
      }}
    }}
  }}
}}

// ============================================
// 画像挿入
// ============================================

/**
 * プレースホルダーテキストの位置に画像を挿入
 */
function insertImageAtPlaceholder_(slide, placeholderText, imageBlob) {{
  if (!imageBlob) {{
    Logger.log('画像Blobがありません: ' + placeholderText);
    return;
  }}
  
  Logger.log('画像挿入を開始: プレースホルダー = ' + placeholderText);
  
  const shapes = slide.getShapes();
  let targetShape = null;
  let foundInTable = false;
  let tableCellInfo = null;
  
  // プレースホルダーテキストを含むShapeを検索（再帰的）
  const searchShape = function(shape, isGroupChild) {{
    try {{
      const shapeType = shape.getShapeType();
      
      // テーブル内を検索
      if (shapeType === SlidesApp.ShapeType.TABLE) {{
        try {{
          const table = shape.asTable();
          const numRows = table.getNumRows();
          const numCols = table.getNumColumns();
          
          for (let row = 0; row < numRows; row++) {{
            for (let col = 0; col < numCols; col++) {{
              const cell = table.getCell(row, col);
              const textRange = cell.getText();
              if (textRange) {{
                const cellText = textRange.asString();
                if (cellText && cellText.indexOf(placeholderText) !== -1) {{
                  tableCellInfo = {{
                    left: cell.getLeft(),
                    top: cell.getTop(),
                    width: cell.getWidth(),
                    height: cell.getHeight(),
                    cell: cell
                  }};
                  foundInTable = true;
                  Logger.log('テーブル内でプレースホルダーを発見: ' + placeholderText + ' (セル: ' + row + ', ' + col + ')');
                  return true;
                }}
              }}
            }}
          }}
        }} catch (e) {{
          Logger.log('テーブル検索エラー: ' + e.message);
        }}
      }}
      
      // 通常のShapeを検索
      if (shapeType === SlidesApp.ShapeType.TEXT_BOX ||
          shapeType === SlidesApp.ShapeType.AUTO_SHAPE ||
          shapeType === SlidesApp.ShapeType.SHAPE ||
          shapeType === SlidesApp.ShapeType.LINE ||
          shapeType === SlidesApp.ShapeType.UNSUPPORTED) {{
        try {{
          const textRange = shape.getText();
          if (textRange) {{
            const text = textRange.asString();
            if (text && text.indexOf(placeholderText) !== -1) {{
              targetShape = shape;
              Logger.log('Shape内でプレースホルダーを発見: ' + placeholderText + ' (ShapeType: ' + shapeType + ')');
              return true;
            }}
          }}
        }} catch (e) {{
          // テキストがないShapeは無視
        }}
      }}
      
      // グループ化されたShapeの場合、子要素も検索
      if (shapeType === SlidesApp.ShapeType.GROUP) {{
        try {{
          const group = shape.asGroup();
          const childShapes = group.getChildren();
          for (let j = 0; j < childShapes.length; j++) {{
            if (searchShape(childShapes[j], true)) {{
              return true;
            }}
          }}
        }} catch (e) {{
          Logger.log('グループ検索エラー: ' + e.message);
        }}
      }}
    }} catch (e) {{
      Logger.log('Shape検索エラー: ' + e.message);
    }}
    return false;
  }};
  
  // 全てのShapeを検索
  for (let i = 0; i < shapes.length; i++) {{
    if (searchShape(shapes[i], false)) {{
      break;
    }}
  }}
  
  // テーブルセル内で見つかった場合
  if (foundInTable && tableCellInfo) {{
    try {{
      tableCellInfo.cell.getText().setText('');
      slide.insertImage(imageBlob, tableCellInfo.left, tableCellInfo.top, 
                        tableCellInfo.width, tableCellInfo.height);
      Logger.log('画像をテーブルセルに挿入しました: ' + placeholderText);
      return;
    }} catch (e) {{
      Logger.log('テーブルセルへの画像挿入エラー: ' + e.message);
    }}
  }}
  
  // 通常のShapeで見つかった場合
  if (targetShape) {{
    try {{
      const left = targetShape.getLeft();
      const top = targetShape.getTop();
      const width = targetShape.getWidth();
      const height = targetShape.getHeight();
      
      targetShape.remove();
      slide.insertImage(imageBlob, left, top, width, height);
      Logger.log('画像をShapeに挿入しました: ' + placeholderText);
      return;
    }} catch (e) {{
      Logger.log('Shapeへの画像挿入エラー: ' + e.message);
    }}
  }}
  
  Logger.log('プレースホルダーが見つかりません: ' + placeholderText);
}}
'''
    
    return gas_code



