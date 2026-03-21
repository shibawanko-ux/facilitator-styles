#!/usr/bin/env python3
"""指定プロジェクトのレポートを再生成するスクリプト"""
import os
import sys

# プロジェクトルートをパスに追加
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

def main():
    from app import load_csv, write_file_if_different, generate_phase_report
    from src.analyzer import detect_phase, validate_email_consistency
    from src.csv_normalizer import normalize_participant_csv
    from src.project_manager import get_project_report_dir, get_project_export_dir, load_projects

    project_name = "アイフル株式会社_リサーチWS"
    project_id = None
    for pid, pdata in load_projects(BASE_DIR).items():
        if pdata.get("name") == project_name:
            project_id = pid
            break
    if not project_id:
        print(f"エラー: プロジェクト {project_name} が見つかりません")
        sys.exit(1)

    report_dir = get_project_report_dir(BASE_DIR, project_id)
    export_dir = get_project_export_dir(BASE_DIR, project_id)
    upload_dir = os.path.join(BASE_DIR, "projects", "アイフル株式会社_リサーチWS", "uploads")

    pre_path = os.path.join(upload_dir, "実施前.csv")
    post_path = os.path.join(upload_dir, "直後.csv")

    if not os.path.exists(pre_path):
        print(f"エラー: {pre_path} が見つかりません")
        sys.exit(1)

    follow_path  = os.path.join(upload_dir, "1ヶ月後.csv")
    manager_path = os.path.join(upload_dir, "上長1ヶ月後.csv")

    from src.csv_normalizer import normalize_manager_csv
    pre_data     = normalize_participant_csv(load_csv(pre_path))
    post_data    = normalize_participant_csv(load_csv(post_path))    if os.path.exists(post_path)    else []
    follow_data  = normalize_participant_csv(load_csv(follow_path))  if os.path.exists(follow_path)  else []
    manager_data = normalize_manager_csv(load_csv(manager_path))     if os.path.exists(manager_path) else []

    uploaded_paths = {"pre": pre_path}
    if os.path.exists(post_path):
        uploaded_paths["post"] = post_path
    if os.path.exists(follow_path):
        uploaded_paths["follow"] = follow_path
    if os.path.exists(manager_path):
        uploaded_paths["manager"] = manager_path

    phase = detect_phase(uploaded_paths)
    print(f"検出Phase: {phase}")

    # Phase 2 以上: メールアドレス整合性を検証（分析実行前）
    if phase >= 2 and post_data:
        is_valid, validation_error = validate_email_consistency(pre_data, post_data, phase)
        if not is_valid and validation_error:
            print(f"エラー: {validation_error}")
            sys.exit(1)

    # skip_slide_content_write=False: スライド挿入内容MDも再生成（河辺様のアクション宣言誤り等の修正を含む）
    result = generate_phase_report(
        phase, pre_data, post_data, follow_data or None, manager_data or None,
        project_id, project_name, report_dir, export_dir,
        skip_slide_content_write=False
    )

    if isinstance(result, dict) and result.get("error"):
        print(f"エラー: {result['error']}")
        sys.exit(1)

    # GASコードを再生成
    from src.gas_generator import generate_gas_code
    report_path = result.get("report_path")
    radar_path = result.get("radar_path")
    slide_content_path = result.get("slide_content_path")
    export_files = []
    for label, filename in [
        ("エグゼクティブサマリー", f"01_エグゼクティブサマリー_Phase{phase}.csv"),
        ("組織別分析", f"02_組織別分析_Phase{phase}.csv"),
        ("満足度分析", "04_満足度分析.csv"),
    ]:
        p = os.path.join(export_dir, filename)
        if os.path.exists(p):
            export_files.append((label, p))
    gas_code = generate_gas_code(
        project_id, project_name, phase,
        report_path, radar_path, export_files,
        slide_content_path=slide_content_path
    )
    gas_path = os.path.join(report_dir, f"GASコード_{project_name}_Phase{phase}.gs")
    with open(gas_path, "w", encoding="utf-8") as f:
        f.write(gas_code)
    print(f"  GASコード: {gas_path}")

    # 個別GASコードを再生成（Phase 2以上）
    if phase >= 2:
        from src.individual_gas_generator import generate_individual_gas_code
        individual_slide_content_path = os.path.join(
            report_dir, f"スライド挿入内容（個別）_{project_name}_Phase{phase}.md"
        )
        if os.path.exists(individual_slide_content_path):
            individual_gas_code = generate_individual_gas_code(
                project_id, project_name, phase,
                individual_slide_content_path
            )
            individual_gas_path = os.path.join(report_dir, f"GASコード（個別）_{project_name}_Phase{phase}.gs")
            with open(individual_gas_path, "w", encoding="utf-8") as f:
                f.write(individual_gas_code)
            print(f"  GASコード（個別）: {individual_gas_path}")
        else:
            print(f"  警告: 個別スライド挿入内容が見つかりません: {individual_slide_content_path}")

    print("レポート再生成完了")
    print(f"  スライド挿入内容: {report_dir}/スライド挿入内容_{project_name}_Phase{phase}.md")

if __name__ == "__main__":
    main()
