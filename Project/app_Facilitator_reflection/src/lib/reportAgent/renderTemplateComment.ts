/**
 * テンプレのみでレポート JSON を生成（AI 無し・品質ゲート合格）
 * テンプレ選択は seed 固定の決定的選択（同じ input → 同じ output）。
 * seed = input.meta.roomId + sectionKey + band + stateType.id で同一文が選ばれる。
 */

import type { ReportAgentInput, ReportAgentOutput, SectionKey } from './types'
import { SECTION_KEYS } from './types'
import { classifyWorkshopState } from './classifyWorkshopState'
import { getTemplatesForStateType } from './stateTypeTemplates'
import { SECTION_COMMENT_TEMPLATES } from './sectionCommentTemplates'
import { REFLECTION_QUESTIONS_FIXED } from './reflectionQuestionsFixed'
import { SHARED_LEADERSHIP_REFLECTION_QUESTIONS_FIXED } from './sharedLeadershipReflectionQuestionsFixed'
import { selectN } from './deterministicSeed'

/** 6軸の表示名（総評・事実文用） */
const SECTION_LABEL_JA: Record<SectionKey, string> = {
  design: '説明・設計',
  visibility: '見える化・編集',
  observation: '場の観察',
  hold: '場のホールド・安心感',
  questioning: '問いかけ・リフレーミング',
  flow: '流れ・即興',
}

/** 総評の補足文用：軸ごとの領域名。1文を200字制約内に収めるため短め。 */
const SECTION_DOMAIN_JA: Record<SectionKey, string> = {
  design: '説明・設計',
  visibility: '見える化・編集',
  observation: '場の観察',
  hold: '場のホールド・安心感',
  questioning: '問いかけ・リフレーミング',
  flow: '流れ・即興',
}

const MAX_STRENGTHS_BULLETS = 3
const MAX_IMPROVEMENT_BULLETS = 3
const SECTION_COMMENT_BULLETS = 2

/**
 * 総評の事実文。点数は出さず、レーダーチャートで分かる数値は使わず、
 * 「そうだったのか」が伝わるテキストで表現する（最高・最低軸を文言で示す）。
 */
function buildFactSentence(input: ReportAgentInput): string {
  const byRole = input.averages.byRole
  const high = input.highestSection
  const low = input.lowestSection
  const highLabel = SECTION_LABEL_JA[high.section]
  const lowLabel = SECTION_LABEL_JA[low.section]

  const base = `${highLabel}が最も高く評価され、${lowLabel}は相対的に低めで伸ばせる領域と読めます。`

  if (byRole?.main && byRole?.participant) {
    const sub = byRole.sub
    const hasSub = sub && SECTION_KEYS.some((k) => sub[k] > 0)
    if (hasSub) {
      return `${base}メイン・サブ・参加者とも傾向が近く、同じ強み・課題が共有されていたと解釈できます。`
    }
    return `${base}メインと参加者で傾向が近く、同じ強み・課題が共有されていたと解釈できます。`
  }

  return `${base}`
}

/**
 * テンプレのみでレポートコメントを生成する。
 * 同じ input なら常に同じ出力（seed 付き決定的選択）。
 */
export function renderTemplateComment(input: ReportAgentInput): ReportAgentOutput {
  const roomId = input.meta.roomId
  const stateType = classifyWorkshopState(input)
  const templates = getTemplatesForStateType(stateType)

  const factSentence = buildFactSentence(input)

  const strengthSeed = roomId + stateType.id + 'strengths'
  const strengthBullets = templates.strengths.bullets.slice(0, MAX_STRENGTHS_BULLETS)
  const nStrength = Math.min(MAX_STRENGTHS_BULLETS, Math.max(1, strengthBullets.length))
  const strengths = selectN(strengthBullets, nStrength, strengthSeed)

  const improvementBullets = templates.improvementHypotheses.bullets.slice(0, MAX_IMPROVEMENT_BULLETS)
  const improvementSeed = roomId + stateType.id + 'improvement'
  const nImprovement = Math.min(MAX_IMPROVEMENT_BULLETS, Math.max(1, improvementBullets.length))
  const improvementHypotheses = selectN(improvementBullets, nImprovement, improvementSeed)

  const sectionComments: ReportAgentOutput['sectionComments'] = {
    design: { bullets: [] },
    visibility: { bullets: [] },
    observation: { bullets: [] },
    hold: { bullets: [] },
    questioning: { bullets: [] },
    flow: { bullets: [] },
  }
  for (const section of SECTION_KEYS) {
    const band = input.sectionLabels[section]?.band ?? 'standard'
    const pool = SECTION_COMMENT_TEMPLATES[section][band] ?? SECTION_COMMENT_TEMPLATES[section].standard
    const seed = roomId + section + band + stateType.id
    sectionComments[section].bullets = selectN(pool, SECTION_COMMENT_BULLETS, seed)
    if (sectionComments[section].bullets.length === 0 && pool.length > 0) {
      sectionComments[section].bullets = [pool[0], pool.length > 1 ? pool[1] : pool[0]]
    }
  }

  const highDomain = SECTION_DOMAIN_JA[input.highestSection.section]
  const lowDomain = SECTION_DOMAIN_JA[input.lowestSection.section]
  const domainSentence = `強みは${highDomain}の領域、改善の手がかりは${lowDomain}の領域と読めます。`
  const lowestBullet = sectionComments[input.lowestSection.section].bullets[0] ?? ''
  const summaryBullets: string[] = [domainSentence, lowestBullet].filter(Boolean)
  const summary = { factSentence, bullets: summaryBullets }

  const nextActions = {
    summary: templates.nextActions.summary,
    bullets: templates.nextActions.bullets.slice(0, 2),
  }

  return {
    summary,
    strengths: { bullets: strengths },
    improvementHypotheses: { bullets: improvementHypotheses },
    nextActions,
    sectionComments,
    reflectionQuestions: [...REFLECTION_QUESTIONS_FIXED],
    sharedLeadershipReflectionQuestions: [...SHARED_LEADERSHIP_REFLECTION_QUESTIONS_FIXED],
    actionProposal: {
      summary: nextActions.summary,
      bullets: [...nextActions.bullets],
    },
  }
}
