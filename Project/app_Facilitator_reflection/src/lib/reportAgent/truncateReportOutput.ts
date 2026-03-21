/**
 * レポート出力の文字数上限（各ブロック200字、bullets 各80字程度）
 * 超えた場合は安全に truncate する。
 */

import type { ReportAgentOutput } from './types'

const MAX_CHARS_PER_BLOCK = 200
const MAX_CHARS_PER_BULLET = 80
const MAX_FACT_SENTENCE = 120
const TRUNCATE_SUFFIX = '…'

function truncateStr(s: string, maxLen: number): string {
  if (s.length <= maxLen) return s
  return s.slice(0, maxLen - TRUNCATE_SUFFIX.length) + TRUNCATE_SUFFIX
}

/**
 * 各ブロックを 200 字以内、各 bullet を 80 字以内に安全に切り詰める。
 */
export function truncateReportOutput(output: ReportAgentOutput): ReportAgentOutput {
  const factSentence = truncateStr(output.summary.factSentence, MAX_FACT_SENTENCE)
  const summaryBullets = output.summary.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET))
  const summaryBlock = [factSentence, ...summaryBullets].join('')
  const summary =
    summaryBlock.length > MAX_CHARS_PER_BLOCK
      ? { factSentence, bullets: summaryBullets.slice(0, 1).map((b) => truncateStr(b, MAX_CHARS_PER_BLOCK - factSentence.length - 2)) }
      : { factSentence, bullets: summaryBullets }

  const strengthsBullets = output.strengths.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET))
  const strengthsBlock = strengthsBullets.join('')
  const strengths =
    strengthsBlock.length > MAX_CHARS_PER_BLOCK
      ? { bullets: strengthsBullets.slice(0, 2).map((b) => truncateStr(b, 99)) }
      : { bullets: strengthsBullets }

  const improvementBullets = output.improvementHypotheses.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET))
  const improvementBlock = improvementBullets.join('')
  const improvementHypotheses =
    improvementBlock.length > MAX_CHARS_PER_BLOCK
      ? { bullets: improvementBullets.slice(0, 2).map((b) => truncateStr(b, 99)) }
      : { bullets: improvementBullets }

  const nextActionsSummary = truncateStr(output.nextActions.summary, MAX_CHARS_PER_BULLET)
  const nextActionsBullets = output.nextActions.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET))
  const nextActionsBlock = nextActionsSummary + nextActionsBullets.join('')
  const nextActions =
    nextActionsBlock.length > MAX_CHARS_PER_BLOCK
      ? { summary: truncateStr(output.nextActions.summary, 80), bullets: nextActionsBullets.map((b) => truncateStr(b, 60)) }
      : { summary: output.nextActions.summary, bullets: nextActionsBullets }

  const result: ReportAgentOutput = {
    summary,
    strengths,
    improvementHypotheses,
    nextActions,
    sectionComments: {
      design: { bullets: output.sectionComments.design.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
      visibility: { bullets: output.sectionComments.visibility.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
      observation: { bullets: output.sectionComments.observation.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
      hold: { bullets: output.sectionComments.hold.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
      questioning: { bullets: output.sectionComments.questioning.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
      flow: { bullets: output.sectionComments.flow.bullets.map((b) => truncateStr(b, MAX_CHARS_PER_BULLET)) },
    },
    reflectionQuestions: output.reflectionQuestions,
    actionProposal: { summary: nextActions.summary, bullets: nextActions.bullets },
  }
  if (output.sharedLeadershipReflectionQuestions?.length) {
    result.sharedLeadershipReflectionQuestions = output.sharedLeadershipReflectionQuestions
  }
  return result
}
