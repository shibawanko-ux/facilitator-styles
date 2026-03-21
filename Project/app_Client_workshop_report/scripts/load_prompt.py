# scripts/load_prompt.py
"""編集者プロンプト（10_editor_prompt.md）からシステムプロンプト全文を抽出する。"""
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent


def get_app_root(project_dir: Path) -> Path:
    """projects/ の親をアプリルートとする。"""
    p = project_dir.resolve()
    if "projects" in p.parts:
        idx = p.parts.index("projects")
        return Path(*p.parts[:idx])
    return _SCRIPT_DIR.parent


def load_system_prompt(app_root: Path) -> str:
    """docs/10_editor_prompt.md の最初の ```...``` ブロックをシステムプロンプトとして返す。"""
    path = app_root / "docs" / "10_editor_prompt.md"
    if not path.exists():
        raise FileNotFoundError(f"編集者プロンプトが見つかりません: {path}")
    text = path.read_text(encoding="utf-8")
    start = "```\n"
    end = "\n```"
    i = text.find(start)
    if i == -1:
        raise ValueError("10_editor_prompt.md にコードブロック（```）が見つかりません")
    j = text.find(end, i + len(start))
    if j == -1:
        raise ValueError("10_editor_prompt.md のコードブロックが閉じられていません")
    return text[i + len(start) : j].strip()
