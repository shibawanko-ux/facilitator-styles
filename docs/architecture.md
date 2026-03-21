# アーキテクチャ概要

このドキュメントはCLAUDE.mdから参照される詳細設計書。
プロンプトを肥大化させずに「真実の置き場所」として機能する。

最終更新: 2026-03-12

---

## プロジェクト一覧と詳細

### app_skill_Analysis（スキル分析レポート生成）
**スタック**: Python 3.x / Flask / Matplotlib
**概要**: ワークショップ参加者のスキル定着度を分析し、スライド用データ・GASコード・テキストレポートを生成するWebアプリ

```
Project/app_skill_Analysis/
├── app.py                      ← Flaskエントリーポイント
├── src/
│   ├── analyzer.py             ← 分析ロジック・ギャップ計算
│   ├── report_generator.py     ← レポート生成メイン
│   ├── report_generator_impl.py← レポート生成サブ
│   ├── gas_generator.py        ← GASコード生成
│   ├── csv_normalizer.py       ← CSVラベル正規化
│   ├── csv_validator.py        ← CSV参加者照合バリデーション
│   └── project_manager.py      ← プロジェクト管理
├── scripts/
│   └── regenerate_project_reports.py  ← レポート一括再生成
├── templates_html/             ← HTMLテンプレート
├── projects/<プロジェクト名>/
│   ├── uploads/                ← アップロードCSV
│   └── reports/                ← 生成レポート・GASコード
├── docs/requirements/          ← 機能要件定義書（番号付き）
└── logs/                       ← 作業ログ
```

---

### app_Facilitator_reflection（ファシリテーター振り返り）
**スタック**: TypeScript / React / Vite / TailwindCSS
**概要**: ファシリテーターが自分の活動を振り返るWebアプリ

```
Project/app_Facilitator_reflection/
├── src/
│   ├── components/     ← Reactコンポーネント
│   └── ...
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json
├── dist/               ← ビルド成果物
└── logs/               ← 作業ログ
```

---

### app_Facilitator_type_diagnosis（ファシリテータータイプ診断）
**スタック**: TypeScript / React / Vite / TailwindCSS / Vercel
**概要**: ファシリテーターのタイプを診断するWebアプリ（Vercelにデプロイ）

```
Project/app_Facilitator_type_diagnosis/
├── src/
├── public/
├── vercel.json         ← Vercelデプロイ設定
├── package.json
├── dist/               ← ビルド成果物
└── logs/               ← 作業ログ
```

---

### app_blog_requirements（ブログ要件管理）
**概要**: ブログ記事の要件・アイデアを管理するドキュメント集

```
Project/app_blog_requirements/
├── docs/
├── articles/
└── logs/
```

---

### app_book-summary（書籍まとめ）
**概要**: ビジネス書の要約を構造的・実践的に作成するドキュメント集

```
Project/app_book-summary/
├── templates/          ← 要約テンプレート
├── guidelines/         ← 執筆ガイドライン
├── examples/          ← 事例集
├── tools/              ← チェックリスト
└── prompts/            ← プロンプト集
```

---

### app_Client_workshop_report（クライアント向けワークショップレポート）
**スタック**: Python
**概要**: クライアント向けワークショップレポートを生成するアプリ

```
Project/app_Client_workshop_report/
├── scripts/            ← 生成スクリプト
├── projects/           ← プロジェクトデータ
├── docs/               ← ドキュメント
├── requirements.txt    ← Python依存パッケージ
└── logs/               ← 作業ログ
```

---

### app_workshop_designer（ワークショップデザイン支援）
**概要**: 未確認（フォルダ作成済み・中身なし）

```
Project/app_workshop_designer/
└── （未作成）
```

---

## 共通技術方針

### フロントエンド（React系）
- **ビルド**: Vite
- **スタイル**: TailwindCSS
- **言語**: TypeScript
- **パッケージ管理**: npm

### バックエンド（Flask系）
- **言語**: Python 3.x
- **フレームワーク**: Flask
- **仮想環境**: venv/
- **依存管理**: requirements.txt

---

## ワークスペース設定

### パーミッション・Hooks
- 設定: `.claude/settings.local.json`
- Hookスクリプト: `.claude/hooks/pre-bash-check.sh`
  - 危険コマンド（rm, git push, git reset --hard 等）を検知して日本語警告

### バージョン管理
- Gitリポジトリ: ワークスペースルート
- `.gitignore`: uploads/, node_modules/, venv/, dist/ 等を除外

---

## 更新ルール
このファイルはプロジェクト構成が変わったときに更新する。
CLAUDE.mdは短く保ち、詳細はここに書く。
