# ワークショップ デザイナー

チャットで対話しながらワークショップを設計し、アウトプットをファイルに保存するCLIツール。

## 起動方法

```bash
cd app_workshop_designer
.venv/bin/python3 main.py
```

## モード

| モード | 説明 |
|--------|------|
| ガイドモード | 与件を一問一答で入力して `01_与件整理.md` に保存 |
| 壁打ちモード | Claude AIと対話しながら設計を深める |
| 両方実行 | ガイド → 壁打ちの順に実行 |

## 壁打ちモードのコマンド

| コマンド | 説明 |
|---------|------|
| `/save <ファイル名>` | 直前のAI回答を保存（例: `/save 03_タイムライン.md`） |
| `/files` | 添付資料（議事録・提案書など）をinputsに追加 |
| `/summary` | 対話内容を `02_対話まとめ.md` に保存 |
| `/clear` | 会話履歴をリセット |
| `/help` | コマンド一覧を表示 |
| `/exit` | 終了 |

## プロジェクト構成

```
projects/YYYYMMDD_クライアント名/
├── inputs/          ← 添付資料（議事録・提案書など）
└── outputs/
    ├── 01_与件整理.md
    ├── 02_対話まとめ.md
    ├── 03_タイムライン.md
    └── 04_スライド構成.md   ← /saveで任意に保存
```

## セットアップ

```bash
# 1. 仮想環境作成（初回のみ）
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. APIキー設定
cp .env.example .env
# .envを開いてANTHROPIC_API_KEYを設定

# 3. 起動
.venv/bin/python3 main.py
```
