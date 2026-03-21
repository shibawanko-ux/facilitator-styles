import os
import anthropic
from pathlib import Path
from prompts.system import SYSTEM_PROMPT
from utils.project import load_inputs_summary, load_outputs_summary, save_output
from utils.exporter import export_chat_content

HELP_TEXT = """
─────────────────────────────────────
💡 コマンド一覧：
  /save <ファイル名>  → 直前のAI回答をファイルに保存
                        例: /save 03_タイムライン.md
  /files             → 添付資料を追加する
  /summary           → これまでの対話内容をまとめてファイルに保存
  /clear             → 会話履歴をリセット
  /help              → このヘルプを表示
  /exit または /quit → 壁打ちモードを終了
─────────────────────────────────────
"""


def run_chat_mode(project_name: str, project_dir: Path):
    """壁打ちモード：Claude APIと対話しながらワークショップを設計する"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    print("\n" + "="*50)
    print("💬 壁打ちモード：ワークショップ設計を始めます")
    print("="*50)
    print(HELP_TEXT)

    # 既存の与件・資料をコンテキストとして読み込む
    inputs_summary = load_inputs_summary(project_dir)
    outputs_summary = load_outputs_summary(project_dir)

    context_parts = []
    if outputs_summary:
        context_parts.append(f"【既存の与件・設計情報】\n{outputs_summary}")
    if inputs_summary:
        context_parts.append(f"【添付資料の内容】\n{inputs_summary}")

    system_with_context = SYSTEM_PROMPT
    if context_parts:
        system_with_context += "\n\n## プロジェクト情報\n" + "\n\n".join(context_parts)

    messages = []
    last_assistant_response = ""

    # 最初のメッセージ
    opening = f"プロジェクト「{project_name}」のワークショップ設計を始めます。何から考えていきましょうか？\n（与件の確認、タイムライン設計、ワーク内容の検討など、どこからでもOKです）"
    print(f"\n🤖 Claude: {opening}\n")

    while True:
        try:
            user_input = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 壁打ちモードを終了します。")
            break

        if not user_input:
            continue

        # コマンド処理
        if user_input.startswith("/"):
            cmd_parts = user_input.split(maxsplit=1)
            cmd = cmd_parts[0].lower()

            if cmd in ["/exit", "/quit"]:
                print("\n👋 壁打ちモードを終了します。")
                break

            elif cmd == "/help":
                print(HELP_TEXT)
                continue

            elif cmd == "/clear":
                messages = []
                print("\n🔄 会話履歴をリセットしました。\n")
                continue

            elif cmd == "/save":
                if len(cmd_parts) < 2:
                    print("⚠️  ファイル名を指定してください。例: /save 03_タイムライン.md")
                    continue
                filename = cmd_parts[1]
                if last_assistant_response:
                    export_chat_content(project_dir, filename, last_assistant_response)
                else:
                    print("⚠️  保存する内容がありません。")
                continue

            elif cmd == "/files":
                print("\n📎 追加したいファイルのパスを入力してください（Enterでキャンセル）:")
                file_path = input("> ").strip()
                if file_path:
                    from utils.project import add_input_file
                    add_input_file(project_dir, file_path)
                    # 資料を再読み込み
                    inputs_summary = load_inputs_summary(project_dir)
                    if inputs_summary:
                        system_with_context = SYSTEM_PROMPT + "\n\n## プロジェクト情報\n"
                        if outputs_summary:
                            system_with_context += f"【既存の与件・設計情報】\n{outputs_summary}\n\n"
                        system_with_context += f"【添付資料の内容】\n{inputs_summary}"
                    print("✅ 資料を読み込みました。次の発言から参照できます。")
                continue

            elif cmd == "/summary":
                if not messages:
                    print("⚠️  対話履歴がありません。")
                    continue
                print("\n📝 対話内容をまとめています...")
                summary_prompt = "これまでの対話内容を以下の構成でMarkdownにまとめてください：\n## 決まったこと\n## 検討中の事項\n## 次のステップ"
                messages.append({"role": "user", "content": summary_prompt})
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    system=system_with_context,
                    messages=messages
                )
                summary_text = response.content[0].text
                messages.append({"role": "assistant", "content": summary_text})
                save_output(project_dir, "02_対話まとめ.md", summary_text)
                print(f"\n🤖 Claude:\n{summary_text}\n")
                last_assistant_response = summary_text
                continue

            else:
                print(f"⚠️  不明なコマンドです。/help でコマンド一覧を確認できます。")
                continue

        # 通常の対話
        messages.append({"role": "user", "content": user_input})

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                system=system_with_context,
                messages=messages
            )
            assistant_text = response.content[0].text
            messages.append({"role": "assistant", "content": assistant_text})
            last_assistant_response = assistant_text
            print(f"\n🤖 Claude:\n{assistant_text}\n")

        except anthropic.APIError as e:
            print(f"\n❌ APIエラー: {e}\n")
        except Exception as e:
            print(f"\n❌ エラー: {e}\n")
