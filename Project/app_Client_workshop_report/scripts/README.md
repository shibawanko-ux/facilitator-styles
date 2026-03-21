# 生成スクリプト

## generate_report.py

編集者プロンプト（`docs/10_editor_prompt.md`）をシステムプロンプトとして OpenAI API に渡し、①〜⑦のセクションを生成して `output/` に保存します。

### 前提

- 環境変数 **OPENAI_API_KEY** を設定すること。
- プロジェクトの `input/` に `good_more.md` / `members.md` / `impressions.md` があること。

### 使い方

```bash
# アプリルート（Project/app_Client_workshop_report）で実行
cd Project/app_Client_workshop_report
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...

# 必須の ①〜③, ⑥, ⑦ のみ生成
python scripts/generate_report.py projects/20240224_ソフトバンクsatto

# ④ 全体傾向 と ⑤ 組織課題仮説 も含める
python scripts/generate_report.py projects/20240224_ソフトバンクsatto --include-trends --include-hypothesis

# ドライラン（API を呼ばず入力確認のみ）
python scripts/generate_report.py projects/20240224_ソフトバンクsatto --dry-run
```

### ⑦ 総括文言

`meta.json` の `workshopType` と `docs/workshop_summary_master.json` で総括文言を切り替えます。  
`workshopType` が空またはマスタにない場合は、プレースホルダーを出力します。
