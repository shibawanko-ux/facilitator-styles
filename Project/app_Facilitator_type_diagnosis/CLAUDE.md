# app_Facilitator_type_diagnosis — プロジェクトメモ

## 概要
ファシリテーターのタイプを診断するWebアプリ。Vercelにデプロイ済み。

## 起動
```bash
cd Project/app_Facilitator_type_diagnosis
npm run dev  # → http://localhost:5173
```

## 構造
```
Project/app_Facilitator_type_diagnosis/
├── src/
├── public/
├── index.html
├── vercel.json         ← Vercelデプロイ設定
├── package.json
└── dist/               ← ビルド成果物（gitignore対象）
```

## コマンド
```bash
npm run dev      # 開発サーバー起動
npm run build    # プロダクションビルド（Vercelデプロイ前に実行）
```

## スタック
TypeScript / React / Vite / TailwindCSS / Vercel
