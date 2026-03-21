# app_Facilitator_reflection — プロジェクトメモ

## 概要
ファシリテーターが自分の活動を振り返るWebアプリ。

## 起動
```bash
cd Project/app_Facilitator_reflection
npm run dev  # → http://localhost:5173
```

## 構造
```
app_Facilitator_reflection/
├── src/
│   ├── components/     ← Reactコンポーネント
│   └── ...
├── index.html
├── vite.config.ts      ← Viteビルド設定
├── tailwind.config.js  ← TailwindCSS設定
├── package.json
└── dist/               ← ビルド成果物（gitignore対象）
```

## コマンド
```bash
npm run dev      # 開発サーバー起動
npm run build    # プロダクションビルド
npm run test     # テスト実行
```

## スタック
TypeScript / React / Vite / TailwindCSS
