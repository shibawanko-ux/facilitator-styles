# Claude Code 起動・ログアウト手順

会社用と個人用でClaude Codeを切り替えて使うための手順です。

---

## 前提

- `~/.zshrc` に `claude-work` エイリアスが設定されていること
- 個人用: `~/.claude`
- 会社用: `~/.claude-work`

---

## 起動手順

### 個人用で起動

```bash
claude
```

### 会社用で起動

```bash
claude-work
```

### 初回のみ：設定の反映

`~/.zshrc` を編集した直後は、以下を実行して反映してください。

```bash
source ~/.zshrc
```

または、新しいターミナルを開いてください。

---

## ログアウト手順

### 方法1: ターミナルからコマンドでログアウト

**個人用アカウントからログアウト:**

Claude Code セッション外のターミナルで以下を実行してください。

```bash
claude auth logout
```

**会社用アカウントからログアウト:**

Claude Code セッション外のターミナル（別ウィンドウや別タブ）で以下を実行してください。

```bash
claude-work auth logout
```

### 方法2: Claude Code セッション内でログアウト

Claude Code が起動している状態で、プロンプトに以下を入力します。

```
/logout
```

※ 会社用で起動したセッションなら会社用アカウントから、個人用で起動したセッションなら個人用アカウントからログアウトされます。

---

## トラブルシューティング

### `claude-work` が認識されない

```bash
source ~/.zshrc
```

を実行するか、ターミナルを開き直してください。

### ログアウト後、再度ログインする

起動コマンド（`claude` または `claude-work`）を実行すると、ログインを求められます。

---

## 参考

- [Claude Code を業務用と個人用で環境分離する方法（Zenn）](https://zenn.dev/galirage/articles/separate-claude-code-for-work-and-personal-use)
