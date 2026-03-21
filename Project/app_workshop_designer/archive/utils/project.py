import os
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PROJECTS_DIR = BASE_DIR / "projects"


def list_projects():
    """既存プロジェクト一覧を返す"""
    if not PROJECTS_DIR.exists():
        return []
    return sorted([d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()])


def create_project(name: str) -> Path:
    """プロジェクトフォルダを作成して返す"""
    project_dir = PROJECTS_DIR / name
    (project_dir / "inputs").mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs").mkdir(parents=True, exist_ok=True)
    print(f"\n✅ プロジェクト作成: projects/{name}/")
    return project_dir


def select_or_create_project() -> tuple[str, Path]:
    """プロジェクトを選択または新規作成する"""
    projects = list_projects()

    print("\n" + "="*50)
    print("📁 プロジェクト選択")
    print("="*50)

    if projects:
        print("\n既存のプロジェクト：")
        for i, p in enumerate(projects, 1):
            print(f"  {i}. {p}")
        print(f"  {len(projects)+1}. 新規プロジェクトを作成")
        print()

        while True:
            choice = input("番号を入力してください: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(projects):
                    name = projects[idx - 1]
                    project_dir = PROJECTS_DIR / name
                    print(f"\n✅ プロジェクト選択: {name}")
                    return name, project_dir
                elif idx == len(projects) + 1:
                    break
            print("有効な番号を入力してください")

    # 新規作成
    print("\n新規プロジェクト名を入力してください")
    print("例: 20260317_トヨタシステムズ")
    name = input("> ").strip()
    if not name:
        today = datetime.today().strftime("%Y%m%d")
        name = f"{today}_新規プロジェクト"

    project_dir = create_project(name)
    return name, project_dir


def save_output(project_dir: Path, filename: str, content: str):
    """outputsフォルダにファイルを保存する"""
    output_path = project_dir / "outputs" / filename
    output_path.write_text(content, encoding="utf-8")
    print(f"\n💾 保存しました: outputs/{filename}")
    return output_path


def add_input_file(project_dir: Path, src_path: str):
    """inputsフォルダに資料をコピーする"""
    src = Path(src_path)
    if not src.exists():
        print(f"⚠️  ファイルが見つかりません: {src_path}")
        return
    dest = project_dir / "inputs" / src.name
    shutil.copy2(src, dest)
    print(f"📎 資料を追加しました: inputs/{src.name}")
    return dest


def load_inputs_summary(project_dir: Path) -> str:
    """inputsフォルダ内のテキストファイルを読み込んでまとめる"""
    inputs_dir = project_dir / "inputs"
    summaries = []
    for f in inputs_dir.iterdir():
        if f.suffix in [".md", ".txt"]:
            content = f.read_text(encoding="utf-8")
            summaries.append(f"=== {f.name} ===\n{content}")
    return "\n\n".join(summaries) if summaries else ""


def load_outputs_summary(project_dir: Path) -> str:
    """outputsフォルダの既存ファイルを読み込む"""
    outputs_dir = project_dir / "outputs"
    summaries = []
    for f in sorted(outputs_dir.iterdir()):
        if f.suffix == ".md":
            content = f.read_text(encoding="utf-8")
            summaries.append(f"=== {f.name} ===\n{content}")
    return "\n\n".join(summaries) if summaries else ""
