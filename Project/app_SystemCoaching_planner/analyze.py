"""
システムコーチング® プランニング資料生成スクリプト
---------------------------------------------------
使い方:
  ./venv/bin/python analyze.py

クライアントフォルダ構成:
  clients/
  └── クライアント名/
      ├── info.json          # 基本情報（初回入力で自動保存）
      ├── interview_01.txt   # インタビューテキスト
      ├── session_01.m4a     # 音声ファイル（保管用）
      └── output/
          └── YYYY-MM-DD_コーチングプラン_クライアント名.md
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

BASE_DIR = Path(__file__).parent
PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt.txt"
CLIENTS_DIR = BASE_DIR / "clients"
CLIENTS_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────
# ユーティリティ
# ──────────────────────────────────────────

def ask(prompt, default=""):
    val = input(prompt).strip()
    return val if val else default

def load_system_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ──────────────────────────────────────────
# クライアント管理
# ──────────────────────────────────────────

def list_clients():
    return sorted([d.name for d in CLIENTS_DIR.iterdir() if d.is_dir()])

def hearing_new_client():
    """新規クライアントのヒアリングを行い、フォルダとinfo.jsonを作成して返す"""
    print("\n  新規クライアントのヒアリングを始めます。")
    print("  " + "-" * 48)

    org_name   = ask("  Q1. 対象の組織・チーム・クライアントの名前を教えてください: ")
    if not org_name:
        print("[エラー] 名前が必要です。")
        sys.exit(1)

    target_name = ask(f"  Q2. 資料に記載する正式な対象者名を教えてください\n      （例: {org_name} 3名 / {org_name} チーム）: ", org_name)
    coach_name  = ask("  Q3. コーチの名前を教えてください: ")
    period_start = ask("  Q4. セッションはいつ頃から始まりますか？（例: 2026年4月）: ")
    period_end   = ask("  Q5. 終了予定はいつ頃ですか？（例: 2026年9月）: ")
    session_count = ask("  Q6. セッションは何回を想定していますか？（デフォルト: 5）: ", "5")
    tools        = ask("  Q7. 利用ツールを教えてください（デフォルト: Zoom、Googleツール）: ", "Zoom、Googleツール")

    info = {
        "target_name":   target_name,
        "coach_name":    coach_name,
        "period_start":  period_start,
        "period_end":    period_end,
        "session_count": session_count,
        "tools":         tools,
    }

    # フォルダ名はorg_nameを使用
    client_dir = CLIENTS_DIR / org_name
    client_dir.mkdir(exist_ok=True)
    (client_dir / "input").mkdir(exist_ok=True)
    (client_dir / "output").mkdir(exist_ok=True)
    save_info(client_dir, info)

    print(f"\n  ヒアリング完了！")
    print(f"  → フォルダ作成:  clients/{org_name}/")
    print(f"  → 基本情報保存:  clients/{org_name}/info.json")
    print(f"  → インプット用:  clients/{org_name}/input/  ← ここにテキスト・音声を置いてください")
    return client_dir

def select_or_create_client():
    clients = list_clients()

    print("\n--- クライアント / 組織・チームを選択 ---")
    if clients:
        print("  既存のクライアント:")
        for i, name in enumerate(clients, 1):
            print(f"    {i}. {name}")
        print(f"    {len(clients) + 1}. 新規作成")
        choice = ask(f"\n  番号を入力してください（1〜{len(clients) + 1}）: ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(clients):
                return CLIENTS_DIR / clients[idx]
        except ValueError:
            pass

    # 新規作成
    return hearing_new_client()


# ──────────────────────────────────────────
# 基本情報（info.json）
# ──────────────────────────────────────────

def load_info(client_dir):
    info_path = client_dir / "info.json"
    if info_path.exists():
        with open(info_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_info(client_dir, info):
    info_path = client_dir / "info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

def get_info(client_dir):
    """既存クライアントの基本情報を返す。info.jsonがなければヒアリングを行う"""
    saved = load_info(client_dir)

    if saved:
        print(f"\n  保存済みの基本情報:")
        print(f"    対象者:       {saved.get('target_name', '')}")
        print(f"    コーチ:       {saved.get('coach_name', '')}")
        print(f"    期間:         {saved.get('period_start', '')} 〜 {saved.get('period_end', '')}")
        print(f"    セッション数: {saved.get('session_count', '')}回")
        print(f"    ツール:       {saved.get('tools', '')}")
        use_saved = ask("\n  この情報を使いますか？（Enterでそのまま使う / u で更新）: ", "y")
        if use_saved.lower() != "u":
            return saved

    # info.jsonがない or 更新を選んだ場合 → ヒアリング形式で再入力
    print("\n  基本情報をヒアリングします。")
    print("  " + "-" * 48)
    info = {
        "target_name":   ask("  Q1. 資料に記載する対象者名を教えてください: "),
        "coach_name":    ask("  Q2. コーチの名前を教えてください: "),
        "period_start":  ask("  Q3. セッションはいつ頃から始まりますか？（例: 2026年4月）: "),
        "period_end":    ask("  Q4. 終了予定はいつ頃ですか？（例: 2026年9月）: "),
        "session_count": ask("  Q5. セッションは何回を想定していますか？（デフォルト: 5）: ", "5"),
        "tools":         ask("  Q6. 利用ツールを教えてください（デフォルト: Zoom、Googleツール）: ", "Zoom、Googleツール"),
    }
    save_info(client_dir, info)
    print("  → info.json を更新しました。")
    return info


# ──────────────────────────────────────────
# インタビューテキスト取得
# ──────────────────────────────────────────

def list_text_files(client_dir):
    input_dir = client_dir / "input"
    if not input_dir.exists():
        return []
    return sorted([
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix in (".txt", ".md")
    ])

def get_interview_text(client_dir):
    input_dir = client_dir / "input"
    input_dir.mkdir(exist_ok=True)
    txt_files = list_text_files(client_dir)

    print(f"\n--- インタビューテキストを選択 ---")
    if txt_files:
        print("  input/ フォルダ内のテキストファイル:")
        for i, f in enumerate(txt_files, 1):
            print(f"    {i}. {f.name}")
        print(f"    {len(txt_files) + 1}. 直接貼り付ける")
        choice = ask(f"\n  番号を入力してください（1〜{len(txt_files) + 1}）: ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(txt_files):
                with open(txt_files[idx], "r", encoding="utf-8") as f:
                    text = f.read()
                print(f"  → {txt_files[idx].name} を読み込みました。")
                return text
        except ValueError:
            pass

    # 直接貼り付け
    print("\n  インタビューテキストを貼り付けてください。")
    print("  入力が終わったら、空行で「END」と入力してEnterを押してください。")
    print("  " + "-" * 48)
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines)

    # テキストファイルとして保存するか確認（input/ フォルダに保存）
    if text.strip():
        save_choice = ask("\n  このテキストをファイルとして保存しますか？（Enterでスキップ / ファイル名を入力）: ")
        if save_choice:
            fname = save_choice if save_choice.endswith(".txt") else save_choice + ".txt"
            save_path = input_dir / fname
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  → input/{fname} に保存しました。")

    return text


# ──────────────────────────────────────────
# Claude API
# ──────────────────────────────────────────

def call_claude(info, interview_text):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("\n[エラー] ANTHROPIC_API_KEY が設定されていません。")
        print(".env ファイルに ANTHROPIC_API_KEY=sk-ant-xxx を設定してください。")
        sys.exit(1)

    user_message = f"""以下のインタビュー情報を分析し、コーチングプランニング資料のテキストを生成してください。

## 基本情報
- 対象者: {info['target_name']}
- コーチ名: {info['coach_name']}
- セッション期間: {info['period_start']} 〜 {info['period_end']}
- セッション回数: {info['session_count']}回
- 利用ツール: {info['tools']}

## インタビュー内容
{interview_text}
"""

    print("\n  分析中です。しばらくお待ちください...")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=load_system_prompt(),
        messages=[{"role": "user", "content": user_message}]
    )

    raw = message.content[0].text.strip()
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if not json_match:
        print("[エラー] AIの出力からJSONを取得できませんでした。")
        print(raw)
        sys.exit(1)

    return json.loads(json_match.group(0))


# ──────────────────────────────────────────
# Markdown生成
# ──────────────────────────────────────────

def generate_markdown(data, info):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    lines.append("# システムコーチング® Coaching Planning")
    lines.append("")
    lines.append("> ORSC®(Organization & Relationship Systems Coaching®)  ")
    lines.append("> 出典：CRR Global Japan ORSC®プログラム")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## コーチングの目的と体制")
    lines.append("")
    lines.append("| 項目 | 内容 |")
    lines.append("|---|---|")
    lines.append(f"| 対象 | {info['target_name']} |")
    lines.append(f"| スケジュール | {info['period_start']} 〜 {info['period_end']}　セッション：{info['session_count']}回想定 |")
    lines.append(f"| 利用ツール | {info['tools']} |")
    lines.append(f"| コーチ | {info['coach_name']} |")
    lines.append("")
    lines.append("### コーチングの目的")
    for item in data.get("coaching_purpose", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### 目指す状態")
    for item in data.get("target_state", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## システムの現状/願いについて")
    lines.append("")
    lines.append("### ありたい夢（ハイドリーム）")
    for item in data.get("dream_high", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### 現状の強み")
    for item in data.get("strengths", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### コーチとしての所感")
    for item in data.get("coach_impression", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### 最悪な夢（ロードリーム）")
    for item in data.get("dream_low", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## スケジュール / ロードマップ")
    lines.append("")
    for step in data.get("roadmap", []):
        step_num = step.get("step", "")
        label = step.get("label", "")
        subtitle = step.get("subtitle", "")
        works = step.get("works", [])
        header = f"### Step{step_num}: {label}"
        if step_num == 0 and subtitle:
            header += f"（{subtitle}）"
        lines.append(header)
        for w in works:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*生成日: {today}　|　awareness:design*")

    return "\n".join(lines)


# ──────────────────────────────────────────
# メイン
# ──────────────────────────────────────────

def main():
    print("=" * 55)
    print("  システムコーチング® プランニング資料生成")
    print("  awareness:design")
    print("=" * 55)

    # クライアント選択
    client_dir = select_or_create_client()
    (client_dir / "output").mkdir(exist_ok=True)

    # 基本情報
    info = get_info(client_dir)

    # インタビューテキスト
    interview_text = get_interview_text(client_dir)
    if not interview_text.strip():
        print("[エラー] インタビューテキストが空です。")
        sys.exit(1)

    # 分析・生成
    data = call_claude(info, interview_text)
    markdown = generate_markdown(data, info)

    # 出力
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = client_dir / "output" / f"{today}_コーチングプラン_{info['target_name']}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print("\n✓ 生成完了！")
    print(f"  出力ファイル: {output_path.relative_to(BASE_DIR)}")
    print("")
    print("  --- 生成内容 ---")
    print(f"  コーチングの目的: {len(data.get('coaching_purpose', []))}項目")
    print(f"  目指す状態:       {len(data.get('target_state', []))}項目")
    print(f"  ありたい夢:       {len(data.get('dream_high', []))}項目")
    print(f"  最悪な夢:         {len(data.get('dream_low', []))}項目")
    print(f"  強み:             {len(data.get('strengths', []))}項目")
    print(f"  コーチ所感:       {len(data.get('coach_impression', []))}項目")
    print(f"  ロードマップ:     Step0〜Step{len(data.get('roadmap', [])) - 1}")


if __name__ == "__main__":
    main()
