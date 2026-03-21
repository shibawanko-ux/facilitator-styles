#!/usr/bin/env python3
"""
組織別スコア検証スクリプト（他組織の数値検証計画に基づく）

スライド挿入内容の組織別数値が analyze_by_department および 02_組織別分析.csv と
一致しているかを検証し、検証結果を Markdown で出力する。

実行例（Project/app_skill_Analysis をカレントに）:
  python scripts/verify_organization_scores.py --project "アイフル株式会社_リサーチWS"

またはワークスペースルートから:
  python Project/app_skill_Analysis/scripts/verify_organization_scores.py --project "アイフル株式会社_リサーチWS"
"""
import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Ogr* プレースホルダーと analyzer キー・02列の対応（report_generator の skill_keys_og に合わせる）
LETTER_TO_KEY = {
    'A': 'delivery',   # 具体化・検証力
    'B': 'research',    # リサーチ・分析力
    'C': 'concept',     # 構想・コンセプト力
    'D': 'communication',  # 伝達・構造化力
    'E': 'implementation',  # 実現・ディレクション力
    'F': 'total',
}
KEY_TO_02_COL = {
    'delivery': '具体化',
    'research': 'リサーチ',
    'concept': '構想',
    'communication': '伝達',
    'implementation': '実現',
    'total': '総合スコア',
}
TOLERANCE = 0.01


def load_csv(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def parse_slide_content_org_blocks(md_path: str) -> Dict[str, Dict[str, Optional[float]]]:
    """
    スライド挿入内容の Markdown をパースし、各 ### 組織名 ブロック内の
    スキル分析テーブルから OgrA_1〜OgrF_1（実施前）、OgrA_2〜OgrF_2（直後）を抽出する。
    戻り値: { 組織名: { 'A_1': 2.67, 'A_2': 3.00, ... } }
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ### 組織名 でブロック分割（スライド0〜2 の ### は組織名でないので、## スライド3 以降のみ）
    blocks = re.split(r'^### (.+)$', content, flags=re.MULTILINE)
    result = {}
    # blocks[0] は先頭、blocks[1], blocks[2] が最初の ### の見出しと本文、blocks[3], blocks[4] が次...
    for i in range(1, len(blocks), 2):
        org_name = blocks[i].strip()
        body = blocks[i + 1] if i + 1 < len(blocks) else ''
        # スキル分析テーブル（表内）の表のみを対象にする（他セクションの表を避ける）
        if '#### スキル分析テーブル（表内）' not in body:
            continue
        # 表の行から | `{{OgrX_N}}` | value | を抽出
        table = {}
        for letter in 'ABCDEF':
            for num in (1, 2):
                key = f'{letter}_{num}'
                # パターン: | `{{OgrA_1}}` | 2.67 | または | `{{OgrA_1}}` | - |
                pat = re.compile(
                    r'\|\s*`\{\{Ogr' + letter + r'_' + str(num) + r'\}\}`\s*\|\s*([^|]+?)\s*\|',
                    re.IGNORECASE
                )
                m = pat.search(body)
                if m:
                    raw = m.group(1).strip()
                    if raw == '-' or not raw:
                        table[key] = None
                    else:
                        try:
                            table[key] = float(raw)
                        except ValueError:
                            table[key] = None
                else:
                    table[key] = None
        if table:
            result[org_name] = table
    return result


def load_02_csv(path: str) -> List[Dict]:
    """02_組織別分析.csv を読み、部署名・人数・各軸・総合を返す。"""
    rows = load_csv(path)
    out = []
    for row in rows:
        dept = (row.get('部署', '') or row.get('\ufeff部署', '')).strip()
        if not dept:
            continue
        out.append({
            'name': dept,
            'count': _safe_int(row.get('人数', '')),
            'total': _safe_float(row.get('総合スコア', '')),
            'research': _safe_float(row.get('リサーチ', '')),
            'concept': _safe_float(row.get('構想', '')),
            'delivery': _safe_float(row.get('具体化', '')),
            'communication': _safe_float(row.get('伝達', '')),
            'implementation': _safe_float(row.get('実現', '')),
        })
    return out


def _safe_float(s: Any) -> float:
    if s is None or s == '':
        return 0.0
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(s: Any) -> int:
    if s is None or s == '':
        return 0
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def compare_level_a(
    slide_data: Dict[str, Dict[str, Optional[float]]],
    dept_analysis_pre: Dict[str, Dict],
    org_list_02: List[Dict],
    dept_analysis_post: Dict[str, Dict],
) -> List[Dict]:
    """
    レベル A: スライドの Ogr*_1 / Ogr*_2 と再計算値（pre / 02 or post）を比較する。
    戻り値: [ { 'org': str, 'axis': str, 'pre_expected': float, 'pre_actual': float, 'pre_ok': bool,
                'post_expected': float, 'post_actual': float, 'post_ok': bool }, ... ]
    """
    rows = []
    for org in org_list_02:
        dept_name = org['name']
        slide = slide_data.get(dept_name) or {}
        pre_dept = dept_analysis_pre.get(dept_name, {})
        post_dept = dept_analysis_post.get(dept_name, org)

        for letter in 'ABCDEF':
            key = LETTER_TO_KEY.get(letter, letter)
            pre_expected = float(pre_dept.get(key, 0) or 0)
            post_expected = float(post_dept.get(key, 0) or 0)
            pre_actual = slide.get(f'{letter}_1')
            post_actual = slide.get(f'{letter}_2')

            pre_actual_f = float(pre_actual) if pre_actual is not None else None
            post_actual_f = float(post_actual) if post_actual is not None else None

            pre_ok = (pre_actual_f is not None and abs(pre_actual_f - pre_expected) <= TOLERANCE) if pre_expected > 0 else (pre_actual_f is None or pre_actual_f == 0)
            if pre_expected == 0 and (pre_actual_f is None or pre_actual_f == 0):
                pre_ok = True
            elif pre_actual_f is None:
                pre_ok = False
            else:
                pre_ok = abs(pre_actual_f - pre_expected) <= TOLERANCE

            post_ok = (post_actual_f is not None and abs(post_actual_f - post_expected) <= TOLERANCE) if post_expected > 0 else (post_actual_f is None or post_actual_f == 0)
            if post_expected == 0 and (post_actual_f is None or post_actual_f == 0):
                post_ok = True
            elif post_actual_f is None:
                post_ok = False
            else:
                post_ok = abs(post_actual_f - post_expected) <= TOLERANCE

            rows.append({
                'org': dept_name,
                'axis': letter,
                'axis_name': {'A': '具体化', 'B': 'リサーチ', 'C': '構想', 'D': '伝達', 'E': '実現', 'F': '総合'}.get(letter, letter),
                'pre_expected': pre_expected,
                'pre_actual': pre_actual_f if pre_actual_f is not None else '-',
                'pre_ok': pre_ok,
                'post_expected': post_expected,
                'post_actual': post_actual_f if post_actual_f is not None else '-',
                'post_ok': post_ok,
            })
    return rows


def compare_level_bc(
    org_list_02: List[Dict],
    progress: List[Dict],
    dept_analysis_pre: Dict[str, Dict],
    dept_analysis_post: Dict[str, Dict],
) -> List[Dict]:
    """
    レベル B/C: 組織の再計算値と、個別メンバーのスコア（1名ならその値、複数名なら平均）を比較する。
    戻り値: [ { 'org': str, 'count': int, 'axis': str, 'pre_expected': float, 'pre_from_individuals': float, 'pre_ok': bool, ... }, ... ]
    """
    import statistics
    rows = []
    dept_to_members = {}
    for p in progress:
        dept = (p.get('department') or '').strip()
        if not dept:
            continue
        dept_to_members.setdefault(dept, []).append(p)

    for org in org_list_02:
        dept_name = org['name']
        members = dept_to_members.get(dept_name, [])
        pre_dept = dept_analysis_pre.get(dept_name, {})
        post_dept = dept_analysis_post.get(dept_name, {})

        if not members:
            for letter in 'ABCDEF':
                key = LETTER_TO_KEY.get(letter, letter)
                rows.append({
                    'org': dept_name,
                    'count': 0,
                    'axis': letter,
                    'pre_expected': pre_dept.get(key, 0) or 0,
                    'pre_from_individuals': None,
                    'pre_ok': False,
                    'post_expected': post_dept.get(key, 0) or 0,
                    'post_from_individuals': None,
                    'post_ok': False,
                })
            continue

        # 組織と同じロジック: 0より大きい値のみで平均（analyze_by_department に合わせる）
        def avg_axis(members_list: List[Dict], key: str, kind: str) -> Optional[float]:
            vals = []
            for m in members_list:
                s = m.get(kind, {})  # 'pre' or 'post'
                if not s:
                    continue
                v = s.get(key)
                if v is not None and v > 0:
                    vals.append(v)
            if not vals:
                return None
            return statistics.mean(vals)

        def avg_total(members_list: List[Dict], kind: str) -> Optional[float]:
            vals = []
            for m in members_list:
                t = m.get('pre_total' if kind == 'pre' else 'post_total')
                if t is not None and t > 0:
                    vals.append(t)
            if not vals:
                return None
            return statistics.mean(vals)

        for letter in 'ABCDEF':
            key = LETTER_TO_KEY.get(letter, letter)
            pre_expected = float(pre_dept.get(key, 0) or 0)
            post_expected = float(post_dept.get(key, 0) or 0)
            if key == 'total':
                pre_ind = avg_total(members, 'pre')
                post_ind = avg_total(members, 'post')
            else:
                pre_ind = avg_axis(members, key, 'pre')
                post_ind = avg_axis(members, key, 'post')

            pre_ok = (pre_ind is not None and abs(pre_ind - pre_expected) <= TOLERANCE) if pre_expected > 0 else (pre_ind is None or pre_ind == 0)
            if pre_expected == 0:
                pre_ok = (pre_ind is None or abs(pre_ind) < TOLERANCE)
            elif pre_ind is not None:
                pre_ok = abs(pre_ind - pre_expected) <= TOLERANCE
            else:
                pre_ok = False

            post_ok = (post_ind is not None and abs(post_ind - post_expected) <= TOLERANCE) if post_expected > 0 else (post_ind is None or post_ind == 0)
            if post_expected == 0:
                post_ok = (post_ind is None or abs(post_ind) < TOLERANCE)
            elif post_ind is not None:
                post_ok = abs(post_ind - post_expected) <= TOLERANCE
            else:
                post_ok = False

            rows.append({
                'org': dept_name,
                'count': len(members),
                'axis': letter,
                'pre_expected': pre_expected,
                'pre_from_individuals': pre_ind,
                'pre_ok': pre_ok,
                'post_expected': post_expected,
                'post_from_individuals': post_ind,
                'post_ok': post_ok,
            })
    return rows


def write_report(
    out_path: str,
    level_a_rows: List[Dict],
    level_bc_rows: Optional[List[Dict]],
    project_name: str,
) -> None:
    md = []
    md.append('# 組織別数値検証結果')
    md.append('')
    md.append(f'**プロジェクト**: {project_name}')
    md.append('')
    md.append('## レベル A: スライド挿入内容 vs 再計算値（analyze_by_department / 02 CSV）')
    md.append('')
    md.append('| 組織 | 軸 | 実施前（期待） | 実施前（スライド） | 実施前一致 | 直後（期待） | 直後（スライド） | 直後一致 |')
    md.append('|------|-----|----------------|---------------------|------------|--------------|------------------|----------|')
    for r in level_a_rows:
        pre_act = r['pre_actual'] if r['pre_actual'] != '-' else '-'
        post_act = r['post_actual'] if r['post_actual'] != '-' else '-'
        md.append(f"| {r['org']} | {r['axis_name']} | {r['pre_expected']:.2f} | {pre_act} | {'OK' if r['pre_ok'] else 'NG'} | {r['post_expected']:.2f} | {post_act} | {'OK' if r['post_ok'] else 'NG'} |")
    all_pre_ok = all(r['pre_ok'] for r in level_a_rows)
    all_post_ok = all(r['post_ok'] for r in level_a_rows)
    md.append('')
    md.append(f'- **実施前 一致**: {"全件OK" if all_pre_ok else "不一致あり"}')
    md.append(f'- **直後 一致**: {"全件OK" if all_post_ok else "不一致あり"}')
    md.append('')

    if level_bc_rows:
        md.append('## レベル B/C: 組織再計算値 vs 個別メンバー（1名はその値、複数名は平均）')
        md.append('')
        md.append('| 組織 | 人数 | 軸 | 実施前（期待） | 実施前（個別から） | 一致 | 直後（期待） | 直後（個別から） | 一致 |')
        md.append('|------|------|-----|----------------|--------------------|------|--------------|------------------|------|')
        for r in level_bc_rows:
            pre_ind = f"{r['pre_from_individuals']:.2f}" if r['pre_from_individuals'] is not None else '-'
            post_ind = f"{r['post_from_individuals']:.2f}" if r['post_from_individuals'] is not None else '-'
            md.append(f"| {r['org']} | {r['count']} | {r['axis']} | {r['pre_expected']:.2f} | {pre_ind} | {'OK' if r['pre_ok'] else 'NG'} | {r['post_expected']:.2f} | {post_ind} | {'OK' if r['post_ok'] else 'NG'} |")
        md.append('')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))


def main():
    parser = argparse.ArgumentParser(description='組織別スコア検証（スライド vs 再計算値）')
    parser.add_argument('--project', default='アイフル株式会社_リサーチWS', help='プロジェクト名（projects/<name> の <name>）')
    parser.add_argument('--no-bc', action='store_true', help='レベル B/C を実行しない')
    args = parser.parse_args()

    project_name = args.project
    base = os.path.join(BASE_DIR, 'projects', project_name)
    upload_dir = os.path.join(base, 'uploads')
    reports_dir = os.path.join(base, 'reports')
    export_dir = os.path.join(base, 'spreadsheet_export')

    pre_path = os.path.join(upload_dir, '実施前.csv')
    post_path = os.path.join(upload_dir, '直後.csv')
    if not os.path.exists(pre_path):
        print(f'エラー: {pre_path} が見つかりません')
        sys.exit(1)
    if not os.path.exists(post_path):
        print(f'エラー: {post_path} が見つかりません')
        sys.exit(1)

    # スライド挿入内容（組織別）。ファイル名は スライド挿入内容_<project_name>_Phase2.md を優先し、なければ一覧から個別以外を探す
    slide_path = os.path.join(reports_dir, f'スライド挿入内容_{project_name}_Phase2.md')
    if not os.path.exists(slide_path):
        try:
            all_md = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
            slide_candidates = [f for f in all_md if '個別' not in f and 'スライド' in f]
            if slide_candidates:
                slide_path = os.path.join(reports_dir, sorted(slide_candidates)[0])
        except OSError:
            pass
    if not os.path.exists(slide_path):
        print(f'エラー: スライド挿入内容（組織別）.md が見つかりません: {reports_dir}')
        sys.exit(1)

    # 02 CSV（Phase2 を優先）
    csv02_path = os.path.join(export_dir, '02_組織別分析_Phase2.csv')
    if not os.path.exists(csv02_path):
        csv02_path = os.path.join(export_dir, '02_組織別分析.csv')
    if not os.path.exists(csv02_path):
        print(f'エラー: 02_組織別分析 CSV が {export_dir} に見つかりません')
        sys.exit(1)

    from app import load_csv
    from src.csv_normalizer import normalize_participant_csv
    from src.analyzer import analyze_by_department, analyze_individual_progress

    pre_data = normalize_participant_csv(load_csv(pre_path))
    post_data = normalize_participant_csv(load_csv(post_path))

    dept_analysis_pre = analyze_by_department(pre_data)
    dept_analysis_post = analyze_by_department(post_data)
    org_list_02 = load_02_csv(csv02_path)
    slide_data = parse_slide_content_org_blocks(slide_path)

    level_a_rows = compare_level_a(slide_data, dept_analysis_pre, org_list_02, dept_analysis_post)
    level_bc_rows = None
    if not args.no_bc:
        progress = analyze_individual_progress(pre_data, post_data)
        level_bc_rows = compare_level_bc(org_list_02, progress, dept_analysis_pre, dept_analysis_post)

    out_path = os.path.join(base, '組織別数値検証結果.md')
    write_report(out_path, level_a_rows, level_bc_rows, project_name)
    print(f'検証結果を出力しました: {out_path}')
    pre_ok = all(r['pre_ok'] for r in level_a_rows)
    post_ok = all(r['post_ok'] for r in level_a_rows)
    if not pre_ok or not post_ok:
        sys.exit(1)
    print('レベル A: 全組織・全軸 一致')


if __name__ == '__main__':
    main()
