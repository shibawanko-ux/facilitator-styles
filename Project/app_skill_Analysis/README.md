# 実践スキル定着度 分析レポート生成システム（app_skill_Analysis）

CSVをアップロードして、ワークショップのスキル定着度分析レポートとCSV・レーダーチャート・GAS連携用データを生成するWebアプリです。

## 特徴

- **Phase 2/3 で分析結果を出力**: 実施前＋直後で Phase 2、実施前＋直後＋1ヶ月後で Phase 3 のレポート・CSV・レーダーチャート・GAS用データを生成します。
- **Phase 1 は出力しない**: 実施前のみの場合はレポート・CSV・GAS を出力しません（要件に基づく）。
- **メールアドレス整合性検証**（Phase 2 以上）: 実施前と直後で同一参加者が同じメールアドレスを使用していることを検証し、不整合がある場合は分析を実行せずエラーを表示します。

## 必要な環境

- Python 3.8 以上
- pip

## セットアップと起動

```bash
cd Project/app_skill_Analysis
pip install -r requirements.txt
python app.py
```

ブラウザで `http://localhost:5000` を開いてください。

## ドキュメント

- 要件定義: [docs/requirements/00_requirements_overview.md](docs/requirements/00_requirements_overview.md)
- 起動方法: [docs/起動方法.md](docs/起動方法.md)

## 参照

- 本アプリの要件・ロジックは **docs/requirements** に統合されています。
