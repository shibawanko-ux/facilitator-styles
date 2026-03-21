# スキル: regenerate-reports（レポート一括再生成）

## 対象プロジェクト
`Project/app_skill_Analysis`

## 手順

### 1. 対象プロジェクトを確認
```bash
ls Project/app_skill_Analysis/projects/
```

### 2. レポートを一括再生成
```bash
cd Project/app_skill_Analysis
python3 scripts/regenerate_project_reports.py 2>&1
```

### 3. 結果を確認
- エラーがないか出力を確認する
- 生成されたファイルを `projects/<プロジェクト名>/reports/` で確認する

## 生成されるファイル
| ファイル | 内容 |
|---------|------|
| `スライド挿入内容_PhaseX.md` | 全体スライド用プレースホルダーデータ |
| `スライド挿入内容（個別）_PhaseX.md` | 個別スライド用プレースホルダーデータ |
| `GASコード_PhaseX.gs` | 全体スライド生成GASコード |
| `GASコード（個別）_PhaseX.gs` | 個別スライド生成GASコード |
| `生成レポート（個別）_PhaseX.md` | 個別テキストレポート |

## よくある問題
- **データが `-` になる**: CSVのメールアドレスのドメインが実施前と1ヶ月後で異なる可能性。`_email_local_match()` でローカル部分一致照合している。
- **プレースホルダーが置換されない**: `src/report_generator.py` のキー名がテンプレートと一致しているか確認。
