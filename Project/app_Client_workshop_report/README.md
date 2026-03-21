# クライアント向けワークショップ振り返り資料作成アプリ

ワークショップ実施後に、クライアントへ提出・プレゼンする振り返りレポートを、ファシリテーターの入力テキストのみから整理・生成するためのアプリ（要件定義・仕様）です。

## ドキュメント

- **[docs/00_手順.md](docs/00_手順.md)** … **やり方の手順だけ**をまとめたファイル。毎回このファイルを見れば作業の流れが分かる。
- **[docs/01_requirements.md](docs/01_requirements.md)** … 要件定義書（概要・入力・出力構成・機能要件・品質要件）
- **[docs/02_data_design.md](docs/02_data_design.md)** … データ設計（プロジェクト名から始まる利用フロー・プロジェクトごとのフォルダ・input/output 格納）
- **[docs/10_editor_prompt.md](docs/10_editor_prompt.md)** … 編集者用プロンプト（LLM に毎回付与するシステムプロンプト）
- **[docs/samples/README.md](docs/samples/README.md)** … 最終サポートサンプル・ワークショップメニューPDFの配置方法
- **[projects/README.md](projects/README.md)** … プロジェクト（1レポート＝1フォルダ）の格納ルール。各レポートのアウトプットは `projects/プロジェクト名/output/` に格納する。

## 成果物の配置

- フォルダ: `Project/app_Client_workshop_report/`
- 要件定義書: `docs/01_requirements.md`
- データ設計: `docs/02_data_design.md`
- 編集者プロンプト: `docs/10_editor_prompt.md`
- サンプル用フォルダ: `docs/samples/`（PDF は手動で配置）
- プロジェクト格納: `projects/`（1レポート＝1プロジェクトフォルダ。最初にプロジェクト名を入力し、その配下に input/ と output/ を格納）

## ①〜⑦の生成（編集・整形）

編集者プロンプトに従い OpenAI で ①〜⑦ を生成するスクリプトを用意しています。

1. 環境変数 `OPENAI_API_KEY` を設定する。
2. アプリルートで以下を実行する。

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/generate_report.py projects/プロジェクト名
```

- ④ 全体傾向・⑤ 組織課題仮説を含める場合: `--include-trends --include-hypothesis` を付与。
- 詳細: [scripts/README.md](scripts/README.md)

実装フェーズでは、上記要件に基づいてアプリを開発する。
