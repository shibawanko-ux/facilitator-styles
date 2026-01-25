# ファシリスタイル - ファシリテーター診断

ファシリテーターとしての自分のスタイル・傾向を4つの軸で可視化し、自己理解と成長のヒントを提供する診断アプリです。

## 機能

- **32問の診断**: 4つの軸（各8問）で傾向を測定
- **16タイプ分類**: 4軸の組み合わせで16種類のファシリテータータイプに分類
- **詳細な結果表示**: 
  - タイプ名とキャッチコピー
  - 4軸のスコア可視化
  - 各軸の強み・弱み・成長ヒント
  - コーファシリとの組み合わせヒント
- **シェア機能**: X/Twitter、Facebook、LINE、クリップボードコピー
- **画像保存**: 結果を画像として保存可能

## 4つの軸

| 軸 | 両極 | 説明 |
|---|---|---|
| 介入スタイル | 触発型 ⇔ 見守型 | 場への働きかけ方 |
| 知覚対象 | 観察型 ⇔ 洞察型 | 情報の捉え方 |
| 判断基準 | 目的型 ⇔ 関係型 | 意思決定の優先順位 |
| 場への関わり | 設計型 ⇔ 即興型 | 進行スタイル |

## 技術スタック

- **フレームワーク**: React 18 + TypeScript
- **ビルドツール**: Vite 5
- **スタイリング**: Tailwind CSS 3
- **画像生成**: html2canvas

## セットアップ

### 必要環境

- Node.js 18以上
- npm または yarn

### インストール

```bash
# リポジトリをクローン（または任意のディレクトリで実行）
cd app_Facilitator_type_diagnosis

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

### ビルド

```bash
# プロダクションビルド
npm run build

# ビルド結果をプレビュー
npm run preview
```

## ディレクトリ構成

```
app_Facilitator_type_diagnosis/
├── docs/                        # ドキュメント
│   ├── 01_requirements.md       # 要件定義書
│   ├── 02_questions.md          # 質問項目一覧
│   ├── 03_axis_contents.md      # 各軸のコンテンツ
│   ├── 04_16types.md            # 16タイプの説明
│   └── 05_cofacili_hints.md     # コーファシリヒント
├── src/
│   ├── components/              # UIコンポーネント
│   │   ├── TopPage.tsx          # トップページ
│   │   ├── QuestionPage.tsx     # 質問画面
│   │   ├── ResultPage.tsx       # 結果画面
│   │   ├── ScoreChart.tsx       # スコアチャート
│   │   ├── AxisDetail.tsx       # 軸の詳細表示
│   │   ├── CofaciliSection.tsx  # コーファシリヒント
│   │   └── ShareSection.tsx     # シェア機能
│   ├── data/                    # データ定義
│   │   ├── types.ts             # 型定義
│   │   ├── questions.ts         # 質問データ
│   │   ├── facilitatorTypes.ts  # 16タイプデータ
│   │   ├── axisContents.ts      # 軸コンテンツ
│   │   └── cofaciliHints.ts     # コーファシリヒント
│   ├── hooks/
│   │   └── useDiagnosis.ts      # 診断ロジックフック
│   ├── utils/
│   │   └── scoring.ts           # スコアリングロジック
│   ├── App.tsx                  # メインアプリ
│   ├── main.tsx                 # エントリーポイント
│   └── index.css                # グローバルスタイル
├── public/
│   └── favicon.svg              # ファビコン
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## ライセンス

MIT License

## 作者

ファシリスタイル開発チーム
