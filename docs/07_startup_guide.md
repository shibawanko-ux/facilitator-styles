# ファシリスタイル 起動方法ガイド

---

## 【Cursor で起動する方法（推奨）】

### ステップ1：Cursor で新しいターミナルを開く

Cursor のメニューから：
- **ターミナル** → **新しいターミナル** をクリック

または、キーボードショートカット：
- Mac: `Control + Shift + @`

### ステップ2：プロジェクトフォルダに移動する

ターミナルに以下をコピー＆ペーストして、**Enter** を押す：

```
cd app_Facilitator_type_diagnosis
```

### ステップ3：依存関係をインストールする（初回のみ）

ターミナルに以下をコピー＆ペーストして、**Enter** を押す：

```
npm install
```

※ 数分かかることがあります。完了するまで待ってください。

### ステップ4：開発サーバーを起動する

ターミナルに以下をコピー＆ペーストして、**Enter** を押す：

```
npm run dev
```

以下のようなメッセージが表示されたら成功です：

```
  VITE v5.x.x  ready

  ➜  Local:   http://localhost:5173/
```

### ステップ5：ブラウザで開く

ターミナルに以下をコピー＆ペーストして、**Enter** を押す：

```
open http://localhost:5173/
```

ブラウザが自動的に開いて、アプリが表示されます。

### 停止するとき

ターミナルで `Control + C` を押す

---

## 【2回目以降の起動方法】

### ステップ1：Cursor でターミナルを開く

### ステップ2：以下を順番に実行

```
cd app_Facilitator_type_diagnosis
```

```
npm run dev
```

```
open http://localhost:5173/
```

---

## 【注意事項】

- `index.html` を直接ブラウザで開いても動作しません
- 必ず `npm run dev` でサーバーを起動してからブラウザでアクセスしてください
- `npm: command not found` と表示される場合は、Node.js がインストールされていません（下記参照）

---

## 必要な環境

- **Node.js**: バージョン 18 以上
- **npm**: Node.js に付属

### Node.js のインストール確認

ターミナルで以下のコマンドを実行して、バージョンを確認してください。

```bash
node -v
# 例: v18.17.0 または v20.x.x

npm -v
# 例: 9.x.x または 10.x.x
```

Node.js がインストールされていない場合は、[Node.js 公式サイト](https://nodejs.org/) からダウンロードしてください。

---

## セットアップ手順

### 1. プロジェクトディレクトリに移動

```bash
cd app_Facilitator_type_diagnosis
```

### 2. 依存関係をインストール

```bash
npm install
```

初回のみ必要です。`node_modules` フォルダと `package-lock.json` が作成されます。

---

## 起動方法

### 開発サーバーを起動

```bash
npm run dev
```

起動後、以下のようなメッセージが表示されます。

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### ブラウザでアクセス

ブラウザを開いて、以下のURLにアクセスしてください。

```
http://localhost:5173/
```

開発サーバーは **ホットリロード** に対応しているため、コードを変更すると自動的にブラウザに反映されます。

### ターミナルからブラウザを開く

開発サーバー起動後、別のターミナルウィンドウで以下のコマンドを実行するとブラウザが開きます。

```bash
# macOS
open http://localhost:5173/

# Windows
start http://localhost:5173/

# Linux
xdg-open http://localhost:5173/
```

### 自動でブラウザを開く（オプション）

`npm run dev` 実行時に自動的にブラウザを開きたい場合は、`--open` オプションを付けます。

```bash
npm run dev -- --open
```

### 開発サーバーを停止

ターミナルで `Ctrl + C` を押すと停止します。

---

## 本番ビルド

本番用のファイルを生成する場合は、以下のコマンドを実行します。

```bash
npm run build
```

`dist/` フォルダに最適化されたファイルが生成されます。

### ビルド結果のプレビュー

ビルドした結果をローカルで確認する場合：

```bash
npm run preview
```

`http://localhost:4173/` でプレビューできます。

---

## よくあるトラブル

### index.html を直接開いても動作しない

このプロジェクトは React + Vite で構築されているため、`index.html` ファイルを直接ブラウザにドラッグ＆ドロップしたり、ファイルパスでアクセスしても動作しません。

**必ず開発サーバー経由（`npm run dev`）でアクセスしてください。**

### `npm install` でエラーが出る

```bash
# node_modules を削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

### ポート 5173 が使用中

別のアプリケーションがポートを使用している場合、Vite は自動的に別のポート（5174 など）を使用します。ターミナルに表示される URL を確認してください。

### Node.js のバージョンが古い

Node.js 18 以上が必要です。バージョンを確認し、必要に応じてアップデートしてください。

---

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `npm install` | 依存関係をインストール |
| `npm run dev` | 開発サーバーを起動 |
| `npm run build` | 本番用ビルドを作成 |
| `npm run preview` | ビルド結果をプレビュー |

---

## 次のステップ

- 動作確認ができたら、[06_deploy_guide.md](./06_deploy_guide.md) を参照して Vercel へデプロイしてください。
