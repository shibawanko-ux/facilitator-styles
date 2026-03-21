# レポート品質ゲート・AI 整形（13_quality_gate_and_polish）

レポート出力の**品質ゲート**と、**AI による言い回し整形（polish）**の仕様をまとめる。

**参照**: [11_report_agent.md](11_report_agent.md) 出力フォーマット・禁止事項、[14_report_structure.md](14_report_structure.md) 結果画面の3セクション。

---

## 1. 品質ゲート

### 1.1 目的

- コメント出力を安定させるため、生成結果に**品質ゲート**を設ける。
- **テンプレ出力は必ず合格する**（AI 無しでも成立）。
- **AI 自然化を使う場合**は、出力がルール違反したら**テンプレにフォールバック**する。

### 1.2 品質ゲート（最低限の5項目）

| # | 項目 | 判定内容 |
|---|------|----------|
| 1 | 観点名の出現 | 6軸の観点名（説明・設計、見える化・編集、場の観察、場のホールド・安心感、問いかけ・リフレーミング、流れ・即興）の**いずれかが少なくとも1回**は全文に含まれる |
| 2 | 4ブロックの存在 | 強み・改善仮説・次回アクション（2点以上）・総評の4ブロックが揃っている（summary, strengths, improvementHypotheses, nextActions が非空かつ nextActions.bullets が2本以上） |
| 3 | 抽象語のみでない | 「良かった」「学びがあった」等の抽象語**のみ**で終わっていない（具体的な観察・相対差・アクションのいずれかが含まれる） |
| 4 | 相対差の言及 | 平均との差 or 高低差の言及が**1回以上**ある（例: 高め／低め／○点差／平均との差） |
| 5 | 文字数上限 | 各ブロック 200 字以内（UI 想定）。対象: summary, strengths, improvementHypotheses, nextActions の各ブロック全体 |

### 1.3 実装

- **API**: `validateReportComment(output: ReportAgentOutput): { ok: boolean; errors: string[] }`  
  - 実装: `src/lib/reportAgent/validateReportComment.ts`
  - 合格時: `ok: true`, `errors: []`
  - 不合格時: `ok: false`, `errors: ['理由1', '理由2', ...]`
- **AI 自然化のフロー**: 自然化の後に `validateReportComment` を実行 → **NG ならテンプレ出力に差し替える**（`generateReport` に組み込み済み）
- **テスト**: `src/lib/reportAgent/__tests__/validateReportComment.test.ts`

---

## 2. AI 言い回し整形（polish）

### 2.1 目的

- ワークショップ振り返りレポートの**言い回しのみ**を AI で整形する。意味・数値・構造は変えず、自然な日本語に整える。
- 実装: [generateReport.ts](../src/lib/reportAgent/generateReport.ts) の `polishWithAI`、[polishAiPrompt.ts](../src/lib/reportAgent/polishAiPrompt.ts) を参照。

### 2.2 制約（プロンプトに含める）

| # | 制約 | 説明 |
|---|------|------|
| 1 | **数値・差分・意味を一切変えない** | スコア、役割名（メイン／サブ／参加者）、6軸の観点名（説明・設計、見える化・編集、場の観察、場のホールド・安心感、問いかけ・リフレーミング、流れ・即興）、高低・差の事実はそのまま。情報の追加・削除・変更禁止。 |
| 2 | **箇条書き構造を維持** | 各 `bullets` 配列の**要素数**を変えない。順序の入れ替え・まとめ・分割禁止。 |
| 3 | **断定を増やさない** | 推測は「〜の可能性」「〜と読める」「〜と解釈できる」等を維持する。 |
| 4 | **研修っぽい一般論を追加しない** | 元テキストにない一般論を足さない。 |

### 2.3 出力形式

- 必ず**同じ JSON キー構造**で返す。[11_report_agent.md §2](11_report_agent.md) および `ReportAgentOutput` 型に合わせる。
- 必須キー: `summary`（factSentence, bullets）, `strengths`, `improvementHypotheses`, `nextActions`, `sectionComments`（**design, visibility, observation, hold, questioning, flow** 各 bullets）, `reflectionQuestions`（3件）, `actionProposal`。

### 2.4 禁止事項

- 研修っぽい一般論の追加、根拠のない断定、満足度要約の追加、抽象語のみへの置き換え。

### 2.5 システムプロンプト（要約）

制約 1〜4 を明記し、**sectionComments は 6軸キー（design, visibility, observation, hold, questioning, flow）** で返す旨を記載する。返答は JSON のみ。

### 2.6 実装時の注意

- 整形後の出力は `validateReportComment` を通す。不合格の場合はテンプレにフォールバックする。
