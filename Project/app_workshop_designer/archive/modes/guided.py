from pathlib import Path
from utils.exporter import export_yoken

QUESTIONS = [
    ("zenntaishou",   "【費訪時の全体象】\nクライアントの全体状況・背景・今回の対象について教えてください。\n（例：どんな会社で、何人が対象で、どんなイベントの一環か）"),
    ("haikei",        "【背景・課題認識】\n組織が抱える課題や壁、懸念事項はどんなことですか？"),
    ("mokuteki",      "【取り組みの目的】\nこのワークショップに取り組む目的は何ですか？"),
    ("goal",          "【ゴール（状態目標）】\nワークショップ後、参加者にどんな状態になってほしいですか？"),
    ("basho",         "【開催場所】\n会場はどこですか？（社内/外部会場/オンラインなど）"),
    ("nitteijikan",   "【実施日程・時間】\n日程と時間を教えてください。（例：2026年4月6日 10:00〜18:00）"),
    ("sanka_ninzu",   "【参加者人数】\n何名参加しますか？テーブル構成はありますか？"),
    ("table_kousei",  "【テーブル構成】\nテーブル編成はどうなりますか？（例：5名×4テーブル、サブファシリ4名）"),
    ("seiyaku",       "【開催場所での制約】\n会場で制約はありますか？（例：体を使うワークをしたい、広さの制限など）"),
    ("challenge",     "【学びのポイント（チャレンジ）】\n参加者に気づいてほしいこと・体験させたいことはなんですか？"),
    ("sanka_sha",     "【参加者情報】\n参加者の属性・役職・現状→ありたい姿を教えてください。"),
    ("seiyaku_jouken","【制約条件】\n組織的・状況的な制約はありますか？（例：新設組織、メンバーが多様など）"),
    ("shinkoucourse", "【進行上の課題】\nファシリテーターとして意識すべき課題・懸念はありますか？"),
]


def run_guided_mode(project_name: str, project_dir: Path):
    """ガイドモード：質問を順番に出して与件を埋める"""
    print("\n" + "="*50)
    print("📋 ガイドモード：与件整理を始めます")
    print("="*50)
    print("\n質問に一つずつ答えてください。")
    print("スキップするときは空白のままEnterを押してください。")
    print("途中でやめるときは 'q' を入力してください。\n")

    data = {}
    total = len(QUESTIONS)

    for i, (key, question) in enumerate(QUESTIONS, 1):
        print(f"\n── Q{i}/{total} ──────────────────")
        print(question)
        print()
        answer = input("> ").strip()

        if answer.lower() == "q":
            print("\n⏸  ガイドモードを中断します。入力済みの内容は保存されます。")
            break

        data[key] = answer if answer else "（未記入）"

    # 与件整理をファイルに保存
    export_yoken(project_dir, project_name, data)

    print("\n✅ 与件整理が完了しました！")
    print("   outputs/01_与件整理.md に保存されました。")
    print("\n次は壁打ちモードでワークショップの設計を深めましょう。")

    return data
