# Claude Code 自律モード設定ガイド

---

## モードの種類

| モード | 動作 | 使いどき |
|-------|------|---------|
| `plan` | すべて確認（デフォルト） | 慎重に作業したいとき |
| `acceptEdits` | ファイル編集は自動・Bash は確認 | 仕事しながら放置したいとき |
| `bypassPermissions` | すべて自動（CI環境向け） | 完全自動化・危険なので注意 |

---

## 切り替え方法

### ターミナルから起動するとき

```bash
claude-safe   # 確認モード（今まで通り）
claude-auto   # 自律モード（ファイル編集を自動承認）
```

※ `~/.zshrc` にエイリアス設定済み

### VS Code 内のチャットで切り替えるとき

`Shift+Tab` を押すたびにモードが切り替わる（画面下部に現在のモードが表示される）

---

## 仕事しながら回すフロー

```
朝：タスクを渡す（claude-auto で起動）
     ↓
Claude が Plan → Work → Review を自動ループ
     ↓
仕事しながら放置
     ↓
昼・夕方：Ctrl+T でタスク状況を確認
     ↓
承認 or 修正指示
```

---

## セッションをまたぐための進捗ファイル

コンテキストが切れてもタスクを引き継ぐために `claude-progress.txt` をプロジェクトに置く。

```
# claude-progress.txt

## 現在の状態
- ログイン機能：完了
- ダッシュボード：実装中（ResultsPage.tsx の Line 120 まで）

## 次にやること
- グラフのレスポンシブ対応
```

Claude に「作業前にこのファイルを読んで、完了したら更新して」と指示するだけでOK。

---

## Worktree で本体を汚さず並列作業

```bash
# 別ブランチで Claude に作業させる（main は触れない）
claude -w feature-branch
```

---

## コンテキスト管理コマンド

| コマンド | 説明 |
|---------|------|
| `/clear` | 新しいセッション開始（履歴リセット） |
| `/compact` | 会話をサマリー圧縮してコンテキストを節約 |

---

## 参考

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Enabling Claude Code to work more autonomously](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously)

最終更新：2026-03-16
