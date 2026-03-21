#!/usr/bin/env python3
"""
ワークショップデザイナー CLI
対話しながらワークショップを設計し、アウトプットをファイルに保存するツール
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .envを読み込む
load_dotenv(Path(__file__).parent / ".env")

# パスを通す
sys.path.insert(0, str(Path(__file__).parent))

from utils.project import select_or_create_project
from modes.guided import run_guided_mode
from modes.chat import run_chat_mode


MENU_TEXT = """
╔══════════════════════════════════════╗
║   🎨 ワークショップ デザイナー       ║
╚══════════════════════════════════════╝

モードを選んでください：

  1. 📋 ガイドモード    与件を一つずつ入力して整理する
  2. 💬 壁打ちモード    Claude AIと対話しながら設計する
  3. 🔄 両方実行        ガイドモード → 壁打ちモードの順に実行
  0. 🚪 終了
"""


def main():
    print(MENU_TEXT)

    # APIキー確認
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY が設定されていません。")
        print("   .env ファイルに ANTHROPIC_API_KEY=your_key を設定してください。")
        print("   ガイドモードのみ使用可能です。\n")

    # モード選択
    while True:
        choice = input("選択 (0-3): ").strip()
        if choice in ["0", "1", "2", "3"]:
            break
        print("0〜3の数字を入力してください。")

    if choice == "0":
        print("\n👋 終了します。")
        return

    # プロジェクト選択
    project_name, project_dir = select_or_create_project()

    if choice == "1":
        run_guided_mode(project_name, project_dir)

    elif choice == "2":
        if not api_key:
            print("\n❌ 壁打ちモードにはAPIキーが必要です。")
            return
        run_chat_mode(project_name, project_dir)

    elif choice == "3":
        run_guided_mode(project_name, project_dir)
        if not api_key:
            print("\n⚠️  APIキーがないため壁打ちモードはスキップします。")
            return
        print("\n" + "="*50)
        print("ガイドモードが完了しました。壁打ちモードに進みます。")
        input("Enterキーを押して続ける...")
        run_chat_mode(project_name, project_dir)

    print("\n✅ お疲れ様でした！")
    print(f"   outputs/ にファイルが保存されています。")
    print(f"   📁 projects/{project_name}/outputs/\n")


if __name__ == "__main__":
    main()
