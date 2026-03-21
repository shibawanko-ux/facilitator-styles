"""
実践スキル定着度 分析レポート生成システム
Flask Webアプリケーション版
"""
import os
import csv
import sys
import io
from flask import Flask, render_template, request, send_from_directory, send_file, Response, jsonify
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 日本語フォントの設定
import platform
try:
    system = platform.system()
    if system == 'Darwin':  # macOS
        plt.rcParams['font.family'] = 'Hiragino Sans'
    elif system == 'Windows':
        plt.rcParams['font.family'] = 'Yu Gothic'
    else:  # Linux
        plt.rcParams['font.family'] = 'Noto Sans CJK JP'
except Exception as e:
    print(f"日本語フォント設定エラー: {e}")
    # エラーが発生しても処理は継続
    pass

from src.analyzer import (
    detect_phase, validate_email_consistency, analyze_phase1, analyze_phase2, analyze_phase3,
    analyze_by_department, analyze_individual_progress, analyze_manager_comparison
)
from src.report_generator import (
    generate_report_markdown, generate_executive_summary_csv,
    generate_department_analysis_csv, generate_satisfaction_analysis_csv,
    generate_practice_frequency_csv, generate_individual_progress_csv,
    generate_manager_comparison_csv, generate_question_comparison_csv,
    generate_slide_content_markdown, generate_individual_report_markdown,
    generate_individual_slide_content_markdown,
    generate_post_action_items_csv, generate_follow_practice_confirmation_csv
)
from src.gas_generator import generate_gas_code
from src.individual_gas_generator import generate_individual_gas_code
from src.project_manager import (
    get_project_list, get_or_create_project, get_project_name,
    update_project_timestamp, get_project_upload_dir, get_project_report_dir,
    get_project_export_dir, delete_project
)
from src.csv_normalizer import normalize_participant_csv, normalize_manager_csv

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
EXPORT_DIR = os.path.join(BASE_DIR, 'spreadsheet_export')

for d in (UPLOAD_DIR, REPORT_DIR, EXPORT_DIR):
    os.makedirs(d, exist_ok=True)

app = Flask(__name__, template_folder='templates_html')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

REQUIRED_FILES = {
    'pre': '実施前.csv',
    'post': '直後.csv',
    'follow': '1ヶ月後.csv',
    'manager': '上長1ヶ月後.csv',
}

# ---- ユーティリティ ----


def xlsx_to_csv_bytes(file_storage) -> bytes:
    """アップロードされた .xlsx ファイルを CSV のバイト列に変換して返す。"""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(file_storage.read()), data_only=True)
    ws = wb.active
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in ws.iter_rows(values_only=True):
        writer.writerow(['' if v is None else str(v) for v in row])
    return buf.getvalue().encode('utf-8-sig')


def save_uploaded_file(file, save_path: str) -> None:
    """アップロードファイルを保存する。xlsx の場合は CSV に変換してから保存する。"""
    filename = file.filename.lower()
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        csv_bytes = xlsx_to_csv_bytes(file)
        with open(save_path, 'wb') as f:
            f.write(csv_bytes)
    else:
        file.save(save_path)


def load_csv(path):
    """CSVファイルを読み込む"""
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def generate_radar_from_csv(exec_summary_csv_path, gap_csv_path=None, out_path='radar.png', phase=1):
    """CSVデータからレーダーチャートを生成"""
    import csv
    
    if not os.path.exists(exec_summary_csv_path):
        raise FileNotFoundError(f"エグゼクティブサマリーCSVが見つかりません: {exec_summary_csv_path}")
    
    # エグゼクティブサマリーCSVを読み込む
    pre_scores = {}
    post_scores = None
    follow_scores = None
    
    with open(exec_summary_csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        # スキル軸のマッピング
        skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
        skill_names_csv = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
        
        for row in rows:
            item = row.get('項目', '').strip()
            # 総合スコア行はスキップ
            if item == '総合スコア':
                continue
            
            # スキル軸を特定
            skill_idx = None
            for i, name in enumerate(skill_names_csv):
                if item == name:
                    skill_idx = i
                    break
            
            if skill_idx is not None:
                key = skill_keys[skill_idx]
                
                # 実施前
                pre_val = row.get('実施前', '').strip()
                if pre_val and pre_val != '-':
                    try:
                        pre_scores[key] = float(pre_val)
                    except (ValueError, TypeError):
                        pass
                
                # 直後
                if phase >= 2:
                    post_val = row.get('直後', '').strip()
                    if post_val and post_val != '-':
                        if post_scores is None:
                            post_scores = {}
                        try:
                            post_scores[key] = float(post_val)
                        except (ValueError, TypeError):
                            pass
                
                # 1ヶ月後
                if phase == 3:
                    follow_val = row.get('1ヶ月後', '').strip()
                    if follow_val and follow_val != '-':
                        if follow_scores is None:
                            follow_scores = {}
                        try:
                            follow_scores[key] = float(follow_val)
                        except (ValueError, TypeError):
                            pass
    
    # 上長評価をギャップ分析CSVから読み込む（Phase 3のみ）
    manager_scores = None
    if phase == 3 and gap_csv_path and os.path.exists(gap_csv_path):
        with open(gap_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            skill_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
            skill_names_csv = ['リサーチ・分析力', '構想・コンセプト力', '具体化・検証力', '伝達・構造化力', '実現・ディレクション力']
            
            manager_scores = {}
            for row in rows:
                skill_axis = row.get('スキル軸', '').strip()
                skill_idx = None
                for i, name in enumerate(skill_names_csv):
                    if skill_axis == name:
                        skill_idx = i
                        break
                
                if skill_idx is not None:
                    key = skill_keys[skill_idx]
                    mgr_val = row.get('上長評価', '').strip()
                    if mgr_val and mgr_val != '-':
                        try:
                            manager_scores[key] = float(mgr_val)
                        except (ValueError, TypeError):
                            pass
    
    # レーダーチャートを生成（すべてのスキル軸が揃っていることを確認）
    if len(pre_scores) != 5:
        raise ValueError(f"実施前のスコアが不完全です。5スキル軸すべてが必要です。取得できたスキル軸: {list(pre_scores.keys())}")
    
    generate_radar(pre_scores, post_scores, follow_scores, manager_scores, out_path)


def generate_radar(pre_scores, post_scores=None, follow_scores=None, manager_scores=None, out_path='radar.png'):
    """レーダーチャートを生成"""
    from src.analyzer import SKILL_AXES
    
    categories = [axis['name'] for axis in SKILL_AXES]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    
    def wrap(vals):
        vals = vals[:]
        vals.append(vals[0])
        ang = angles + angles[:1]
        return vals, ang
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    score_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    
    # 実施前
    pre_vals = [pre_scores[key] for key in score_keys]
    pre_vals_wrapped, ang = wrap(pre_vals)
    ax.plot(ang, pre_vals_wrapped, 'o-', linewidth=2.5, label='実施前', color='#3498db', markersize=8)
    ax.fill(ang, pre_vals_wrapped, alpha=0.25, color='#3498db')
    
    # 直後
    if post_scores:
        post_vals = [post_scores[key] for key in score_keys]
        post_vals_wrapped, _ = wrap(post_vals)
        ax.plot(ang, post_vals_wrapped, 'o-', linewidth=2.5, label='直後', color='#e67e22', markersize=8)
        ax.fill(ang, post_vals_wrapped, alpha=0.25, color='#e67e22')
    
    # 1ヶ月後
    if follow_scores:
        follow_vals = [follow_scores[key] for key in score_keys]
        follow_vals_wrapped, _ = wrap(follow_vals)
        ax.plot(ang, follow_vals_wrapped, 'o-', linewidth=2.5, label='1ヶ月後', color='#27ae60', markersize=8)
        ax.fill(ang, follow_vals_wrapped, alpha=0.25, color='#27ae60')
    
    # 上長評価
    if manager_scores:
        manager_vals = [manager_scores[key] for key in score_keys]
        manager_vals_wrapped, _ = wrap(manager_vals)
        ax.plot(ang, manager_vals_wrapped, 'o-', linewidth=2.5, label='上長1ヶ月後', color='#9b59b6', markersize=8)
        ax.fill(ang, manager_vals_wrapped, alpha=0.25, color='#9b59b6')
    
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7, linewidth=1)
    plt.title('全社スキル定着度推移', size=16, pad=20, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def generate_individual_radar(person_data, manager_scores=None, out_path='radar.png', person_name='', phase=2):
    """個人別レーダーチャートを生成"""
    from src.analyzer import SKILL_AXES
    
    categories = [axis['name'] for axis in SKILL_AXES]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    
    def wrap(vals):
        vals = vals[:]
        vals.append(vals[0])
        ang = angles + angles[:1]
        return vals, ang
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    score_keys = ['research', 'concept', 'delivery', 'communication', 'implementation']
    
    pre_scores = person_data.get('pre', {})
    post_scores = person_data.get('post')
    follow_scores = person_data.get('follow')
    
    # Phase2の場合はfollow_scoresを無視
    if phase == 2:
        follow_scores = None
    
    # 実施前
    if pre_scores:
        pre_vals = [pre_scores.get(key, 0) for key in score_keys]
        pre_vals_wrapped, ang = wrap(pre_vals)
        ax.plot(ang, pre_vals_wrapped, 'o-', linewidth=2.5, label='実施前', color='#3498db', markersize=8)
        ax.fill(ang, pre_vals_wrapped, alpha=0.25, color='#3498db')
    
    # 直後
    if post_scores:
        post_vals = [post_scores.get(key, 0) for key in score_keys]
        post_vals_wrapped, _ = wrap(post_vals)
        ax.plot(ang, post_vals_wrapped, 'o-', linewidth=2.5, label='直後', color='#e67e22', markersize=8)
        ax.fill(ang, post_vals_wrapped, alpha=0.25, color='#e67e22')
    
    # 1ヶ月後（Phase3のみ）
    if phase == 3 and follow_scores:
        follow_vals = [follow_scores.get(key, 0) for key in score_keys]
        follow_vals_wrapped, _ = wrap(follow_vals)
        ax.plot(ang, follow_vals_wrapped, 'o-', linewidth=2.5, label='1ヶ月後', color='#27ae60', markersize=8)
        ax.fill(ang, follow_vals_wrapped, alpha=0.25, color='#27ae60')
    
    # 上長評価（Phase 3のみ）
    if phase == 3 and manager_scores:
        manager_vals = [manager_scores.get(key, 0) for key in score_keys]
        manager_vals_wrapped, _ = wrap(manager_vals)
        ax.plot(ang, manager_vals_wrapped, 'o-', linewidth=2.5, label='上長1ヶ月後', color='#9b59b6', markersize=8)
        ax.fill(ang, manager_vals_wrapped, alpha=0.25, color='#9b59b6')
    
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7, linewidth=1)
    
    # タイトルに個人名を含める
    title = f'{person_name}様 スキル定着度推移' if person_name else '個人スキル定着度推移'
    plt.title(title, size=16, pad=20, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def write_file_if_different(file_path, new_content):
    """ファイルが存在し、内容が同じ場合は上書きしない"""
    import hashlib
    new_content_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()
    should_overwrite = True
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            existing_hash = hashlib.md5(existing_content.encode('utf-8')).hexdigest()
            if existing_hash == new_content_hash:
                # 同じ内容なので上書きしない
                should_overwrite = False
        except Exception:
            # 読み込みエラー時は上書き
            pass
    
    overwrite_skipped = False
    if should_overwrite:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        overwrite_skipped = True
    
    return overwrite_skipped


def generate_phase_report(phase, pre_data, post_data, follow_data, manager_data,
                          project_id, project_name, project_report_dir, project_export_dir,
                          skip_slide_content_write=False):
    """特定のPhaseのレポートを生成（ヘルパー関数）
    skip_slide_content_write=True のときはスライド挿入内容MDを上書きしない（既存の手動編集を保持したままGAS再生成する場合に使用）。
    """
    import hashlib
    from src.report_generator import generate_gap_analysis_csv
    
    # 分析実行
    try:
        if phase == 1:
            analysis = analyze_phase1(pre_data)
        elif phase == 2:
            analysis = analyze_phase2(pre_data, post_data)
        else:  # phase == 3
            analysis = analyze_phase3(pre_data, post_data, follow_data, manager_data)
    except ValueError as e:
        return {'error': str(e)}
    
    # エグゼクティブサマリーCSV生成（Phaseごとに別ファイルにする必要があるか検討）
    # ギャップ分析（Phase 3のみ）- エグゼクティブサマリーCSV生成の前にパスを準備
    gap_path = None
    if phase == 3 and 'manager' in analysis:
        gap_path = os.path.join(project_export_dir, '03_ギャップ分析.csv')
        generate_gap_analysis_csv(analysis['follow'], analysis['manager'], gap_path, follow_data, manager_data)
    
    # 現状は共通ファイルを使用するため、Phaseごとに上書きされる可能性がある
    # レーダーチャート生成に必要
    exec_summary_path = os.path.join(project_export_dir, f'01_エグゼクティブサマリー_Phase{phase}.csv')
    generate_executive_summary_csv(phase, analysis, exec_summary_path, gap_csv_path=gap_path)
    
    # 満足度分析（Phase 2以上）- 直後.csvから取得されるため、Phaseごとに分ける必要はない
    sat_path = None
    if phase >= 2:
        sat_path = os.path.join(project_export_dir, '04_満足度分析.csv')
        try:
            generate_satisfaction_analysis_csv(analysis, sat_path, post_data)
        except Exception as e:
            print(f"満足度分析CSV生成エラー (Phase {phase}): {e}", file=sys.stderr)
    
    # レーダーチャート生成
    radar_filename = f'生成レポート_{project_name}_Phase{phase}_レーダーチャート.png'
    radar_path = os.path.join(project_report_dir, radar_filename)
    
    # Phase 3で上長評価データがある場合とない場合の2つのレーダーチャートを生成
    radar_path_with_manager = None
    if phase == 3:
        # 上長評価なしのレーダーチャート（通常版）
        generate_radar_from_csv(exec_summary_path, None, radar_path, phase)
        
        # 上長評価データがある場合、上長評価を含むレーダーチャートも生成
        if gap_path and os.path.exists(gap_path):
            radar_filename_with_manager = f'生成レポート_{project_name}_Phase{phase}_上長評価含む_レーダーチャート.png'
            radar_path_with_manager = os.path.join(project_report_dir, radar_filename_with_manager)
            generate_radar_from_csv(exec_summary_path, gap_path, radar_path_with_manager, phase)
    else:
        # Phase 1, 2の場合は通常のレーダーチャートのみ
        generate_radar_from_csv(exec_summary_path, gap_path, radar_path, phase)
    
    # 組織別分析
    dept_data = pre_data
    if phase == 3 and follow_data:
        dept_data = follow_data
    elif phase >= 2 and post_data:
        dept_data = post_data
    
    dept_analysis = analyze_by_department(dept_data)
    dept_path = None
    if dept_analysis:
        dept_path = os.path.join(project_export_dir, f'02_組織別分析_Phase{phase}.csv')
        generate_department_analysis_csv(dept_analysis, dept_path)
    
    # レポート生成
    report_md = generate_report_markdown(
        phase, analysis, pre_data, post_data, follow_data, manager_data,
        project_name=project_name,
        satisfaction_csv_path=sat_path,
        gap_csv_path=gap_path,
        executive_summary_csv_path=exec_summary_path,
        radar_path_with_manager=radar_path_with_manager if phase == 3 else None
    )
    report_md = f"# プロジェクト: {project_name}\n\n" + report_md
    
    report_filename = f'生成レポート_{project_name}_Phase{phase}.md'
    report_path = os.path.join(project_report_dir, report_filename)
    overwrite_skipped_report = write_file_if_different(report_path, report_md)
    
    # スライド挿入内容のマークダウンファイル生成
    slide_content_md = generate_slide_content_markdown(
        phase, analysis, pre_data, post_data, follow_data, manager_data,
        project_name=project_name,
        executive_summary_csv_path=exec_summary_path,
        gap_csv_path=gap_path if phase == 3 else None,
        department_analysis_csv_path=dept_path
    )
    slide_content_filename = f'スライド挿入内容_{project_name}_Phase{phase}.md'
    slide_content_path = os.path.join(project_report_dir, slide_content_filename)
    if skip_slide_content_write:
        overwrite_skipped_slide = True  # 書き込まない＝既存ファイルを維持
    else:
        overwrite_skipped_slide = write_file_if_different(slide_content_path, slide_content_md)
    
    # 個人別レポート生成（Phase 2以上）
    individual_report_path = None
    individual_slide_content_path = None
    overwrite_skipped_individual = False
    if phase >= 2:
        try:
            # 個人別スコア推移データを取得
            individual_progress = analyze_individual_progress(pre_data, post_data, follow_data)
            
            if not individual_progress or len(individual_progress) == 0:
                print(f"警告: 個人別データが取得できませんでした (Phase {phase})", file=sys.stderr)
            else:
                print(f"個人別データ取得: {len(individual_progress)}名 (Phase {phase})", file=sys.stderr)
            
            # Phase 3の場合、ギャップ分析データも取得
            manager_comparison = None
            if phase == 3 and manager_data:
                manager_comparison = analyze_manager_comparison(follow_data, manager_data)
            
            # 個人別レーダーチャートを生成
            import re
            # 個人用レーダーチャートは Phase 別フォルダに格納（05_分析と出力仕様 2.2）
            personal_radar_dir = 'Phase2_personal_radar_chart' if phase == 2 else 'Phase3_personal_radar_chart'
            personal_radar_dir_full = os.path.join(project_report_dir, personal_radar_dir)
            os.makedirs(personal_radar_dir_full, exist_ok=True)
            radar_count = 0
            for person in individual_progress:
                person_name = (person.get('name') or '').strip()
                if not person_name:
                    email = person.get('email', '')
                    person_name = (email.split('@')[0] if '@' in email else email) if email else ''
                if not person_name:
                    continue
                # ファイル名に使用できない文字を置換
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', person_name)
                radar_filename_individual = f'生成レポート（個別）_{project_name}_{safe_name}_Phase{phase}_レーダーチャート.png'
                radar_path_individual = os.path.join(personal_radar_dir_full, radar_filename_individual)
                
                # 上長評価データを取得（Phase 3のみ）
                person_manager_scores = None
                if phase == 3 and manager_comparison:
                    for gap_person in manager_comparison:
                        if gap_person.get('email') == person.get('email'):
                            person_manager_scores = gap_person.get('manager')
                            break
                
                # 個人別レーダーチャートを生成
                try:
                    generate_individual_radar(person, person_manager_scores, radar_path_individual, person_name, phase)
                    radar_count += 1
                except Exception as e:
                    print(f"個人別レーダーチャート生成エラー ({person_name}): {e}", file=sys.stderr)
            
            print(f"個人別レーダーチャート生成: {radar_count}件 (Phase {phase})", file=sys.stderr)
            
            # 個人別レポートMarkdownを生成
            if individual_progress and len(individual_progress) > 0:
                individual_report_md = generate_individual_report_markdown(
                    phase, individual_progress, manager_comparison, post_data, project_name, project_report_dir
                )
                
                if not individual_report_md or len(individual_report_md.strip()) == 0:
                    print(f"警告: 個人別レポートMarkdownが空です (Phase {phase})", file=sys.stderr)
                else:
                    individual_report_filename = f'生成レポート（個別）_{project_name}_Phase{phase}.md'
                    individual_report_path = os.path.join(project_report_dir, individual_report_filename)
                    overwrite_skipped_individual = write_file_if_different(individual_report_path, individual_report_md)
                    if overwrite_skipped_individual:
                        print(f"個人別レポートファイルは既存の内容と同じためスキップされました: {individual_report_path}", file=sys.stderr)
                    else:
                        print(f"個人別レポートファイルを生成しました: {individual_report_path}", file=sys.stderr)
                
                # 個人別スライド挿入内容を生成
                try:
                    individual_slide_content_md = generate_individual_slide_content_markdown(
                        phase, individual_progress, manager_comparison, manager_data, post_data, project_name, project_report_dir,
                        follow_data=follow_data
                    )
                    
                    if not individual_slide_content_md or len(individual_slide_content_md.strip()) == 0:
                        print(f"警告: 個人別スライド挿入内容Markdownが空です (Phase {phase})", file=sys.stderr)
                    else:
                        individual_slide_content_filename = f'スライド挿入内容（個別）_{project_name}_Phase{phase}.md'
                        individual_slide_content_path = os.path.join(project_report_dir, individual_slide_content_filename)
                        overwrite_skipped_individual_slide = write_file_if_different(individual_slide_content_path, individual_slide_content_md)
                        if overwrite_skipped_individual_slide:
                            print(f"個人別スライド挿入内容ファイルは既存の内容と同じためスキップされました: {individual_slide_content_path}", file=sys.stderr)
                        else:
                            print(f"個人別スライド挿入内容ファイルを生成しました: {individual_slide_content_path}", file=sys.stderr)
                except Exception as e:
                    print(f"個人別スライド挿入内容生成エラー (Phase {phase}): {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
            else:
                print(f"警告: 個人別データがないため、レポートを生成しませんでした (Phase {phase})", file=sys.stderr)
        except Exception as e:
            print(f"個人別レポート生成エラー (Phase {phase}): {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    return {
        'phase': phase,
        'report_path': report_path,
        'radar_path': radar_path,
        'radar_path_with_manager': radar_path_with_manager,  # Phase 3で上長評価データがある場合
        'slide_content_path': slide_content_path,
        'individual_report_path': individual_report_path,  # 個人別レポート
        'individual_slide_content_path': individual_slide_content_path,  # 個人別スライド挿入内容
        'overwrite_skipped_report': overwrite_skipped_report,
        'overwrite_skipped_slide': overwrite_skipped_slide,
        'overwrite_skipped_individual': overwrite_skipped_individual,
        'exec_summary_path': exec_summary_path,
        'dept_path': dept_path,
        'sat_path': sat_path,
        'gap_path': gap_path,
        'analysis': analysis
    }


def analyze_all(uploaded_paths, project_id, project_name):
    """全分析を実行 - Phase 2/3 のみレポート・CSV・GAS を生成（Phase 1 は出力しない）"""
    detected_phase = detect_phase(uploaded_paths)
    if detected_phase == 0:
        return {'error': '必要なCSVが不足しています。実施前のCSVが必要です。'}
    
    # データ読み込み（フォーム準拠: 列名・値の正規化を読込直後に適用）
    pre_data = normalize_participant_csv(load_csv(uploaded_paths['pre']))
    post_data = None
    follow_data = None
    manager_data = None
    if 'post' in uploaded_paths:
        post_data = normalize_participant_csv(load_csv(uploaded_paths['post']))
    if 'follow' in uploaded_paths:
        follow_data = normalize_participant_csv(load_csv(uploaded_paths['follow']))
    if 'manager' in uploaded_paths:
        manager_data = normalize_manager_csv(load_csv(uploaded_paths['manager']))
    
    # Phase 1（実施前のみ）の場合はレポート・CSV・GAS を出力しない（要件）
    if detected_phase == 1:
        update_project_timestamp(BASE_DIR, project_id)
        return {
            'phase': 1,
            'project_id': project_id,
            'project_name': project_name,
            'report_path': None,
            'radar_path': None,
            'slide_content_path': None,
            'export_files': [],
            'phase1_only_no_output': True,
            'gas_code_generated': False,
            'gas_file_path': None,
            'individual_reports': {},
            'individual_slide_contents': {}
        }
    
    # Phase 2 以上: メールアドレス整合性を検証（分析実行前）
    is_valid, validation_error = validate_email_consistency(pre_data, post_data, detected_phase)
    if not is_valid and validation_error:
        return {'error': validation_error}
    
    # 結果格納ディレクトリ（プロジェクトごとのreportsとspreadsheet_exportを使用）
    project_report_dir = get_project_report_dir(BASE_DIR, project_id)
    project_export_dir = get_project_export_dir(BASE_DIR, project_id)
    
    # Phase 2, 3 のみレポートを生成（Phase 1 は出力しない）
    phases_to_generate = []
    if pre_data and post_data:
        phases_to_generate.append(2)
    if pre_data and post_data and follow_data:
        phases_to_generate.append(3)
    
    phase_results = {}
    overwrite_skipped_phases = []
    
    # 各Phaseのレポートを生成
    for phase in phases_to_generate:
        result = generate_phase_report(
            phase, pre_data, post_data, follow_data, manager_data,
            project_id, project_name, project_report_dir, project_export_dir
        )
        if 'error' in result:
            return result
        phase_results[phase] = result
        if result.get('overwrite_skipped_report') or result.get('overwrite_skipped_slide'):
            overwrite_skipped_phases.append(phase)
    
    # 最新のPhase（検出されたPhase）の結果を返す値として使用
    latest_phase = detected_phase
    latest_result = phase_results[latest_phase]
    
    # 共通のCSVエクスポートファイル（最新Phase用）
    export_files = []
    email_mismatch_warning = None  # 実施前・直後のメールアドレス不一致時
    progress_data_for_mismatch = None
    
    # 実践頻度分析（Phase 3のみ）
    if latest_phase == 3 and 'analysis' in latest_result and 'practice_frequency' in latest_result['analysis']:
        freq_path = os.path.join(project_export_dir, '05_実践頻度分析.csv')
        generate_practice_frequency_csv(latest_result['analysis'], freq_path)
        export_files.append(('実践頻度分析', freq_path))
    
    # 個人別スコア推移（Phase 2以上）
    if latest_phase >= 2:
        progress_data = analyze_individual_progress(pre_data, post_data, follow_data)
        if progress_data:
            # 実践頻度データを追加
            if latest_phase == 3 and follow_data:
                for person in progress_data:
                    email = person['email']
                    follow_row = next((r for r in follow_data if r.get('メールアドレス') == email), None)
                    if follow_row:
                        practice_freq = follow_row.get('Q16B', '')
                        if not practice_freq:
                            practice_freq = follow_row.get('Q16A', '')
                        try:
                            person['practice_frequency'] = int(float(practice_freq))
                        except (ValueError, TypeError):
                            person['practice_frequency'] = '-'
            
            progress_path = os.path.join(project_export_dir, '06_個人別スコア推移.csv')
            generate_individual_progress_csv(progress_data, progress_path)
            export_files.append(('個人別スコア推移', progress_path))
            progress_data_for_mismatch = progress_data
    
    # 実施前・直後のメールアドレス合致チェック（Phase 2以上かつ直後あり）
    if progress_data_for_mismatch and post_data:
        unmatched = [p['name'] for p in progress_data_for_mismatch if p.get('post') is None]
        if unmatched:
            pre_count = len(progress_data_for_mismatch)
            matched_count = pre_count - len(unmatched)
            names_with_san = '、'.join(n + 'さん' for n in unmatched)
            message_detail = f'要因：{names_with_san}のメールアドレスが直後.csvと一致しません'
            email_mismatch_warning = {
                'pre_count': pre_count,
                'matched_count': matched_count,
                'unmatched_names': unmatched,
                'message_detail': message_detail
            }
    
    # 本人上長比較（Phase 3のみ）
    if latest_phase == 3 and follow_data and manager_data:
        comparison_data = analyze_manager_comparison(follow_data, manager_data)
        if comparison_data:
            comp_path = os.path.join(project_export_dir, '07_本人上長比較.csv')
            generate_manager_comparison_csv(comparison_data, comp_path, manager_data)
            export_files.append(('本人上長比較', comp_path))
    
    # アンケート項目別平均比較表
    question_path = os.path.join(project_export_dir, '08_アンケート項目別平均比較表.csv')
    generate_question_comparison_csv(latest_phase, pre_data, question_path, post_data, follow_data, manager_data)
    export_files.append(('アンケート項目別平均比較表', question_path))
    
    # 実施直後アクション項目CSV生成（Phase 2以上かつpost_dataが存在する場合は常に生成）
    if latest_phase >= 2 and post_data:
        post_action_path = os.path.join(project_export_dir, '09_実施直後アクション項目.csv')
        try:
            generate_post_action_items_csv(post_data, post_action_path)
            if os.path.exists(post_action_path) and os.path.getsize(post_action_path) > 0:
                export_files.append(('実施直後アクション項目', post_action_path))
        except Exception as e:
            print(f"実施直後アクション項目CSV生成エラー: {e}", file=sys.stderr)
    
    # 1ヶ月後定着確認CSV生成（Phase 3かつfollow_dataが存在し、Q16BまたはQ17Bのデータがある場合のみ）
    if latest_phase >= 3 and follow_data:
        # データ存在チェック: Q16BまたはQ17Bのデータが存在するか確認
        has_practice_data = False
        for row in follow_data:
            q16b = row.get('Q16B', '') or row.get('実践頻度', '') or row.get('Q16B: 実践頻度', '')
            q17b = row.get('Q17B', '') or row.get('実践エビデンス', '') or row.get('Q17B: 実践エビデンス', '') or row.get('コメント', '') or row.get('自由記述', '')
            if q16b or q17b:
                has_practice_data = True
                break
        
        if has_practice_data:
            follow_practice_path = os.path.join(project_export_dir, '10_1ヶ月後定着確認.csv')
            try:
                generate_follow_practice_confirmation_csv(follow_data, follow_practice_path)
                # ファイルが生成された場合のみexport_filesに追加
                if os.path.exists(follow_practice_path) and os.path.getsize(follow_practice_path) > 0:
                    export_files.append(('1ヶ月後定着確認', follow_practice_path))
            except Exception as e:
                print(f"1ヶ月後定着確認CSV生成エラー: {e}", file=sys.stderr)
    
    # 最新Phaseのレポートパスとレーダーチャートパス
    report_path = latest_result['report_path']
    radar_path = latest_result['radar_path']
    slide_content_path = latest_result['slide_content_path']
    
    # GASコードを自動生成（最新Phaseのみ - 各PhaseのGASコードは個別に生成可能）
    gas_filename = f'GASコード_{project_name}_Phase{latest_phase}.gs'
    gas_file_path = os.path.join(project_report_dir, gas_filename)
    gas_code_generated = False
    try:
        print(f"[analyze_all] GASコード自動生成開始: project_id={project_id}, project_name={project_name}, phase={latest_phase}", file=sys.stderr)
        
        # 最新Phase用のエクスポートファイルリストを作成
        latest_export_files = export_files.copy()
        if latest_result.get('exec_summary_path'):
            latest_export_files.append(('エグゼクティブサマリー', latest_result['exec_summary_path']))
        if latest_result.get('dept_path'):
            latest_export_files.append(('組織別分析', latest_result['dept_path']))
        if latest_result.get('sat_path'):
            latest_export_files.append(('満足度分析', latest_result['sat_path']))
        if latest_result.get('gap_path'):
            latest_export_files.append(('ギャップ分析', latest_result['gap_path']))
        
        gas_code = generate_gas_code(
            project_id, project_name, latest_phase,
            report_path, radar_path, latest_export_files,
            slide_content_path=slide_content_path if os.path.exists(slide_content_path) else None
        )
        
        # GASコードをファイルとして保存
        with open(gas_file_path, 'w', encoding='utf-8') as f:
            f.write(gas_code)
        gas_code_generated = True
        print(f"[analyze_all] GASコード自動生成成功: {len(gas_code)}文字, 保存先: {gas_file_path}", file=sys.stderr)
    except Exception as e:
        print(f"[analyze_all] GASコード自動生成エラー: {e}", file=sys.stderr)
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    # プロジェクトの更新日時を更新
    update_project_timestamp(BASE_DIR, project_id)
    
    # Phase 2とPhase 3の個別レポートと個別スライド挿入内容のパスを取得
    individual_reports = {}
    individual_slide_contents = {}
    for phase in [2, 3]:
        if phase in phase_results:
            result = phase_results[phase]
            if result.get('individual_report_path') and os.path.exists(result['individual_report_path']):
                individual_reports[phase] = result['individual_report_path']
            if result.get('individual_slide_content_path') and os.path.exists(result['individual_slide_content_path']):
                individual_slide_contents[phase] = result['individual_slide_content_path']

    # 個別GASコードを自動生成（Phase 2/3 で個別スライド挿入内容が存在する場合）
    for phase, slide_content_path in individual_slide_contents.items():
        individual_gas_filename = f'GASコード（個別）_{project_name}_Phase{phase}.gs'
        individual_gas_file_path = os.path.join(project_report_dir, individual_gas_filename)
        try:
            print(f"[analyze_all] 個別GASコード自動生成開始: Phase {phase}", file=sys.stderr)
            individual_gas_code = generate_individual_gas_code(
                project_id, project_name, phase, slide_content_path
            )
            with open(individual_gas_file_path, 'w', encoding='utf-8') as f:
                f.write(individual_gas_code)
            print(f"[analyze_all] 個別GASコード自動生成成功: {individual_gas_filename}", file=sys.stderr)
        except Exception as e:
            print(f"[analyze_all] 個別GASコード自動生成エラー (Phase {phase}): {e}", file=sys.stderr)

    return {
        'phase': latest_phase,
        'project_id': project_id,
        'project_name': project_name,
        'report_path': report_path,
        'radar_path': radar_path,
        'slide_content_path': slide_content_path,
        'export_files': export_files,
        'overwrite_skipped': len(overwrite_skipped_phases) > 0,
        'gas_code_generated': gas_code_generated,
        'gas_file_path': gas_file_path if gas_code_generated else None,
        'generated_phases': phases_to_generate,  # 生成されたPhaseのリストを追加
        'individual_reports': individual_reports,  # Phase 2, 3の個別レポートパス
        'individual_slide_contents': individual_slide_contents,  # Phase 2, 3の個別スライド挿入内容パス
        'email_mismatch_warning': email_mismatch_warning  # 実施前・直後でメール未合致がある場合
    }

# ---- ルーティング ----


@app.route('/ping')
def ping():
    """接続確認用（ブラウザで表示されないときの診断用）"""
    return 'OK', 200


@app.route('/api/validate-participants', methods=['POST'])
def validate_participants_api():
    """
    CSVアップロード前の参加者照合バリデーション（27_CSV照合バリデーション要件）
    アップロードされたCSVと既存CSVを照合し、不一致情報をJSONで返す
    """
    from src.csv_validator import validate_participants

    project_id = request.form.get('project_id', '')
    if not project_id:
        return jsonify({'error': 'project_id が必要です'}), 400

    project_upload_dir = get_project_upload_dir(BASE_DIR, project_id)
    results = {}

    def _parse_file(file_storage, is_manager=False):
        """アップロードされたCSVファイルをパースして正規化済みリストを返す"""
        raw_text = file_storage.stream.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(raw_text))
        rows = list(reader)
        return normalize_manager_csv(rows) if is_manager else normalize_participant_csv(rows)

    def _load_existing(data_key):
        path = os.path.join(project_upload_dir, REQUIRED_FILES[data_key])
        return normalize_participant_csv(load_csv(path)) if os.path.exists(path) else None

    # 直後.csv → 実施前.csv と照合
    post_file = request.files.get('post_file')
    if post_file and post_file.filename:
        pre_data = _load_existing('pre')
        if pre_data:
            post_data = _parse_file(post_file)
            results['post'] = validate_participants(post_data, pre_data)

    # 1ヶ月後.csv → 直後.csv（なければ実施前.csv）と照合
    follow_file = request.files.get('follow_file')
    if follow_file and follow_file.filename:
        ref_data = _load_existing('post') or _load_existing('pre')
        if ref_data:
            follow_data = _parse_file(follow_file)
            ref_label = '直後.csv' if _load_existing('post') else '実施前.csv'
            results['follow'] = validate_participants(follow_data, ref_data)
            results['follow']['ref_label'] = ref_label

    # 上長1ヶ月後.csv → 実施前.csv と照合（対象者メールアドレス列）
    manager_file = request.files.get('manager_file')
    if manager_file and manager_file.filename:
        pre_data = _load_existing('pre')
        if pre_data:
            raw_text = manager_file.stream.read().decode('utf-8-sig')
            manager_rows = list(csv.DictReader(io.StringIO(raw_text)))
            results['manager'] = validate_participants(
                manager_rows, pre_data,
                email_col='対象者メールアドレス',
                name_col='対象者氏名'
            )

    has_any_issues = any(v.get('has_issues') for v in results.values())
    return jsonify({'results': results, 'has_issues': has_any_issues})


@app.route('/', methods=['GET', 'POST'])
def index():
    """メインページ"""
    msg = ''
    result_links = []
    selected_project_id = None
    email_mismatch_warning = None
    
    if request.method == 'POST':
        # プロジェクト情報を取得
        project_selection = request.form.get('project_selection', '')
        project_name_new = request.form.get('project_name_new', '').strip()
        
        # プロジェクトIDを決定
        if project_selection == 'new' and project_name_new:
            # 新規プロジェクト作成
            project_id = get_or_create_project(BASE_DIR, project_name_new)
            project_name = project_name_new
            selected_project_id = project_id
        elif project_selection and project_selection != 'new':
            # 既存プロジェクトを選択
            project_id = project_selection
            project_name = get_project_name(BASE_DIR, project_id) or project_id
            selected_project_id = project_id
        else:
            msg = 'エラー: プロジェクトを選択するか、新規プロジェクト名を入力してください。'
            # エラー時もプロジェクト一覧を取得
            project_list = get_project_list(BASE_DIR)
            return render_template('index.html', msg=msg, links=result_links, 
                                 required=list(REQUIRED_FILES.values()), 
                                 project_list=project_list,
                                 selected_project_id=None)
        
        uploaded = {}
        project_upload_dir = get_project_upload_dir(BASE_DIR, project_id)
        
        # 個別のname属性でファイルを受け取る
        file_mapping = {
            'pre_file': 'pre',
            'post_file': 'post',
            'follow_file': 'follow',
            'manager_file': 'manager'
        }
        
        # アップロードされたファイルを処理
        for form_key, data_key in file_mapping.items():
            file = request.files.get(form_key)
            if file and file.filename:
                # ファイル名を標準化
                standard_name = REQUIRED_FILES[data_key]
                save_path = os.path.join(project_upload_dir, standard_name)
                save_uploaded_file(file, save_path)
                uploaded[data_key] = save_path
        
        # 既存ファイルも確認（アップロードされていない場合は既存ファイルを使用）
        for data_key, standard_name in REQUIRED_FILES.items():
            if data_key not in uploaded:
                # 既存ファイルのパスを確認
                existing_path = os.path.join(project_upload_dir, standard_name)
                if os.path.exists(existing_path):
                    uploaded[data_key] = existing_path
        
        # 実施前.csvが必須（アップロードまたは既存ファイルのいずれか）
        if 'pre' not in uploaded:
            msg = 'エラー: 実施前.csvが存在しません。ファイルをアップロードしてください。'
        else:
            res = analyze_all(uploaded, project_id, project_name)
            if 'error' in res:
                msg = res['error']
            elif res.get('phase1_only_no_output'):
                msg = '実施前のデータを保存しました。Phase 1（実施前のみ）ではレポート・CSV・GAS の出力は行いません。直後・1ヶ月後のデータをアップロードすると、Phase 2/3 の分析結果をダウンロードできます。'
                result_links = []
                selected_project_id = project_id
            else:
                used_files = []
                if 'pre' in uploaded:
                    used_files.append('実施前.csv')
                if 'post' in uploaded:
                    used_files.append('直後.csv')
                if 'follow' in uploaded:
                    used_files.append('1ヶ月後.csv')
                if 'manager' in uploaded:
                    used_files.append('上長1ヶ月後.csv')
                
                files_info = '、'.join(used_files)
                overwrite_info = ''
                if 'overwrite_skipped' in res and res.get('overwrite_skipped'):
                    overwrite_info = '（既存ファイルと同じ内容のため上書きをスキップしました）'
                msg = f"分析完了: Phase {res['phase']} - プロジェクト: {project_name} (使用ファイル: {files_info}){overwrite_info}"
                result_links = []
                
                # レポートとレーダーチャートのリンク（プロジェクトごとのフォルダに対応、Phaseごとに分ける）
                report_rel_path = os.path.relpath(res["report_path"], BASE_DIR)
                radar_rel_path = os.path.relpath(res["radar_path"], BASE_DIR)
                result_links.append((f'生成レポート Phase {res["phase"]} (Markdown)', f'/download/{report_rel_path}'))
                result_links.append((f'レーダーチャート Phase {res["phase"]} (PNG)', f'/download/{radar_rel_path}'))
                
                # スライド挿入内容のマークダウンファイルのリンクを追加
                if 'slide_content_path' in res and res['slide_content_path']:
                    slide_content_rel_path = os.path.relpath(res["slide_content_path"], BASE_DIR)
                    result_links.append((f'スライド挿入内容 Phase {res["phase"]} (Markdown)', f'/download/{slide_content_rel_path}'))
                
                # Phase 2とPhase 3の個別レポートと個別スライド挿入内容のリンクを追加
                if 'individual_reports' in res:
                    for phase, file_path in res['individual_reports'].items():
                        if os.path.exists(file_path):
                            rel_path = os.path.relpath(file_path, BASE_DIR)
                            result_links.append((f'生成レポート（個別） Phase {phase} (Markdown)', f'/download/{rel_path}'))
                
                if 'individual_slide_contents' in res:
                    for phase, file_path in res['individual_slide_contents'].items():
                        if os.path.exists(file_path):
                            rel_path = os.path.relpath(file_path, BASE_DIR)
                            result_links.append((f'スライド挿入内容（個別） Phase {phase} (Markdown)', f'/download/{rel_path}'))
                
                # CSVエクスポートファイルのリンクを追加
                for label, file_path in res.get('export_files', []):
                    rel_path = os.path.relpath(file_path, BASE_DIR)
                    result_links.append((f'{label} (CSV)', f'/download/{rel_path}'))
                
                # レポートが生成されたので、プロジェクトIDを確実に設定
                selected_project_id = project_id
                # 実施前・直後のメールアドレス不一致がある場合は警告を渡す
                email_mismatch_warning = res.get('email_mismatch_warning')
    
    # プロジェクト一覧を取得（POST処理後も最新の一覧を取得）
    project_list = get_project_list(BASE_DIR)
    
    return render_template('index.html', msg=msg, links=result_links, 
                         required=list(REQUIRED_FILES.values()), 
                         project_list=project_list,
                         selected_project_id=selected_project_id,
                         email_mismatch_warning=email_mismatch_warning)


@app.route('/api/project/<project_id>/files')
def get_project_files(project_id):
    """プロジェクトの既存ファイル一覧を取得"""
    try:
        project_name = get_project_name(BASE_DIR, project_id)
        if not project_name:
            return jsonify({'error': 'プロジェクトが見つかりません'}), 404
        
        project_upload_dir = get_project_upload_dir(BASE_DIR, project_id)
        existing_files = {}
        
        for key, filename in REQUIRED_FILES.items():
            file_path = os.path.join(project_upload_dir, filename)
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                existing_files[key] = {
                    'filename': filename,
                    'exists': True,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                existing_files[key] = {
                    'filename': filename,
                    'exists': False
                }
        
        return jsonify({
            'project_id': project_id,
            'project_name': project_name,
            'files': existing_files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/delete', methods=['DELETE', 'POST'])
def delete_project_api(project_id):
    """プロジェクトを削除"""
    try:
        result = delete_project(BASE_DIR, project_id)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラーが発生しました: {str(e)}'}), 500


@app.route('/api/project/<project_id>/files-status')
def get_files_status(project_id):
    """プロジェクトのファイル生成状況を取得（進捗率を含む）"""
    try:
        try:
            from src.report_quality_checker import check_all_files_completeness
        except ImportError:
            check_all_files_completeness = None  # モジュールが無い場合は品質チェックをスキップ

        project_name = get_project_name(BASE_DIR, project_id)
        if not project_name:
            return jsonify({'error': 'プロジェクトが見つかりません'}), 404
        
        project_report_dir = get_project_report_dir(BASE_DIR, project_id)
        project_export_dir = get_project_export_dir(BASE_DIR, project_id)
        
        files_status = {}
        
        # Phaseごとのファイルを確認（Phase 1, 2, 3）
        phase_reports = {}
        phase_radars = {}
        phase_slide_contents = {}
        phase_gas_codes = {}
        
        for p in [1, 2, 3]:
            # 生成レポート (Markdown)
            report_filename = f'生成レポート_{project_name}_Phase{p}.md'
            report_path = os.path.join(project_report_dir, report_filename)
            report_exists = os.path.exists(report_path)
            report_size = os.path.getsize(report_path) if report_exists else 0
            report_quality = None
            if report_exists:
                try:
                    from src.report_quality_checker import check_report_completeness
                    report_quality = check_report_completeness(report_path)
                    print(f"[get_files_status] Phase {p} レポート品質チェック: completeness_score={report_quality.get('completeness_score', 0.0)}, is_complete={report_quality.get('is_complete', False)}")
                except (ImportError, Exception) as e:
                    print(f"[get_files_status] Phase {p} レポート品質チェックエラー: {e}", file=sys.stderr)
                    import traceback
                    try:
                        traceback.print_exc(file=sys.stderr)
                    except (BrokenPipeError, OSError):
                        pass
                    report_quality = None
            
            # ファイルが存在する場合は品質チェック結果を使用、存在しない場合は0.0
            if report_exists:
                if report_quality:
                    report_completeness = report_quality.get('completeness_score', 0.5)
                    report_is_complete = report_quality.get('is_complete', False)
                    if not report_is_complete and report_size > 1000:
                        report_completeness = max(report_completeness, 0.8)
                        report_is_complete = True
                else:
                    report_completeness = 1.0 if report_size > 1000 else 0.5
                    report_is_complete = report_size > 1000
            else:
                report_completeness = 0.0
                report_is_complete = False
            
            phase_reports[p] = {
                'label': f'生成レポート Phase {p} (Markdown)',
                'filename': report_filename,
                'exists': report_exists,
                'path': os.path.relpath(report_path, BASE_DIR) if report_exists else None,
                'completeness_score': report_completeness,
                'is_complete': report_is_complete,
                'phase': p
            }
            
            # レーダーチャート (PNG)
            radar_filename = f'生成レポート_{project_name}_Phase{p}_レーダーチャート.png'
            radar_path = os.path.join(project_report_dir, radar_filename)
            radar_exists = os.path.exists(radar_path)
            radar_size = os.path.getsize(radar_path) if radar_exists else 0
            if radar_exists and radar_size > 1000:
                radar_completeness = 1.0
                radar_is_complete = True
            elif radar_exists:
                radar_completeness = 0.5
                radar_is_complete = False
            else:
                radar_completeness = 0.0
                radar_is_complete = False
            
            phase_radars[p] = {
                'label': f'レーダーチャート Phase {p} (PNG)',
                'filename': radar_filename,
                'exists': radar_exists,
                'path': os.path.relpath(radar_path, BASE_DIR) if radar_exists else None,
                'completeness_score': radar_completeness,
                'is_complete': radar_is_complete,
                'phase': p
            }
            
            # スライド挿入内容 (Markdown)
            slide_content_filename = f'スライド挿入内容_{project_name}_Phase{p}.md'
            slide_content_path = os.path.join(project_report_dir, slide_content_filename)
            slide_content_exists = os.path.exists(slide_content_path)
            slide_content_size = os.path.getsize(slide_content_path) if slide_content_exists else 0
            slide_content_quality = None
            if slide_content_exists:
                try:
                    from src.report_quality_checker import check_slide_content_completeness
                    slide_content_quality = check_slide_content_completeness(slide_content_path)
                except (ImportError, Exception):
                    slide_content_quality = None
            
            if slide_content_exists:
                if slide_content_quality:
                    slide_content_completeness = slide_content_quality.get('completeness_score', 0.5)
                    slide_content_is_complete = slide_content_quality.get('is_complete', False)
                    if not slide_content_is_complete and slide_content_size > 500:
                        slide_content_completeness = max(slide_content_completeness, 0.8)
                        slide_content_is_complete = True
                else:
                    slide_content_completeness = 1.0 if slide_content_size > 500 else 0.5
                    slide_content_is_complete = slide_content_size > 500
            else:
                slide_content_completeness = 0.0
                slide_content_is_complete = False
            
            phase_slide_contents[p] = {
                'label': f'スライド挿入内容 Phase {p} (Markdown)',
                'filename': slide_content_filename,
                'exists': slide_content_exists,
                'path': os.path.relpath(slide_content_path, BASE_DIR) if slide_content_exists else None,
                'completeness_score': slide_content_completeness,
                'is_complete': slide_content_is_complete,
                'phase': p
            }
            
            # GASコード
            gas_filename = f'GASコード_{project_name}_Phase{p}.gs'
            gas_path = os.path.join(project_report_dir, gas_filename)
            gas_exists = os.path.exists(gas_path)
            gas_size = os.path.getsize(gas_path) if gas_exists else 0
            if gas_exists and gas_size > 1000:
                gas_completeness = 1.0
                gas_is_complete = True
            elif gas_exists:
                gas_completeness = 0.5
                gas_is_complete = False
            else:
                gas_completeness = 0.0
                gas_is_complete = False
            
            phase_gas_codes[p] = {
                'label': f'GASコード Phase {p}',
                'filename': gas_filename,
                'exists': gas_exists,
                'path': os.path.relpath(gas_path, BASE_DIR) if gas_exists else None,
                'completeness_score': gas_completeness,
                'is_complete': gas_is_complete,
                'phase': p
            }
        
        # 最大Phaseを判定（存在するレポートの中で最大のPhase）
        max_phase = 1
        for p in [3, 2, 1]:
            if phase_reports[p]['exists']:
                max_phase = p
                break
        
        files_status['reports_by_phase'] = phase_reports
        files_status['radars_by_phase'] = phase_radars
        files_status['slide_contents_by_phase'] = phase_slide_contents
        files_status['gas_codes_by_phase'] = phase_gas_codes
        files_status['max_phase'] = max_phase
        
        # Phase 2とPhase 3の個別レポートと個別スライド挿入内容を確認
        phase_individual_reports = {}
        phase_individual_slide_contents = {}
        
        for p in [2, 3]:
            # 個別レポート (Phase 2以上)
            individual_report_filename = f'生成レポート（個別）_{project_name}_Phase{p}.md'
            individual_report_path = os.path.join(project_report_dir, individual_report_filename)
            individual_report_exists = os.path.exists(individual_report_path)
            individual_report_size = os.path.getsize(individual_report_path) if individual_report_exists else 0
            
            if individual_report_exists and individual_report_size > 100:
                individual_report_completeness = 1.0
                individual_report_is_complete = True
            elif individual_report_exists:
                individual_report_completeness = 0.5
                individual_report_is_complete = False
            else:
                individual_report_completeness = 0.0
                individual_report_is_complete = False
            
            phase_individual_reports[p] = {
                'label': f'生成レポート（個別） Phase {p} (Markdown)',
                'filename': individual_report_filename,
                'exists': individual_report_exists,
                'path': os.path.relpath(individual_report_path, BASE_DIR) if individual_report_exists else None,
                'completeness_score': individual_report_completeness,
                'is_complete': individual_report_is_complete,
                'phase': p
            }
            
            # 個別スライド挿入内容 (Phase 2以上)
            individual_slide_content_filename = f'スライド挿入内容（個別）_{project_name}_Phase{p}.md'
            individual_slide_content_path = os.path.join(project_report_dir, individual_slide_content_filename)
            individual_slide_content_exists = os.path.exists(individual_slide_content_path)
            individual_slide_content_size = os.path.getsize(individual_slide_content_path) if individual_slide_content_exists else 0
            
            if individual_slide_content_exists and individual_slide_content_size > 100:
                individual_slide_content_completeness = 1.0
                individual_slide_content_is_complete = True
            elif individual_slide_content_exists:
                individual_slide_content_completeness = 0.5
                individual_slide_content_is_complete = False
            else:
                individual_slide_content_completeness = 0.0
                individual_slide_content_is_complete = False
            
            phase_individual_slide_contents[p] = {
                'label': f'スライド挿入内容（個別） Phase {p} (Markdown)',
                'filename': individual_slide_content_filename,
                'exists': individual_slide_content_exists,
                'path': os.path.relpath(individual_slide_content_path, BASE_DIR) if individual_slide_content_exists else None,
                'completeness_score': individual_slide_content_completeness,
                'is_complete': individual_slide_content_is_complete,
                'phase': p
            }
        
        files_status['individual_reports_by_phase'] = phase_individual_reports
        files_status['individual_slide_contents_by_phase'] = phase_individual_slide_contents
        
        # CSVエクスポートファイル（最大Phaseに応じてフィルタリング）
        all_export_file_mapping = {
            '01_エグゼクティブサマリー.csv': ('エグゼクティブサマリー', 1),  # Phase 1以上
            '02_組織別分析.csv': ('組織別分析', 1),  # Phase 1以上
            '03_ギャップ分析.csv': ('ギャップ分析', 3),  # Phase 3のみ
            '04_満足度分析.csv': ('満足度分析', 2),  # Phase 2以上
            '05_実践頻度分析.csv': ('実践頻度分析', 3),  # Phase 3のみ
            '06_個人別スコア推移.csv': ('個人別スコア推移', 2),  # Phase 2以上
            '07_本人上長比較.csv': ('本人上長比較', 3),  # Phase 3のみ
            '08_アンケート項目別平均比較表.csv': ('アンケート項目別平均比較表', 1),  # Phase 1以上
            '09_実施直後アクション項目.csv': ('実施直後アクション項目', 2),  # Phase 2以上（ファイルが存在する場合のみ表示）
            '10_1ヶ月後定着確認.csv': ('1ヶ月後定着確認', 3),  # Phase 3のみ（ファイルが存在する場合のみ表示）
        }
        
        # 最大Phaseに応じてファイルマッピングをフィルタリング
        export_file_mapping = {}
        for filename, (label, required_phase) in all_export_file_mapping.items():
            if max_phase >= required_phase:
                export_file_mapping[filename] = label
        
        csv_files = []
        for filename, label in export_file_mapping.items():
            # エグゼクティブサマリーと組織別分析はPhase付きファイル名を優先的に探す
            file_path = None
            file_exists = False
            
            if filename == '01_エグゼクティブサマリー.csv':
                # Phase付きファイル名を優先的に探す
                phase_filename = f'01_エグゼクティブサマリー_Phase{max_phase}.csv'
                phase_file_path = os.path.join(project_export_dir, phase_filename)
                if os.path.exists(phase_file_path):
                    file_path = phase_file_path
                    file_exists = True
                    filename = phase_filename  # 表示用のファイル名を更新
                else:
                    # Phase付きファイルがない場合はPhaseなしファイル名を試す
                    file_path = os.path.join(project_export_dir, filename)
                    file_exists = os.path.exists(file_path)
            elif filename == '02_組織別分析.csv':
                # Phase付きファイル名を優先的に探す
                phase_filename = f'02_組織別分析_Phase{max_phase}.csv'
                phase_file_path = os.path.join(project_export_dir, phase_filename)
                if os.path.exists(phase_file_path):
                    file_path = phase_file_path
                    file_exists = True
                    filename = phase_filename  # 表示用のファイル名を更新
                else:
                    # Phase付きファイルがない場合はPhaseなしファイル名を試す
                    file_path = os.path.join(project_export_dir, filename)
                    file_exists = os.path.exists(file_path)
            else:
                # その他のファイルは通常通り
                file_path = os.path.join(project_export_dir, filename)
                file_exists = os.path.exists(file_path)
            
            file_size = os.path.getsize(file_path) if file_exists else 0
            # CSVファイルの進捗率を計算
            if file_exists and file_size > 100:
                csv_completeness = 1.0
                csv_is_complete = True
            elif file_exists:
                csv_completeness = 0.5  # ファイルが存在するが小さい場合は50%
                csv_is_complete = False
            else:
                csv_completeness = 0.0
                csv_is_complete = False
            
            csv_files.append({
                'label': f'{label} (CSV)',
                'filename': filename,
                'exists': file_exists,
                'path': os.path.relpath(file_path, BASE_DIR) if file_exists else None,
                'completeness_score': csv_completeness,
                'is_complete': csv_is_complete
            })
        files_status['csv_files'] = csv_files
        
        # 全体の進捗率を計算（全Phaseのファイルを含む）
        all_files = []
        for p in [1, 2, 3]:
            if phase_reports[p]['exists']:
                all_files.append(phase_reports[p])
            if phase_radars[p]['exists']:
                all_files.append(phase_radars[p])
            if phase_slide_contents[p]['exists']:
                all_files.append(phase_slide_contents[p])
            if phase_gas_codes[p]['exists']:
                all_files.append(phase_gas_codes[p])
            # Phase 2とPhase 3の個別レポートと個別スライド挿入内容
            if p >= 2:
                if phase_individual_reports[p]['exists']:
                    all_files.append(phase_individual_reports[p])
                if phase_individual_slide_contents[p]['exists']:
                    all_files.append(phase_individual_slide_contents[p])
        all_files.extend(csv_files)
        
        total_files = len(all_files)
        completed_files = sum(1 for f in all_files if f.get('is_complete', False))
        total_completeness = sum(f.get('completeness_score', 0.0) for f in all_files)
        average_completeness = total_completeness / total_files if total_files > 0 else 0.0
        progress_percentage = int(average_completeness * 100)
        
        # デバッグログ
        print(f"[get_files_status] 結果サマリー:")
        print(f"  - 最大Phase: {max_phase}")
        for p in [1, 2, 3]:
            print(f"  - Phase {p} レポート: exists={phase_reports[p]['exists']}, is_complete={phase_reports[p]['is_complete']}")
            print(f"  - Phase {p} GASコード: exists={phase_gas_codes[p]['exists']}, is_complete={phase_gas_codes[p]['is_complete']}")
        print(f"  - 全体進捗: {progress_percentage}% ({completed_files}/{total_files}ファイル完成)")
        
        return jsonify({
            'project_id': project_id,
            'project_name': project_name,
            'files_status': files_status,
            'progress': {
                'percentage': progress_percentage,
                'completed_files': completed_files,
                'total_files': total_files,
                'average_completeness': average_completeness
            }
        })
    except Exception as e:
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/gas-code')
@app.route('/api/project/<project_id>/gas-code/<int:phase>')
def get_gas_code(project_id, phase=None):
    """プロジェクトのGASコードを生成（Phaseを指定可能）"""
    try:
        project_name = get_project_name(BASE_DIR, project_id)
        if not project_name:
            return jsonify({'error': 'プロジェクトが見つかりません'}), 404
        
        project_report_dir = get_project_report_dir(BASE_DIR, project_id)
        project_export_dir = get_project_export_dir(BASE_DIR, project_id)
        
        # Phaseが指定されていない場合、レポートファイルからPhaseを検出
        if phase is None:
            # Phase 3, 2, 1の順で検索
            for p in [3, 2, 1]:
                report_filename = f'生成レポート_{project_name}_Phase{p}.md'
                report_path = os.path.join(project_report_dir, report_filename)
                if os.path.exists(report_path):
                    phase = p
                    break
            
            if phase is None:
                return jsonify({'error': 'レポートファイルが見つかりません。先に分析を実行してください。'}), 404
        else:
            # Phaseが指定されている場合、そのPhaseのレポートファイルを検索
            report_filename = f'生成レポート_{project_name}_Phase{phase}.md'
            report_path = os.path.join(project_report_dir, report_filename)
        
            if not os.path.exists(report_path):
                return jsonify({'error': f'Phase {phase}のレポートファイルが見つかりません。先に分析を実行してください。'}), 404
        
        # レーダーチャートファイルを検索（Phaseごと）
        radar_filename = f'生成レポート_{project_name}_Phase{phase}_レーダーチャート.png'
        radar_path = os.path.join(project_report_dir, radar_filename)
        
        # エクスポートファイルを検索（Phaseごとに適切なファイルを検索）
        export_files = []
        
        # Phaseごとに必要なファイルを定義
        if phase == 1:
            # Phase1ではエグゼクティブサマリーと組織別分析のみ
            export_file_mapping = {
                '01_エグゼクティブサマリー_Phase1.csv': 'エグゼクティブサマリー',
                '01_エグゼクティブサマリー.csv': 'エグゼクティブサマリー',  # 後方互換性
                '02_組織別分析_Phase1.csv': '組織別分析',
                '02_組織別分析.csv': '組織別分析',  # 後方互換性
            }
        elif phase == 2:
            # Phase2ではエグゼクティブサマリー、組織別分析、満足度分析
            export_file_mapping = {
                '01_エグゼクティブサマリー_Phase2.csv': 'エグゼクティブサマリー',
                '01_エグゼクティブサマリー.csv': 'エグゼクティブサマリー',  # 後方互換性
                '02_組織別分析_Phase2.csv': '組織別分析',
                '02_組織別分析.csv': '組織別分析',  # 後方互換性
                '04_満足度分析_Phase2.csv': '満足度分析',
                '04_満足度分析.csv': '満足度分析',  # 後方互換性
            }
        else:
            # Phase3ではすべてのファイル
            export_file_mapping = {
                '01_エグゼクティブサマリー_Phase3.csv': 'エグゼクティブサマリー',
                '01_エグゼクティブサマリー.csv': 'エグゼクティブサマリー',  # 後方互換性
                '02_組織別分析_Phase3.csv': '組織別分析',
                '02_組織別分析.csv': '組織別分析',  # 後方互換性
                '03_ギャップ分析.csv': 'ギャップ分析',
                '04_満足度分析_Phase3.csv': '満足度分析',
                '04_満足度分析.csv': '満足度分析',  # 後方互換性
                '05_実践頻度分析.csv': '実践頻度分析',
                '06_個人別スコア推移.csv': '個人別スコア推移',
                '07_本人上長比較.csv': '本人上長比較',
                '08_アンケート項目別平均比較表.csv': 'アンケート項目別平均比較表',
            }
        
        # ファイルを検索（Phase付きファイル名を優先、存在しない場合はPhaseなしファイル名を試す）
        added_labels = set()  # 重複を防ぐため
        for filename, label in export_file_mapping.items():
            if label in added_labels:
                continue  # 既に追加済みのラベルはスキップ
            file_path = os.path.join(project_export_dir, filename)
            if os.path.exists(file_path):
                export_files.append((label, file_path))
                added_labels.add(label)
                print(f"GASコード生成: {label} CSVを追加: {file_path}")
        
        # GASコードを生成（phaseは既に確定している）
        print(f"GASコード生成開始: project_id={project_id}, project_name={project_name}, phase={phase}")
        print(f"  レポートパス: {report_path} (存在: {os.path.exists(report_path)})")
        print(f"  レーダーチャートパス: {radar_path} (存在: {os.path.exists(radar_path)})")
        print(f"  エクスポートファイル数: {len(export_files)}")
        for label, path in export_files:
            print(f"    - {label}: {path} (存在: {os.path.exists(path)})")
        
        try:
            # スライド挿入内容Markdownファイルのパスを取得（Phaseごと）
            slide_content_filename = f'スライド挿入内容_{project_name}_Phase{phase}.md'
            slide_content_path = os.path.join(project_report_dir, slide_content_filename)
            
            gas_code = generate_gas_code(
                project_id, project_name, phase,
                report_path, radar_path, export_files,
                slide_content_path=slide_content_path if os.path.exists(slide_content_path) else None
            )
            print(f"GASコード生成成功: {len(gas_code)}文字")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"GASコード生成エラー: {e}")
            print(f"エラートレース: {error_trace}")
            return jsonify({'error': f'GASコード生成に失敗しました: {str(e)}'}), 500
        
        # GASコードをファイルとして保存（Phaseごと）
        gas_filename = f'GASコード_{project_name}_Phase{phase}.gs'
        gas_file_path = os.path.join(project_report_dir, gas_filename)
        try:
            with open(gas_file_path, 'w', encoding='utf-8') as f:
                f.write(gas_code)
            gas_file_saved = True
            gas_file_rel_path = os.path.relpath(gas_file_path, BASE_DIR)
        except Exception as e:
            print(f"GASコードファイル保存エラー: {e}")
            gas_file_saved = False
            gas_file_rel_path = None
        
        response_data = {
            'project_id': project_id,
            'project_name': project_name,
            'gas_code': gas_code,
            'gas_file_saved': gas_file_saved,
            'gas_file_path': gas_file_rel_path,
            'gas_filename': gas_filename
        }
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"GASコード生成エンドポイントエラー: {e}")
        print(f"エラートレース: {error_trace}")
        return jsonify({'error': f'GASコード生成に失敗しました: {str(e)}'}), 500


@app.route('/api/project/<project_id>/individual-gas-code/<int:phase>')
def get_individual_gas_code(project_id, phase):
    """プロジェクトの個人用GASコードを生成（Phase 2または3のみ）"""
    try:
        if phase not in [2, 3]:
            return jsonify({'error': '個人用GASコードはPhase 2またはPhase 3のみ対応しています。'}), 400
        
        project_name = get_project_name(BASE_DIR, project_id)
        if not project_name:
            return jsonify({'error': 'プロジェクトが見つかりません'}), 404
        
        project_report_dir = get_project_report_dir(BASE_DIR, project_id)
        
        # 個人用スライド挿入内容Markdownファイルのパスを取得
        individual_slide_content_filename = f'スライド挿入内容（個別）_{project_name}_Phase{phase}.md'
        individual_slide_content_path = os.path.join(project_report_dir, individual_slide_content_filename)
        
        if not os.path.exists(individual_slide_content_path):
            return jsonify({'error': f'個人用スライド挿入内容ファイルが見つかりません: {individual_slide_content_filename}'}), 404
        
        # 個人用GASコードを生成
        print(f"個人用GASコード生成開始: project_id={project_id}, project_name={project_name}, phase={phase}")
        print(f"  個人用スライド挿入内容パス: {individual_slide_content_path} (存在: {os.path.exists(individual_slide_content_path)})")
        
        try:
            gas_code = generate_individual_gas_code(
                project_id, project_name, phase,
                individual_slide_content_path
            )
            print(f"個人用GASコード生成成功: {len(gas_code)}文字")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"個人用GASコード生成エラー: {e}")
            print(f"エラートレース: {error_trace}")
            return jsonify({'error': f'個人用GASコード生成に失敗しました: {str(e)}'}), 500
        
        # GASコードをファイルとして保存
        gas_filename = f'GASコード（個別）_{project_name}_Phase{phase}.gs'
        gas_file_path = os.path.join(project_report_dir, gas_filename)
        try:
            with open(gas_file_path, 'w', encoding='utf-8') as f:
                f.write(gas_code)
            gas_file_saved = True
            gas_file_rel_path = os.path.relpath(gas_file_path, BASE_DIR)
        except Exception as e:
            print(f"個人用GASコードファイル保存エラー: {e}")
            gas_file_saved = False
            gas_file_rel_path = None
        
        response_data = {
            'project_id': project_id,
            'project_name': project_name,
            'phase': phase,
            'gas_code': gas_code,
            'gas_file_saved': gas_file_saved,
            'gas_file_path': gas_file_rel_path,
            'gas_filename': gas_filename
        }
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"個人用GASコード生成エンドポイントエラー: {e}")
        print(f"エラートレース: {error_trace}")
        return jsonify({'error': f'個人用GASコード生成に失敗しました: {str(e)}'}), 500


def _validate_file_access(filename):
    """ファイルアクセスの検証（共通処理）"""
    import unicodedata
    # セキュリティチェック: パストラバーサル攻撃を防ぐ
    if '..' in filename or filename.startswith('/'):
        return None, 'Invalid path', 400
    
    # reports や spreadsheet_export 配下を配信
    file_path = os.path.join(BASE_DIR, filename)
    
    # ファイルが存在し、許可されたディレクトリ内にあることを確認
    if not os.path.exists(file_path):
        # 厳密一致で見つからない場合: 同一ディレクトリ内で NFKC 正規化して照合（Unicode 互換文字の差を吸収）
        parent = os.path.dirname(file_path)
        base = os.path.basename(file_path)
        if os.path.isdir(parent):
            base_norm = unicodedata.normalize('NFKC', base)
            for f in os.listdir(parent):
                if unicodedata.normalize('NFKC', f) == base_norm:
                    file_path = os.path.join(parent, f)
                    break
        if not os.path.exists(file_path):
            return None, 'File not found', 404
    
    # 許可されたディレクトリ内か確認（reports と spreadsheet_export のみ）
    real_base = os.path.realpath(BASE_DIR)
    real_file = os.path.realpath(file_path)
    if not real_file.startswith(real_base):
        return None, 'Access denied', 403
    
    # プロジェクトフォルダ内のreports、spreadsheet_export、またはuploadsディレクトリ内のみ許可
    projects_dir = os.path.realpath(os.path.join(BASE_DIR, 'projects'))
    
    # 旧形式のreportsまたはspreadsheet_exportディレクトリ（後方互換性のため）
    if real_file.startswith(os.path.realpath(REPORT_DIR)) or real_file.startswith(os.path.realpath(EXPORT_DIR)):
        pass  # 許可
    # プロジェクトフォルダ内の場合
    elif real_file.startswith(projects_dir):
        # プロジェクトフォルダ内のreports、spreadsheet_export、uploadsのみ許可
        rel_path = os.path.relpath(real_file, projects_dir)
        # project_XXX/reports/, project_XXX/spreadsheet_export/, project_XXX/uploads/ の形式のみ許可
        if not ('/reports/' in rel_path or '/spreadsheet_export/' in rel_path or '/uploads/' in rel_path):
            return None, 'Access denied', 403
    else:
        return None, 'Access denied', 403
    
    return file_path, None, None


@app.route('/view/<path:filename>')
def view_file(filename):
    """ファイルをブラウザで表示"""
    
    file_path, error_msg, error_code = _validate_file_access(filename)
    if error_msg:
        return error_msg, error_code
    
    directory = os.path.dirname(file_path)
    filename_only = os.path.basename(file_path)
    
    # ファイルの拡張子に応じて適切なContent-Typeを設定
    ext = os.path.splitext(filename_only)[1].lower()
    mimetype_map = {
        '.md': 'text/markdown; charset=utf-8',
        '.txt': 'text/plain; charset=utf-8',
        '.csv': 'text/csv; charset=utf-8',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.gs': 'text/plain; charset=utf-8',
        '.py': 'text/plain; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
    }
    mimetype = mimetype_map.get(ext, 'text/plain; charset=utf-8')
    
    # CSVファイルの場合は、HTMLテーブルとして表示
    if ext == '.csv':
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                return Response('<p>CSVファイルが空です。</p>', mimetype='text/html; charset=utf-8')
            
            # HTMLテーブルを生成
            html_table = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", sans-serif;">\n'
            
            # ヘッダー行
            if rows:
                html_table += '  <thead>\n    <tr style="background-color: #3498db; color: white; font-weight: bold;">\n'
                for cell in rows[0]:
                    html_table += f'      <th style="text-align: left; padding: 10px;">{cell}</th>\n'
                html_table += '    </tr>\n  </thead>\n'
            
            # データ行
            html_table += '  <tbody>\n'
            for row in rows[1:]:
                html_table += '    <tr>\n'
                for cell in row:
                    # 数値の場合は右揃え
                    try:
                        float(cell)
                        html_table += f'      <td style="text-align: right; padding: 8px;">{cell}</td>\n'
                    except ValueError:
                        html_table += f'      <td style="padding: 8px;">{cell}</td>\n'
                html_table += '    </tr>\n'
            html_table += '  </tbody>\n</table>'
            
            # HTMLテンプレートに埋め込む
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename_only}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-align: left;
            padding: 12px;
            border: 1px solid #2980b9;
        }}
        td {{
            padding: 10px;
            border: 1px solid #ddd;
        }}
        tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tbody tr:hover {{
            background-color: #f0f8ff;
        }}
        .download-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }}
        .download-link:hover {{
            background-color: #229954;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{filename_only}</h1>
        {html_table}
        <a href="/download/{filename}" class="download-link">CSVファイルをダウンロード</a>
    </div>
</body>
</html>"""
            
            return Response(full_html, mimetype='text/html; charset=utf-8')
        except Exception as e:
            # エラー時はテキストとして表示
            return send_file(file_path, mimetype='text/csv; charset=utf-8')
    
    # Markdownファイルの場合は、HTMLにレンダリングして表示
    if ext == '.md':
        try:
            from html import escape as html_escape
            import re
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 画像記法を変換：同じディレクトリの画像は Base64 埋め込みで表示（URL エンコード・パスずれの影響を受けない）
            import base64
            import unicodedata
            md_dir = os.path.dirname(file_path)
            def replace_image(match):
                alt, src = match.group(1), match.group(2).strip()
                if not src:
                    return f'<img src="" alt="{html_escape(alt)}" style="max-width:100%;height:auto;">'
                src_basename = os.path.basename(src)
                img_full_path = os.path.normpath(os.path.join(md_dir, src))
                # 同一ディレクトリ内に限定（パストラバーサル防止）
                try:
                    if os.path.commonpath([os.path.realpath(md_dir), os.path.realpath(img_full_path)]) != os.path.realpath(md_dir):
                        return f'<span class="img-placeholder">[画像: {html_escape(src)}]</span>'
                except ValueError:
                    return f'<span class="img-placeholder">[画像: {html_escape(src)}]</span>'
                # 1) 厳密一致でファイルを探す
                if not os.path.isfile(img_full_path):
                    # 2) NFKC 正規化で照合（例: 羽 U+7FBD と 羽 U+FA0E 互換文字でファイル名がずれている場合）
                    src_norm = unicodedata.normalize('NFKC', src_basename)
                    for f in os.listdir(md_dir):
                        if unicodedata.normalize('NFKC', f) == src_norm:
                            img_full_path = os.path.join(md_dir, f)
                            break
                if os.path.isfile(img_full_path):
                    try:
                        with open(img_full_path, 'rb') as fimg:
                            b64 = base64.b64encode(fimg.read()).decode('ascii')
                        ext_img = os.path.splitext(src)[1].lower()
                        mime = 'image/png' if ext_img == '.png' else ('image/jpeg' if ext_img in ('.jpg', '.jpeg') else 'image/png')
                        return f'<img src="data:{mime};base64,{b64}" alt="{html_escape(alt)}" style="max-width:100%;height:auto;">'
                    except Exception:
                        pass
                # ファイルが無い場合は /view/ URL をフォールバック（パーセントエンコード）
                from urllib.parse import quote
                view_dir = os.path.dirname(filename).replace('\\', '/')
                img_src = f"{view_dir}/{src}" if view_dir else src
                img_src_encoded = quote(img_src, safe='/')
                return f'<img src="/view/{img_src_encoded}" alt="{html_escape(alt)}" style="max-width:100%;height:auto;">'
            html_content = re.sub(r'!\[([^\]]*)\]\(<?([^)\s>]+)>?\)', replace_image, content)
            
            # コードブロックの処理（先に処理して、他の変換の影響を受けないようにする）
            code_blocks = []
            def replace_code_block(match):
                idx = len(code_blocks)
                code_blocks.append(match.group(0))
                return f'___CODE_BLOCK_{idx}___'
            html_content = re.sub(r'```[\s\S]*?```', replace_code_block, html_content)
            
            # インラインコード
            inline_codes = []
            def replace_inline_code(match):
                idx = len(inline_codes)
                inline_codes.append(match.group(0))
                return f'___INLINE_CODE_{idx}___'
            html_content = re.sub(r'`([^`\n]+)`', replace_inline_code, html_content)
            
            # 見出し
            html_content = re.sub(r'^#### (.*)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            
            # 太字
            html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
            
            # リストの処理（行単位で処理）
            lines = html_content.split('\n')
            in_list = False
            processed_lines = []
            for line in lines:
                if re.match(r'^- (.+)$', line.strip()):
                    if not in_list:
                        processed_lines.append('<ul>')
                        in_list = True
                    processed_lines.append(re.sub(r'^- (.+)$', r'<li>\1</li>', line.strip()))
                else:
                    if in_list:
                        processed_lines.append('</ul>')
                        in_list = False
                    processed_lines.append(line)
            if in_list:
                processed_lines.append('</ul>')
            html_content = '\n'.join(processed_lines)
            
            # Markdown 表を HTML table に変換
            def md_table_to_html(table_lines):
                if not table_lines:
                    return ''
                rows = []
                for line in table_lines:
                    cells = [c.strip() for c in line.strip().split('|')]
                    cells = [c for c in cells if c]
                    if not cells:
                        continue
                    rows.append(cells)
                if not rows:
                    return ''
                tbody_start = 1
                if len(rows) > 1 and all(re.match(r'^[-:\s]+$', str(cell)) for cell in rows[1]):
                    tbody_start = 2
                out = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;margin:1em 0;"><thead><tr style="background:#3498db;color:white;">'
                for c in rows[0]:
                    out += f'<th style="padding:8px;">{html_escape(str(c))}</th>'
                out += '</tr></thead><tbody>'
                for row in rows[tbody_start:]:
                    out += '<tr>'
                    for c in row:
                        out += f'<td style="padding:8px;">{html_escape(str(c))}</td>'
                    out += '</tr>'
                out += '</tbody></table>'
                return out
            
            lines = html_content.split('\n')
            result_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if re.match(r'^\|.+\|$', line.strip()):
                    table_lines = []
                    while i < len(lines) and re.match(r'^\|.+\|$', lines[i].strip()):
                        table_lines.append(lines[i])
                        i += 1
                    result_lines.append(md_table_to_html(table_lines))
                    continue
                result_lines.append(line)
                i += 1
            html_content = '\n'.join(result_lines)
            
            # インラインコードを復元
            for i, code in enumerate(inline_codes):
                code_text = code.strip('`')
                html_content = html_content.replace(f'___INLINE_CODE_{i}___', f'<code>{code_text}</code>')
            
            # コードブロックを復元
            for i, code_block in enumerate(code_blocks):
                code_text = code_block.replace('```', '').strip()
                if code_text.startswith('\n'):
                    code_text = code_text[1:]
                html_content = html_content.replace(f'___CODE_BLOCK_{i}___', f'<pre><code>{code_text}</code></pre>')
            
            # 改行を<br>に変換（コードブロック内を除く）
            html_content = html_content.replace('\n', '<br>\n')
            
            # HTMLテンプレートに埋め込む
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename_only}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        strong {{
            font-weight: bold;
            color: #2c3e50;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: 14px;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 10px;
            border: 1px solid #2980b9;
            text-align: left;
        }}
        td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
            
            return Response(full_html, mimetype='text/html; charset=utf-8')
        except Exception as e:
            # エラー時はテキストとして表示
            return send_file(file_path, mimetype='text/plain; charset=utf-8')
    
    # PNG画像ファイルの場合は、HTMLで表示
    if ext == '.png':
        try:
            # Base64エンコードしてHTMLに埋め込む
            import base64
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename_only}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .download-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .download-link:hover {{
            background-color: #229954;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{filename_only}</h1>
        <img src="data:image/png;base64,{image_data}" alt="{filename_only}">
        <br>
        <a href="/download/{filename}" class="download-link">画像をダウンロード</a>
    </div>
</body>
</html>"""
            
            return Response(full_html, mimetype='text/html; charset=utf-8')
        except Exception as e:
            # エラー時は通常通り送信
            return send_file(file_path, mimetype=mimetype)
    
    # その他のファイルは通常通り送信
    return send_file(file_path, mimetype=mimetype)


@app.route('/download/<path:filename>')
def download(filename):
    """ファイルダウンロード"""
    file_path, error_msg, error_code = _validate_file_access(filename)
    if error_msg:
        return error_msg, error_code
    
    directory = os.path.dirname(file_path)
    filename_only = os.path.basename(file_path)
    return send_from_directory(directory, filename_only, as_attachment=True)


if __name__ == '__main__':
    import sys
    # macOS ではポート 5000 が AirPlay Receiver で使われていることがあるため、デフォルトを 5001 に
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    print("アプリケーションを起動しています...")
    print(f"  ブラウザで次のいずれかを開いてください（ポート {port}）:")
    print(f"    http://127.0.0.1:{port}")
    print(f"    http://localhost:{port}")
    print("  表示されない場合は、別のターミナルで: curl http://127.0.0.1:{port}/ping")
    # host='0.0.0.0' で待ち受ける（localhost で 403 になる環境への対応）
    app.run(debug=True, port=port, host='0.0.0.0')
