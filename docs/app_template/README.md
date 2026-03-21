# 新規アプリ作成テンプレート

新しいアプリを作るときはこのテンプレートをコピーして使う。

## 使い方

```bash
# テンプレートをコピー
cp -r docs/app_template Project/app_新機能名

# hookに実行権限を付与
chmod +x Project/app_新機能名/.claude/hooks/pre-bash-check.sh
```

## 含まれるもの

| ファイル | 説明 |
|---------|------|
| `CLAUDE.md` | Claude Codeへの指示・ルール |
| `.gitignore` | Git除外設定 |
| `.claude/settings.local.json` | パーミッション設定 |
| `.claude/hooks/pre-bash-check.sh` | 危険操作ガードレール |
| `docs/requirements.md` | 要件定義テンプレート |

## 作成後にやること

1. `CLAUDE.md` のアプリ名・目的を書き換える
2. `docs/requirements.md` を記入する
3. `logs/` フォルダを作成する
4. アプリ固有のフォルダを追加する
