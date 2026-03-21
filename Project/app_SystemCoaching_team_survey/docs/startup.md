# 起動方法・動作確認手順

## 1. ローカル開発サーバーの起動

### 前提条件
- Node.js 18以上がインストールされていること
- Supabaseプロジェクトが作成済みであること
- `.env` ファイルが設定済みであること

### 手順

```bash
# プロジェクトフォルダに移動
cd app_SystemCoaching_team_survey

# 依存関係のインストール（初回のみ）
npm install

# 開発サーバーの起動
npm run dev
```

ブラウザで `http://localhost:5173` にアクセスする。

---

## 2. 環境変数の確認

`.env` ファイルに以下が設定されているか確認する。

```
VITE_SUPABASE_URL=https://yjqpeuzxpyxyncqipobp.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
```

---

## 3. Supabaseの確認

| 確認項目 | 場所 |
|---------|------|
| テーブルの確認 | Supabase → Table Editor |
| ユーザーの確認 | Supabase → Authentication → Users |
| SQLの実行 | Supabase → SQL Editor |

---

## 4. 動作確認チェックリスト

### 認証
- [ ] `http://localhost:5173` にアクセスするとログイン画面にリダイレクトされる
- [ ] 未登録のメールアドレスでログインするとエラーが表示される
- [ ] 正しいメールアドレス・パスワードでログインできる
- [ ] ログイン後にダッシュボードに遷移する
- [ ] 招待メールのリンクからパスワード設定画面に遷移できる
- [ ] パスワードが8文字未満の場合にエラーが表示される
- [ ] パスワードが一致しない場合にエラーが表示される

### ビルド確認
```bash
# ビルドが成功するか確認
npm run build

# リントエラーがないか確認
npm run lint
```

---

## 5. アドミンユーザーの作成手順

1. Supabase → Authentication → Users → `Invite user` をクリック
2. アドミンのメールアドレスを入力して招待メールを送信
3. SQL Editorで以下を実行してアドミン権限を付与する

```sql
insert into public.users (id, email, role)
values (
  '招待したユーザーのUUID',
  'admin@example.com',
  'admin'
);
```

4. 招待メールのリンクからパスワードを設定する
5. ログインして動作確認する

---

## 6. よくあるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| `Failed to fetch` | Supabase URLが間違っている | `.env` のURLを確認 |
| ログインできない | usersテーブルにデータがない | 手順5でユーザーを登録 |
| 画面が真っ白 | ビルドエラー | `npm run build` でエラー確認 |
