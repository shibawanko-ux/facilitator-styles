# レポート生成モジュール設計（12_report_module_design）

本ドキュメントは [11_report_agent.md](11_report_agent.md) を正として、レポート生成モジュールの**設計のみ**を提案する。実装は別フェーズで行う。

---

## 1. 概要

- **入力**: 同一ルームの評価一覧（生データ）。`evaluations[]` と `roomId` を想定。
- **出力**: UI がそのまま表示できるレポート JSON（09 §2 の形式）。
- **2モード**: 「テンプレ出力のみ」と「AI で自然化」を切替可能にする。

---

## 2. reportAgentInput を作る関数（集計 → 分析済みデータ化）

### 2.1 責務

- **入力**: 生データ（`roomId`, `evaluations`: `{ id, room_id, role, scores }[]`）。既存の `EvaluationWithScoresAndRole` 相当を想定。
- **出力**: 09 §3 で定義した**分析済みデータ**（`ReportAgentInput` 型）。AI に渡す／テンプレ選択に使う。

集計と分析を**1本の関数**にまとめ、生データを外に漏らさない。

### 2.2 関数シグネチャ（案）

```ts
function buildReportAgentInput(
  roomId: string,
  evaluations: EvaluationWithScoresAndRole[]
): ReportAgentInput
```

- `evaluations` が 0 件の場合はエラーとするか、空の分析済みデータを返すかは実装時に決定する（設計上は「0件は呼び出し側で弾く」でも可）。

### 2.3 内部で行う計算（09 §3.1 必須項目に沿う）

| 必須項目 | 算出方法（案） |
|----------|----------------|
| **n（回答者数）** | `evaluations.length`。有効な scores が 1 件もない行は除外するかどうかは実装で規定。 |
| **全体平均** | 全評価の全項目（E1〜F4）のスコアを平たく平均。既存 `computeAverages` の結果から再計算するか、専用で 1 回で求める。 |
| **6軸の総合点（平均）＋平均との差** | 役割を問わず各軸（design, visibility, observation, hold, questioning, flow）のセクション平均を算出。全体平均との差 `diffFromOverall` を付与。実装は `computeSixAxisAveragesByRole` 等を利用。 |
| **最高の軸・最低の軸（平均との差）** | 6軸のセクション平均の max / min を特定し、それぞれ `section`, `mean`, `diffFromOverall` を設定。`section` は 6軸キー。 |
| **ばらつきが大きい軸（あれば）** | 各軸内の項目スコアの標準偏差（または IQR）を算出。閾値を超えた軸を `highVarianceSections[]` に列挙。 |
| **役割別の差分が大きい軸（あれば）** | 役割別セクション平均の max−min を各軸で算出。閾値を超えた軸を `highRoleDiffSections[]` に列挙。 |
| **状態タイプ分類** | セクション平均・役割間差のパターンから、09 で定義した状態タイプ ID を 1 つ以上付与。 |

既存の `resultAnalysis.ts` の `computeSixAxisAveragesByRole` 等を**利用**し、全体平均・diffFromOverall・最高/最低軸・ばらつき・役割差・状態タイプ・スコア帯→ラベルを組み立てる。

### 2.4 スコア帯 → 意味ラベル（09 §4）

- セクション平均を 09 §4 の帯（very_high / high / standard / improvement / attention）にマッピングする。
- `buildReportAgentInput` の最後で各**軸**の `sectionLabels` を付与する。

### 2.5 ReportAgentInput の型（案）

09 §3.2 の JSON に合わせた型。実装時は同一のキー名とする。**SectionKey は 6軸**。

```ts
type SectionKey = 'design' | 'visibility' | 'observation' | 'hold' | 'questioning' | 'flow'

interface ReportAgentInputMeta {
  roomId: string
  n: number
  roleCounts: { main: number; sub: number; participant: number }
}

interface SectionWithDiff {
  mean: number
  diffFromOverall: number
}

interface ReportAgentInputAverages {
  overall: number
  bySection: Record<SectionKey, SectionWithDiff>
  byRole: {
    main: Record<SectionKey, number>
    sub: Record<SectionKey, number>
    participant: Record<SectionKey, number>
  }
}

interface HighestLowestSection {
  section: SectionKey
  mean: number
  diffFromOverall: number
}

interface HighVarianceSection {
  section: SectionKey
  stdDev: number
  mean: number
}

interface HighRoleDiffSection {
  section: SectionKey
  maxMinDiff: number
  description: string
}

interface StateType {
  id: string
  label: string
}

interface SectionLabel {
  label: string
  band: 'very_high' | 'high' | 'standard' | 'improvement' | 'attention'
}

export interface ReportAgentInput {
  meta: ReportAgentInputMeta
  averages: ReportAgentInputAverages
  highestSection: HighestLowestSection
  lowestSection: HighestLowestSection
  highVarianceSections: HighVarianceSection[]
  highRoleDiffSections: HighRoleDiffSection[]
  stateTypes: StateType[]
  sectionLabels: Record<SectionKey, SectionLabel>
}
```

---

## 3. reportAgentOutput の型（UI 表示に合わせる）

09 §2 の JSON 構造をそのまま型定義する。UI が期待するキーと一致させる。

### 3.1 型定義（案）

```ts
// 箇条書き＋説明があるブロック
interface BulletsBlock {
  bullets: string[]
}

interface SummaryBlock {
  factSentence: string
  bullets: string[]
}

interface NextActionsBlock {
  summary: string
  bullets: string[]
}

interface ActionProposalBlock {
  summary: string
  bullets: string[]
}

interface SectionCommentsBlock {
  design: BulletsBlock
  visibility: BulletsBlock
  observation: BulletsBlock
  hold: BulletsBlock
  questioning: BulletsBlock
  flow: BulletsBlock
}

interface ReflectionQuestionItem {
  question: string
  intent: string
}

export interface ReportAgentOutput {
  summary: SummaryBlock
  strengths: BulletsBlock
  improvementHypotheses: BulletsBlock
  nextActions: NextActionsBlock
  sectionComments: SectionCommentsBlock
  reflectionQuestions: ReflectionQuestionItem[]   // 長さ 3
  actionProposal: ActionProposalBlock
}
```

- `reflectionQuestions` は 3 問固定（09 §7）。型で長さを強制するかは実装方針に任せる（`[ReflectionQuestionItem, ReflectionQuestionItem, ReflectionQuestionItem]` や readonly タプルも可）。

---

## 4. 「テンプレ出力のみ」モードと「AI で自然化」モードの切替

### 4.1 モードの意味

| モード | 説明 |
|--------|------|
| **テンプレ出力のみ** | `ReportAgentInput` から、09 §6 の示唆テンプレ辞書と §7 の振り返りの問い・§8 のアクション提案ルールに従い、**テンプレート文を選んで組み立てるだけ**で `ReportAgentOutput` を生成する。AI 呼び出しは行わない。 |
| **AI で自然化** | 上記のテンプレ出力（または同じ入力から組み立てた下書き）を AI に渡し、09 §5・§9 のルールに従って**自然な文言に整える**。出力型は同じ `ReportAgentOutput`。 |

どちらのモードでも**出力型は同一**（`ReportAgentOutput`）とし、UI はモードを意識せず表示できるようにする。

### 4.2 切替方法（案）

- **関数レベル**: `generateReport(input: ReportAgentInput, options: { mode: 'template_only' | 'ai_naturalize' }): Promise<ReportAgentOutput>` のようにオプションでモードを指定する。
- **実行時設定**: 環境変数や設定フラグで「AI 利用可能か」を切り、利用不可のときは自動で `template_only` にフォールバックする設計も可。

### 4.3 処理フロー（案）

1. `buildReportAgentInput(roomId, evaluations)` で分析済みデータを得る。
2. `generateReport(input, { mode })` を呼ぶ。
   - **template_only**: 入力に応じてテンプレを選択し、`ReportAgentOutput` を組み立てて返す（同期的でも可。Promise で統一しても可）。**テンプレ出力は品質ゲートを必ず満たす設計**とする。
   - **ai_naturalize**: （オプション）同じ入力でテンプレ出力を生成し、それを AI のプロンプトに含める。または分析済みデータのみを AI に渡し、出力 JSON をパースして `ReportAgentOutput` にする。実装時に 09 のプロンプト仕様と合わせる。**AI 出力は `validateReportComment(output)` で検証し、`ok: false` の場合はテンプレ出力にフォールバックする。**

### 4.4 品質ゲートとフォールバック（実装済み）

- **API**: `validateReportComment(output): { ok: boolean; errors: string[] }`（[13_quality_gate_and_polish.md](13_quality_gate_and_polish.md) 品質ゲート準拠）
- **AI 自然化時のフロー**: 自然化の結果を `validateReportComment` に渡す → `ok: false` ならテンプレ出力を返す。テンプレ出力はゲートを満たす前提のため、AI 無しでも成立する。

---

## 5. ユニットテスト用 fixture データ（2 ケース）

09 §10 の 2 ケースに合わせ、**分析済みデータ（ReportAgentInput）** の fixture を 2 件定義する。テストでは「この入力に対してテンプレモードで生成した出力が、期待する構造と内容を持つこと」を検証するのに使う。

### 5.1 ケース 1: 安全性高・挑戦不足型（safety_high_challenge_low）

- **意図**: 場のホールド・安心感が最も高く、流れ・即興が相対的に低い。安心感は高いが流れの編集・柔軟性に余裕がなかったと読めるパターン。

**fixture: `reportAgentInputFixture_safetyHighChallengeLow`**（実装は `__tests__/fixtures_reportPipeline.ts` の inputFixtureCase1 等を参照）

- `meta.n`: 3（メイン1 + 参加者2）。サブなし。
- `averages.bySection` / `byRole`: 6軸キー（design, visibility, observation, hold, questioning, flow）で値を設定。
- `highestSection`: section: `hold`, mean: 4.2 程度
- `lowestSection`: section: `flow`, mean: 3.5 程度
- `stateTypes`: `[{ id: 'safety_high_challenge_low', label: '安全性高・挑戦不足型' }]`
- `sectionLabels`: 各軸に 09 §4 の帯（very_high / high / standard / improvement / attention）を付与。

### 5.2 ケース 2: 説明・設計が低め・場の観察が高め

- **意図**: 説明・設計（design）が低く、場の観察・安心感が高い。全体設計・伝達は弱め、参加者観察は強めのパターン。

**fixture: `reportAgentInputFixture_designLowObservationHigh`**（実装は inputFixtureCase2 等を参照）

- `meta.n`: 4（メイン1、サブ1、参加者2）
- `averages.bySection` / `byRole`: 6軸キーで設定。design が最低軸、observation または hold が最高軸。
- `highestSection`: section: `hold` または `observation`
- `lowestSection`: section: `design`
- `stateTypes`: 全体設計弱め・参加者観察強めに相当する ID
- `sectionLabels`: design=improvement, observation/hold=high, flow=standard など。

数値は 09 §14 ケース2 および `fixtures_reportPipeline.ts` に合わせる。

### 5.3 fixture の置き場所と形式

- **ファイル**: `src/lib/__fixtures__/reportAgentInput.ts` または `src/lib/reportAgent/__tests__/fixtures.ts` など、テストとレポートモジュールの構成に合わせて配置。
- **形式**: `ReportAgentInput` 型に合うオブジェクトを export する。生の evaluations は不要。必要なら「この fixture からテンプレ出力を生成したときの期待値」を別ファイル（`reportAgentOutputFixture_*.ts`）で持つ。

---

## 6. モジュール・ファイル構成（案）

実装時に参照するための案。実装しない。

- `src/lib/reportAgent/types.ts`  
  - `ReportAgentInput`（09 §3.2 に合わせた型）, `ReportAgentOutput`（09 §2 に合わせた型）, その他ブロック型。
- `src/lib/reportAgent/buildReportAgentInput.ts`  
  - `buildReportAgentInput(roomId, evaluations)`。集計・分析・状態タイプ・ラベル付与まで一括。
- `src/lib/reportAgent/scoreBand.ts`  
  - セクション平均 → band ID / 意味ラベルのマッピング（09 §4）。
- `src/lib/reportAgent/stateTypes.ts`  
  - セクション平均・役割差のパターン → 状態タイプ ID / ラベル。
- `src/lib/reportAgent/generateFromTemplate.ts`  
  - テンプレのみモード: `ReportAgentInput` → `ReportAgentOutput`。
- `src/lib/reportAgent/validateReportComment.ts`  
  - 品質ゲート: `validateReportComment(output)` → `{ ok, errors }`。AI 自然化後に実行し、NG ならテンプレにフォールバックする。
- `src/lib/reportAgent/generateReport.ts`  
  - `generateReport(input, options)`。mode に応じてテンプレのみ or AI 自然化を呼び分け。ai_naturalize 時は結果を `validateReportComment` で検証し、不合格ならテンプレを返す。
- `src/lib/reportAgent/__tests__/`  
  - 上記 2 ケースの fixture を使ったユニットテスト。品質ゲートの合格・不合格ケースのテストを含む。

既存の `resultAnalysis.ts` はそのまま利用し、`buildReportAgentInput` から呼び出す形でよい。

---

## 7. 参照

- [11_report_agent.md](11_report_agent.md) … 入出力仕様・必須項目・スコア帯・状態タイプ・テンプレ辞書の正。
- [04_data_design.md](04_data_design.md) … evaluations のスキーマと集計の置き場所。
- [05_evaluation_items.md](05_evaluation_items.md) … 項目 ID（E1〜F4）と6軸の対応。
