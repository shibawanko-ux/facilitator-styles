from pathlib import Path
from datetime import datetime


YOKEN_TEMPLATE = """# 与件整理

**プロジェクト名**: {project_name}
**作成日**: {date}

---

## 費訪時の全体象
{zenntaishou}

## 背景・課題認識
{haikei}

## 取り組みの目的
{mokuteki}

## ゴール（状態目標）
{goal}

## 開催情報
- **開催場所**: {basho}
- **実施日程・時間**: {nitteijikan}
- **参加者人数**: {sanka_ninzu}
- **テーブル構成**: {table_kousei}
- **開催場所での制約**: {seiyaku}

## 学びのポイント（チャレンジ）
{challenge}

## 参加者情報
{sanka_sha}

## 制約条件
{seiyaku_jouken}

## 進行上の課題
{shinkoucourse}
"""

TIMELINE_TEMPLATE = """# タイムライン

**プロジェクト名**: {project_name}
**ワークショップタイトル**: {ws_title}
**活動目標**: {katsudo_goal}
**学習目標**: {gakushu_goal}
**時間**: {jikan}
**参加者人数**: {sanka_ninzu}

---

{timeline_table}
"""


def export_yoken(project_dir: Path, project_name: str, data: dict) -> Path:
    """与件整理をファイルに保存"""
    content = YOKEN_TEMPLATE.format(
        project_name=project_name,
        date=datetime.today().strftime("%Y-%m-%d"),
        **{k: data.get(k, "（未記入）") for k in [
            "zenntaishou", "haikei", "mokuteki", "goal",
            "basho", "nitteijikan", "sanka_ninzu", "table_kousei",
            "seiyaku", "challenge", "sanka_sha", "seiyaku_jouken", "shinkoucourse"
        ]}
    )
    path = project_dir / "outputs" / "01_与件整理.md"
    path.write_text(content, encoding="utf-8")
    print(f"\n💾 保存しました: outputs/01_与件整理.md")
    return path


def export_timeline(project_dir: Path, project_name: str, content: str) -> Path:
    """タイムラインをファイルに保存"""
    path = project_dir / "outputs" / "03_タイムライン.md"
    path.write_text(content, encoding="utf-8")
    print(f"\n💾 保存しました: outputs/03_タイムライン.md")
    return path


def export_chat_content(project_dir: Path, filename: str, content: str) -> Path:
    """壁打ち内容を任意のファイルに保存"""
    path = project_dir / "outputs" / filename
    path.write_text(content, encoding="utf-8")
    print(f"\n💾 保存しました: outputs/{filename}")
    return path
