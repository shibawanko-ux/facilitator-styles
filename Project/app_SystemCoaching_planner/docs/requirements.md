# 要件定義 — app_SystemCoaching_planner

作成日: 2026-03-16
更新日: 2026-03-16

## 概要

インタビュー内容からシステムコーチング®（ORSC®）のコーチングプランニング資料テキストを
Claude AIを使って自動生成するPython CLIツール。
クライアント（組織・チーム）ごとにフォルダを作成し、インプット・アウトプットを管理する。

---

## 背景

- システムコーチング®（ORSC®）の案件ごとに、コーチングプランニング資料を手作業で作成していた
- インタビューから分析・文章化・ロードマップ作成に時間がかかっていた
- 参考スライド（SystemCoach_plan.pdf）と同等の構成のテキストを自動生成したい

---

## フォルダ構成

```
app_SystemCoaching_planner/
├── analyze.py              # メインスクリプト（CLIツール）
├── README.md               # 使い方ガイド
├── requirements.txt        # 依存パッケージ
├── .env                    # APIキー設定
├── prompts/
│   └── system_prompt.txt   # Claude用プロンプト（ORSCフレームワーク）
├── clients/                # クライアントごとのフォルダ
│   └── クライアント名/
│       ├── info.json       # 基本情報（初回ヒアリングで自動保存）
│       ├── input/          # インタビューテキスト・音声ファイルを格納
│       │   ├── YYYY-MM-DD_インタビュー_transcript.txt
│       │   ├── YYYY-MM-DD_インタビュー_summary.txt
│       │   └── session_01.m4a（音声ファイル・保管用）
│       └── output/         # 生成したコーチングプランMarkdownを格納
│           └── YYYY-MM-DD_コーチングプラン_クライアント名.md
└── venv/                   # 仮想環境
```

---

## 機能要件

### クライアント管理

- 既存クライアント一覧を番号で選択できる
- 新規クライアントはヒアリング形式（7問）でフォルダ・`info.json` を自動作成
- 既存クライアントの基本情報は保存済み内容を表示し、Enterでそのまま使用 / `u` で更新

### インプット（入力）

- インタビューテキストは `clients/クライアント名/input/` 内の `.txt` `.md` ファイルから選択
- ファイルが存在しない場合はターミナルに直接貼り付け入力も可能（保存オプションあり）
- 音声ファイル（`.m4a` など）は `input/` に置いておくだけでよい（スクリプトは読み込まない）

### 処理

- Claude API（`claude-opus-4-6`）でORSCフレームワークに基づく分析・生成
- JSON形式で構造化された出力を受け取りパース

### アウトプット（出力）

生成されるMarkdownの構成：

| セクション | 内容 |
|---|---|
| コーチングの目的と体制 | 対象・期間・コーチ・目的・目指す状態 |
| システムの現状/願い | ありたい夢・現状の強み・コーチ所感・最悪な夢 |
| スケジュール / ロードマップ | Step0〜Step5 + 各セッションのワーク内容 |

- 保存先: `clients/クライアント名/output/YYYY-MM-DD_コーチングプラン_クライアント名.md`

---

## 非機能要件

- 動作環境: ローカル（macOS）
- 言語: Python 3.x（CLIスクリプト）
- AIモデル: `claude-opus-4-6`
- 認証: なし（ローカル利用想定）

---

## スタック

- Python 3.x
- Anthropic Python SDK（`anthropic==0.40.0`）
- python-dotenv（`python-dotenv==1.0.0`）

---

## 環境変数

- `ANTHROPIC_API_KEY`: Anthropic APIキー（`.env` に設定）

---

## 起動方法

```bash
cd Project/app_SystemCoaching_planner
./venv/bin/python analyze.py
```

---

## ヒアリング項目（新規クライアント作成時）

| # | 質問 | 保存先キー |
|---|------|-----------|
| Q1 | 対象の組織・チーム・クライアントの名前 | フォルダ名 |
| Q2 | 資料に記載する正式な対象者名 | `target_name` |
| Q3 | コーチの名前 | `coach_name` |
| Q4 | セッション開始時期 | `period_start` |
| Q5 | セッション終了予定 | `period_end` |
| Q6 | セッション回数（デフォルト: 5） | `session_count` |
| Q7 | 利用ツール（デフォルト: Zoom、Googleツール） | `tools` |
