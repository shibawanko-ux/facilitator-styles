# app_skill_Analysis — プロジェクトメモ

## 概要
ワークショップ参加者のスキル定着度を分析し、スライド用データ・GASコード・テキストレポートを生成するWebアプリ。

## 起動
```bash
cd Project/app_skill_Analysis
python3 app.py  # → http://localhost:5000
```

## 構造
```
Project/app_skill_Analysis/
├── app.py                  ← Flaskエントリーポイント（APIエンドポイント定義）
├── src/
│   ├── analyzer.py             ← スキル分析ロジック・ギャップ計算
│   ├── report_generator.py     ← レポート生成メイン（プレースホルダーデータ生成）
│   ├── report_generator_impl.py← レポート生成サブ（ギャップ分類・テキスト生成）
│   ├── gas_generator.py        ← GASコード生成
│   ├── csv_normalizer.py       ← CSVラベル正規化
│   ├── csv_validator.py        ← CSV参加者照合バリデーション
│   └── project_manager.py      ← プロジェクト管理
├── scripts/
│   └── regenerate_project_reports.py  ← レポート一括再生成スクリプト
├── templates_html/         ← HTMLテンプレート
├── projects/               ← プロジェクトデータ
│   └── <プロジェクト名>/
│       ├── uploads/        ← アップロードCSV（実施前・直後・1ヶ月後・上長）
│       └── reports/        ← 生成レポート・GASコード
└── docs/requirements/      ← 機能要件定義書（番号付き）
```

## よく使うコマンド
```bash
# レポート一括再生成
python3 scripts/regenerate_project_reports.py 2>&1

# 構文チェック
python3 -m py_compile src/report_generator.py && echo "OK"
```

## 重要な仕様メモ
- **メール照合**: `_email_local_match()` でローカル部分（@より前）一致で照合
- **ギャップ計算式**: `本人(1ヶ月後) - 上長`（正 = 過信、負 = 上長が高く評価）
- **プレースホルダー識別子**: `{{O_*}}`, `{{Ogr*}}`, `{{Ork*}}` は最初の組織のみ保持ルール適用済み
- **Phase**: CSVアップロード時に `REPORT_DATA.phase` から取得
