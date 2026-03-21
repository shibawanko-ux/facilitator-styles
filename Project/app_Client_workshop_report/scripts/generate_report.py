#!/usr/bin/env python3
"""
①〜⑦のセクションを編集者プロンプトに従い OpenAI で生成し、プロジェクトの output/ に保存する。
要件: 01_requirements.md F-2。編集者プロンプト: docs/10_editor_prompt.md
"""
import argparse
import json
import os
import sys
from pathlib import Path

# アプリルートを基準に load_prompt をインポート
SCRIPT_DIR = Path(__file__).resolve().parent
APP_ROOT = SCRIPT_DIR.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from scripts.load_prompt import get_app_root, load_system_prompt


# 各出力ファイルの冒頭に付ける見出し（スライド配置メモ付き）
OUTPUT_HEADERS = {
    "01_good_more.md": "# ① ファシリテーターから見た Good & More の整理（チーム別）\n\n※スライド P9〜P12 に貼る\n\n---\n\n",
    "02_members.md": "# ② 印象が強いメンバーの整理\n\n※スライド P13 に貼る\n\n---\n\n",
    "03_impressions.md": "# ③ 各ファシリテーターの所感整理\n\n※スライド P14 に貼る\n\n---\n\n",
    "04_trends.md": "# ④ ワークショップ後の全体傾向\n\n※スライド P3 に貼る\n\n---\n\n",
    "05_hypothesis.md": "# ⑤ 見えた組織課題仮説\n\n※スライド P3 に貼る\n\n---\n\n",
    "06_summary.md": "# ⑥ まとめ\n\n※スライド P3 に貼る\n\n---\n\n",
    "07_overview.md": "# ⑦ 今回のワークショップ総括\n\n※スライド P3 に貼る\n\n---\n\n",
}


def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def load_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def call_editor(
    client,
    system_prompt: str,
    user_message: str,
    model: str = "gpt-4o",
) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )
    return (resp.choices[0].message.content or "").strip()


def ensure_output_dir(project_dir: Path) -> Path:
    out = project_dir / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_output(out_dir: Path, filename: str, body: str) -> None:
    header = OUTPUT_HEADERS.get(filename, "")
    path = out_dir / filename
    path.write_text(header + body, encoding="utf-8")
    print(f"  → {path.relative_to(path.parent.parent.parent)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="①〜⑦を編集者プロンプトで生成し output/ に保存")
    parser.add_argument("project_dir", type=Path, help="例: projects/20240224_ソフトバンクsatto")
    parser.add_argument("--include-trends", action="store_true", help="④ 全体傾向を含める")
    parser.add_argument("--include-hypothesis", action="store_true", help="⑤ 組織課題仮説を含める")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI モデル (default: gpt-4o)")
    parser.add_argument("--dry-run", action="store_true", help="API を呼ばず入力確認のみ")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    if not project_dir.is_dir():
        print(f"エラー: プロジェクトフォルダが存在しません: {project_dir}", file=sys.stderr)
        sys.exit(1)

    app_root = get_app_root(project_dir)
    input_dir = project_dir / "input"
    out_dir = ensure_output_dir(project_dir)

    good_more = load_text(input_dir / "good_more.md")
    members = load_text(input_dir / "members.md")
    impressions = load_text(input_dir / "impressions.md")

    if not good_more:
        print("警告: input/good_more.md が空です。", file=sys.stderr)
    if not members:
        print("警告: input/members.md が空です。", file=sys.stderr)
    if not impressions:
        print("警告: input/impressions.md が空です。", file=sys.stderr)

    meta = load_json(project_dir / "meta.json", {})
    workshop_type = meta.get("workshopType") or ""
    master_path = app_root / "docs" / "workshop_summary_master.json"
    summary_master = load_json(master_path, {})
    overview_text = summary_master.get(workshop_type)
    if overview_text is None:
        overview_text = summary_master.get("", "")

    system_prompt = load_system_prompt(app_root)
    print("編集者プロンプトを読み込みました。")

    if args.dry_run:
        print("--dry-run のため API は呼びません。")
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("エラー: 環境変数 OPENAI_API_KEY を設定してください。", file=sys.stderr)
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    # ① Good & More
    print("① Good & More を生成中...")
    body_01 = call_editor(
        client,
        system_prompt,
        "以下はファシリテーターが入力した Good（強み）と More（伸びしろ）のテキストです。"
        "編集者プロンプトの「① ファシリテーターから見た Good & More の整理」のルールに従い、"
        "チーム別に要約タイトルと内容を整理してください。入力以外の情報は使わず、意味と温度感を保ってください。"
        "対外提出可能な品質になるよう、敬体で読みやすく整えてください。出力は Markdown のみとし、"
        "見出しは「## Aチーム」のようにチーム名、「### Good」「### More」を使ってください。\n\n" + good_more,
        model=args.model,
    )
    write_output(out_dir, "01_good_more.md", body_01)

    # ② 印象が強いメンバー
    print("② 印象が強いメンバーを生成中...")
    body_02 = call_editor(
        client,
        system_prompt,
        "以下はファシリテーターが入力した「印象が強いメンバー」のテキストです。"
        "編集者プロンプトの「② 印象が強いメンバーの整理」のルールに従い、"
        "印象に残った理由・行動・姿勢・関わり方（事実ベース）を整理してください。"
        "人物評価・性格判断は禁止です。対外提出可能な品質になるよう敬体で整えてください。"
        "出力は Markdown のみ。各メンバーは「## 名前」で見出しをつけてください。\n\n" + members,
        model=args.model,
    )
    write_output(out_dir, "02_members.md", body_02)

    # ③ 各ファシリテーターの所感
    print("③ 各ファシリテーターの所感を生成中...")
    body_03 = call_editor(
        client,
        system_prompt,
        "以下は各ファシリテーターの所感テキストです。"
        "編集者プロンプトの「③ 各ファシリテーターの所感整理」のルールに従い、"
        "統合・要約せずファシリテーターごとに整理し、言い回し・温度感を保持してください。"
        "対外提出可能な品質になるよう、誤字脱字のみ修正し敬体で整えてください。"
        "出力は Markdown のみ。各所感は「## 名前」で見出しをつけてください。\n\n" + impressions,
        model=args.model,
    )
    write_output(out_dir, "03_impressions.md", body_03)

    # ④ 全体傾向（オプション）
    if args.include_trends:
        print("④ 全体傾向を生成中...")
        body_04 = call_editor(
            client,
            system_prompt,
            "以下は①で整理した Good & More の内容です。"
            "編集者プロンプトの「④ ワークショップ後の全体傾向」のルールに従い、"
            "Good 3項目・More 3項目（各50文字程度）、「〜傾向が見られた」を基本表現で箇条書きにしてください。\n\n" + body_01,
            model=args.model,
        )
        write_output(out_dir, "04_trends.md", body_04)
    else:
        print("④ はスキップ（--include-trends で含められます）")

    # ⑤ 組織課題仮説（オプション）
    if args.include_hypothesis:
        print("⑤ 組織課題仮説を生成中...")
        combined = f"【① Good & More】\n{body_01}\n\n【② 印象が強いメンバー】\n{body_02}\n\n【③ 所感】\n{body_03}"
        body_05 = call_editor(
            client,
            system_prompt,
            "以下は①・②・③で整理した内容です。"
            "編集者プロンプトの「⑤ 見えた組織課題仮説」のルールに従い、"
            "最大3項目、タイトル20文字以内・リード文50文字以内で、"
            "「〜可能性がある」「〜傾向が見られた」に留めてください。\n\n" + combined,
            model=args.model,
        )
        write_output(out_dir, "05_hypothesis.md", body_05)
    else:
        print("⑤ はスキップ（--include-hypothesis で含められます）")

    # ⑥ まとめ（リード文＋要素3点＋総合のGood＆More＋見えた組織課題仮説）
    combined_123 = f"【① Good & More】\n{body_01}\n\n【② 印象が強いメンバー】\n{body_02}\n\n【③ 所感】\n{body_03}"

    print("⑥ まとめ（リード文・要素）を生成中...")
    part_summary = call_editor(
        client,
        system_prompt,
        "以下は①・②・③で整理した内容です。"
        "編集者プロンプトの「⑥ まとめ」のルールに従い、"
        "リード文（80文字程度、手応え→構造→次のステップ、最後の一文で「次のステップが実務につながる」文脈を必ず含める）と、"
        "要素3点（各10文字程度・名詞句）を出力してください。Markdown で「**リード文**」「**要素**」のように見出しをつけてください。\n\n" + combined_123,
        model=args.model,
    )

    print("⑥ 総合のGood＆Moreを生成中...")
    part_good_more = call_editor(
        client,
        system_prompt,
        "以下は①で整理した Good & More（チーム別）の内容です。"
        "これを総合し、P3用の「総合のGood＆More」として、Good 3条・More 3条で箇条書きにしてください。"
        "各項目は80文字程度とし、入力の内容のみを使い、断定せず「〜傾向が見られた」などに留めてください。"
        "出力形式は「### Good」の下に「- 内容」を3行、「### More」の下に「- 内容」を3行にしてください。\n\n" + body_01,
        model=args.model,
    )

    print("⑥ 見えた組織課題仮説を生成中...")
    part_hypothesis = call_editor(
        client,
        system_prompt,
        "以下は①・②・③で整理した内容です。"
        "編集者プロンプトの「⑤ 見えた組織課題仮説」のルールに従い、"
        "すべての入力情報を分析して組織課題仮説を3つ作成してください。"
        "各項目は「**タイトル**」＋改行＋説明文の形式とし、断定せず「〜傾向が見られた」「〜可能性がある」に留めてください。"
        "出力は「- **タイトル**」で始まる箇条書き3項目にしてください。\n\n" + combined_123,
        model=args.model,
    )

    body_06 = (
        part_summary
        + "\n\n---\n\n## 総合のGood＆More\n\n"
        + part_good_more
        + "\n\n---\n\n## 見えた組織課題仮説\n\n"
        + part_hypothesis
    )
    write_output(out_dir, "06_summary.md", body_06)

    # ⑦ ワークショップ総括
    print("⑦ ワークショップ総括を出力中...")
    if overview_text:
        body_07 = f"**今回のワークショップ総括：**\n\n{overview_text}"
    else:
        body_07 = (
            "**今回のワークショップ総括：**\n\n"
            "（実施ワークショップ種別に応じた総括文言を、meta.json の workshopType に指定するか、"
            "docs/workshop_summary_master.json に追加してください。）"
        )
    write_output(out_dir, "07_overview.md", body_07)

    print("完了しました。")


if __name__ == "__main__":
    main()
