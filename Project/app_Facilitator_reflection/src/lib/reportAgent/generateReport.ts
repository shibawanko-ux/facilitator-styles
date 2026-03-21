/**
 * レポートコメント生成パイプライン（11_report_agent.md 準拠）
 * 1) renderTemplateComment でテンプレのみ JSON
 * 2) 任意で polishWithAI（言い回しのみ整形）
 * 3) validateReportComment を通す
 * 4) NG ならテンプレにフォールバック
 * 5) 文字数上限で truncate
 */

import type { ReportAgentInput, ReportAgentOutput } from './types'
import { renderTemplateComment } from './renderTemplateComment'
import { validateReportComment } from './validateReportComment'
import { truncateReportOutput } from './truncateReportOutput'

export interface GenerateReportOptions {
  /** true のとき polishWithAI を呼ぶ（未実装の場合は無視） */
  useAI?: boolean
  /** テスト用: AI の代わりにこの関数を使う */
  polishWithAIFn?: (
    templateOutput: ReportAgentOutput,
    input: ReportAgentInput
  ) => Promise<ReportAgentOutput | null>
}

/**
 * TODO: polishWithAI 実装時の「意味不変の制約」（言い回しのみ整形し、意味・構造は変えない）
 *
 * - 数値や差分の追加/削除禁止 … 点・差・〇点・高め/低め等の数値・相対差表現を増減させない
 * - bullets 数の変更禁止 … summary/strengths/improvementHypotheses/nextActions/sectionComments 等の各 bullets 配列の要素数はテンプレと同一にすること
 * - JSON キー構造固定 … ReportAgentOutput のキー（summary, strengths, sectionComments 等）の追加・削除・改名禁止
 * - polish 後に validate を必ず通し、NG ならテンプレへフォールバック … 本ファイルの generateReport 内で既に実施。実装側は validate を通す前提で出力すること
 */
/**
 * AI で言い回しのみ整形する。意味は変えず。
 * 未実装の場合は null を返し、呼び出し側でテンプレをそのまま使う。
 */
export async function polishWithAI(
  _templateOutput: ReportAgentOutput,
  _input: ReportAgentInput
): Promise<ReportAgentOutput | null> {
  return null
}

/**
 * レポートコメントを生成する。
 * テンプレは必ず品質ゲートを通る設計。AI 使用時は validate NG でテンプレにフォールバックする。
 */
export async function generateReport(
  input: ReportAgentInput,
  options?: GenerateReportOptions
): Promise<ReportAgentOutput> {
  const templateOutput = renderTemplateComment(input)

  let output: ReportAgentOutput = templateOutput
  const polishFn = options?.polishWithAIFn ?? polishWithAI
  if (options?.useAI) {
    const polished = await polishFn(templateOutput, input)
    if (polished) output = polished
  }

  const result = validateReportComment(output)
  if (!result.ok) {
    output = templateOutput
  }

  return truncateReportOutput(output)
}

/**
 * 同期的にテンプレのみで生成（AI なし・validate 済み前提）
 */
export function generateReportSync(input: ReportAgentInput): ReportAgentOutput {
  const templateOutput = renderTemplateComment(input)
  return truncateReportOutput(templateOutput)
}
