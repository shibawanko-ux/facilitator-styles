# 起動手順（動作確認用）

ファシリテーターリフレクションを手元で動かして動作確認するための、最短の起動手順です。

---

## 前提

- **Node.js** がインストールされていること（LTS 推奨）
  - 確認: ターミナルで `node -v` と `npm -v` を実行し、バージョンが表示されれば OK

---

## 手順

### 1. プロジェクトフォルダへ移動

ターミナルで、このアプリのフォルダに移動します。

```bash
cd Project/app_Facilitator_reflection
```

（リポジトリのルートにいる場合は、上記の通り。すでに `app_Facilitator_reflection` の中にいる場合は不要です。）

### 2. 依存関係のインストール（初回または package.json 変更後）

初めて起動するときや、`package.json` を変更したあとは、次を実行します。

```bash
npm install
```

### 3. 開発サーバーを起動

次を実行します。

```bash
npm run dev
```

ターミナルに、次のような表示が出ます。

```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 4. （任意）Supabase を使う場合

- ルーム作成・評価入力など DB を使う機能を試すには、**環境変数**の設定が必要です。
- プロジェクト直下に `.env` または `.env.local` を用意し、`VITE_SUPABASE_URL` と `VITE_SUPABASE_ANON_KEY` を設定してください。雛形は `.env.example` をコピーして編集します。
- 設定後は開発サーバーを一度止めて（Ctrl+C）から、再度 `npm run dev` で起動してください。詳細は [08_implementation_guide_beginner.md](08_implementation_guide_beginner.md) の Step 8 を参照。

### 5. ブラウザで開く

- ブラウザで **http://localhost:5173/** を開きます。
- 「ファシリテーターリフレクション」と「Step 8 まで完了しました。」が表示されれば、起動は成功です。Supabase を設定している場合は「Supabase 接続設定済み」も表示されます。

### 6. 終了するとき

- 開発サーバーを止めるには、ターミナルで **Ctrl + C** を押します。

---

## 本番ビルドの確認（任意）

本番用のビルドが通るかだけ確認したい場合:

```bash
npm run build
```

成功すると `dist/` フォルダができ、その中に HTML と JS/CSS が出力されます。ローカルで本番に近い表示を確認するには:

```bash
npm run preview
```

表示された URL（例: http://localhost:4173）をブラウザで開いて確認できます。

---

## うまく起動しないとき

| 症状 | 確認すること |
|------|----------------|
| `node: command not found` | Node.js をインストールする（[nodejs.org](https://nodejs.org/) の LTS 版） |
| `npm install` でエラー | ネット接続を確認。Proxy 環境の場合は設定を確認 |
| ポート 5173 が使われている | 別のターミナルで 5173 を使っているプロセスを終了するか、Vite が表示する別のポートで開く |
| 画面が真っ白 | ブラウザの開発者ツール（F12）のコンソールでエラーを確認 |

---

## 関連ドキュメント

- 初めてセットアップする流れ: [08_implementation_guide_beginner.md](08_implementation_guide_beginner.md)（Step 1〜8）
- 環境変数（Supabase）の設定: 06 の Step 8 を参照
