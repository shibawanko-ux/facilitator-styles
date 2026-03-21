/**
 * レポートエージェント入出力の型定義（11_report_agent.md §2 / §3.2 準拠・6軸）
 */

/** 6軸の軸ID（03 §4・09 sectionComments キー） */
export type SectionKey =
  | 'design'
  | 'visibility'
  | 'observation'
  | 'hold'
  | 'questioning'
  | 'flow'

export const SECTION_KEYS: SectionKey[] = [
  'design',
  'visibility',
  'observation',
  'hold',
  'questioning',
  'flow',
]

/** 状態タイプ分類（classifyWorkshopState の戻り値） */
export interface StateType {
  id: string
  label: string
}

/** スコア帯（09 §4） */
export type BandId =
  | 'very_high'
  | 'high'
  | 'standard'
  | 'improvement'
  | 'attention'

/** 各視点のスコア帯ラベル（renderTemplate で使用） */
export interface SectionLabel {
  label: string
  band: BandId
}

/** 状態タイプ判定に必要な分析データの最小形（buildReportAgentInput の出力の一部） */
export interface WorkshopAnalysisForClassification {
  averages: {
    bySection: Record<SectionKey, { mean: number }>
  }
  highestSection: { section: SectionKey; mean: number }
  lowestSection: { section: SectionKey; mean: number }
  highVarianceSections: Array<{ section: SectionKey; stdDev: number }>
  highRoleDiffSections: Array<{ section: SectionKey; maxMinDiff: number }>
}

/** 役割別セクション平均（factSentence 用） */
export interface ByRoleSectionMeans {
  main: Record<SectionKey, number>
  sub: Record<SectionKey, number>
  participant: Record<SectionKey, number>
}

/** renderTemplateComment の入力（分析済みデータ＋roomId＋sectionLabels） */
export interface ReportAgentInput extends Omit<WorkshopAnalysisForClassification, 'averages'> {
  meta: { roomId: string }
  sectionLabels: Record<SectionKey, SectionLabel>
  averages: WorkshopAnalysisForClassification['averages'] & {
    byRole?: ByRoleSectionMeans
  }
}

/** 箇条書きのみのブロック */
export interface BulletsBlock {
  bullets: string[]
}

/** 総評ブロック（事実1文＋箇条書き） */
export interface SummaryBlock {
  factSentence: string
  bullets: string[]
}

/** 次回アクション／アクション提案ブロック */
export interface NextActionsBlock {
  summary: string
  bullets: string[]
}

/** 6軸ごとの分析コメント（09 §2 sectionComments） */
export interface SectionCommentsBlock {
  design: BulletsBlock
  visibility: BulletsBlock
  observation: BulletsBlock
  hold: BulletsBlock
  questioning: BulletsBlock
  flow: BulletsBlock
}

/** 振り返りの問い1件 */
export interface ReflectionQuestionItem {
  question: string
  intent: string
}

/**
 * レポート生成結果（UI がそのまま表示する形）
 * 09 §2 の JSON 構造に合わせる。
 * sharedLeadershipReflectionQuestions は 03 の振り返り拡張。サブがいる場合に結果画面で表示する。
 */
export interface ReportAgentOutput {
  summary: SummaryBlock
  strengths: BulletsBlock
  improvementHypotheses: BulletsBlock
  nextActions: NextActionsBlock
  sectionComments: SectionCommentsBlock
  reflectionQuestions: ReflectionQuestionItem[]
  /** シェアドリーダーシップ・認知の振り返り用（03）。サブが1人以上いるときに表示。 */
  sharedLeadershipReflectionQuestions?: ReflectionQuestionItem[]
  actionProposal: NextActionsBlock
}
