# Vercelへのデプロイ手順

このガイドでは、ファシリテータースタイルをVercelにデプロイする手順を説明します。

## 前提条件

- GitHubアカウント（推奨）またはGitLabアカウント
- Vercelアカウント（無料で作成可能）

---

## 方法1: GitHubリポジトリ経由でデプロイ（推奨）

### Step 1: GitHubにリポジトリを作成

1. [GitHub](https://github.com)にログイン
2. 「New repository」をクリック
3. リポジトリ名を入力（例: `facilistyle`）
4. Public または Private を選択
5. 「Create repository」をクリック

### Step 2: コードをGitHubにプッシュ

```bash
# プロジェクトディレクトリに移動
cd app_Facilitator_type_diagnosis

# Gitを初期化
git init

# すべてのファイルをステージング
git add .

# 最初のコミット
git commit -m "Initial commit: ファシリテータースタイル診断アプリ"

# GitHubリポジトリをリモートに追加
git remote add origin https://github.com/YOUR_USERNAME/facilistyle.git

# mainブランチにプッシュ
git branch -M main
git push -u origin main
```

### Step 3: Vercelでデプロイ

1. [Vercel](https://vercel.com)にアクセス
2. 「Sign Up」または「Log In」
3. GitHubアカウントで連携

4. ダッシュボードで「Add New...」→「Project」をクリック

5. 「Import Git Repository」でGitHubリポジトリを選択

6. プロジェクト設定:
   - **Framework Preset**: Vite
   - **Root Directory**: `./`（そのまま）
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

7. 「Deploy」をクリック

8. デプロイ完了後、URLが発行されます（例: `https://facilistyle.vercel.app`）

---

## 方法2: Vercel CLIでデプロイ

### Step 1: Vercel CLIをインストール

```bash
npm install -g vercel
```

### Step 2: Vercelにログイン

```bash
vercel login
```

ブラウザが開くので、アカウントで認証します。

### Step 3: デプロイ

```bash
# プロジェクトディレクトリに移動
cd app_Facilitator_type_diagnosis

# デプロイ
vercel

# 質問に回答:
# - Set up and deploy? → Y
# - Which scope? → 自分のアカウントを選択
# - Link to existing project? → N
# - Project name → facilistyle（任意）
# - Directory → ./
# - Override settings? → N
```

### Step 4: プロダクションデプロイ

```bash
vercel --prod
```

---

## カスタムドメインの設定（オプション）

1. Vercelダッシュボードでプロジェクトを選択
2. 「Settings」→「Domains」
3. カスタムドメインを入力（例: `facilistyle.example.com`）
4. DNSレコードを設定:
   - Aレコード: `76.76.19.19`
   - または CNAMEレコード: `cname.vercel-dns.com`

---

## 環境変数の設定（必要な場合）

Google Analyticsなどを追加する場合:

1. Vercelダッシュボードでプロジェクトを選択
2. 「Settings」→「Environment Variables」
3. 変数を追加:
   - Name: `VITE_GA_TRACKING_ID`
   - Value: `G-XXXXXXXXXX`
   - Environment: Production

---

## 自動デプロイ

GitHubリポジトリと連携すると:
- `main`ブランチへのプッシュで自動的にプロダクションデプロイ
- プルリクエストごとにプレビューデプロイが作成

---

## GitHub連携で本番に出す手順（やさしい版）

すでにVercelとGitHubを連携している場合、**コードをGitHubにプッシュするだけで本番が自動で更新**されます。手順は次のとおりです。

### 1. 変更をGitHubにプッシュする

ターミナルでプロジェクトフォルダに移動して、次を実行します。

```bash
cd app_Facilitator_type_diagnosis   # プロジェクトのフォルダへ

git add .
git commit -m "ここに変更内容のメモを書く"
git push origin main
```

- `git add .` … 変更したファイルを「出荷リスト」に載せる
- `git commit -m "..."` … ひとまとまりの変更として記録する
- `git push origin main` … その記録をGitHubの `main` ブランチに送る

ここまで成功すると、**Vercelが自動でビルドとデプロイを開始**します。

### 2. Vercelのダッシュボードを開く

1. ブラウザで [https://vercel.com](https://vercel.com) を開く
2. ログインする（GitHubで連携している場合はそのまま）
3. 一覧から **このプロジェクト**（例: facilitator-styles）をクリック

### 3. デプロイの進み具合を確認する

- プロジェクトを開くと **「Deployments」** の一覧が表示されます
- いちばん上にあるのが **いま進行中 or 直近のデプロイ** です
- **Status** が `Building` → `Ready` になれば本番反映完了です
- 途中でエラーになった場合は **Status** が `Error` になり、ログで原因を確認できます

### 4. 本番のURLを開いて確認する

- 一覧のデプロイ行の **「Visit」** をクリックするか
- プロジェクトの **「Domains」** に書いてあるURL（例: `https://〇〇.vercel.app`）をブラウザで開く

ここで表示されているサイトが **本番環境** です。  
今後も `main` に `git push` するたびに、同じ手順で自動で本番が更新されます。

### うまくいかないとき

- **デプロイが始まらない**  
  → GitHubにプッシュできているか確認（`git status` で `Your branch is up to date with 'origin/main'` になっているか）
- **ビルドが失敗する（Status: Error）**  
  → そのデプロイをクリックして **「Building」** のログを開き、赤いエラーメッセージを確認。  
  → ローカルで `npm run build` を実行すると、同じエラーを再現して原因を探せます
- **古い画面のまま**  
  → ブラウザのハードリロード（Ctrl+Shift+R / Cmd+Shift+R）やシークレットウィンドウでURLを開いてみる

---

## トラブルシューティング

### ビルドエラーが発生する場合

```bash
# ローカルでビルドを確認
npm run build
```

エラーメッセージを確認し、修正してから再デプロイ。

### 404エラーが発生する場合

SPAのルーティング設定が必要な場合、`vercel.json`を追加:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### 依存関係のエラー

```bash
# node_modulesとpackage-lock.jsonを削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

---

## 更新・再デプロイ

### GitHubリポジトリ経由の場合

```bash
git add .
git commit -m "Update: 機能改善"
git push origin main
```

自動的にVercelが再デプロイします。

### Vercel CLIの場合

```bash
vercel --prod
```

---

## 参考リンク

- [Vercel公式ドキュメント](https://vercel.com/docs)
- [Vite + Vercelガイド](https://vitejs.dev/guide/static-deploy.html#vercel)
