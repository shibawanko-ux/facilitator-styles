/**
 * 状態タイプ分類（テンプレ分岐に使用）
 * - 安全性高・挑戦不足型 / 挑戦高・混乱型 / 実践高・再現性あり型 / ばらつき大・分断型
 */

import type { StateType, WorkshopAnalysisForClassification } from './types'

/** 状態タイプ ID（テンプレ分岐のキー） */
export const STATE_TYPE_IDS = {
  SAFETY_HIGH_CHALLENGE_LOW: 'safety_high_challenge_low',
  EAGLE_LOW_BUG_HIGH: 'eagle_low_bug_high',
  CHALLENGE_HIGH_CHAOS: 'challenge_high_chaos',
  PRACTICE_HIGH_REPRODUCIBLE: 'practice_high_reproducible',
  VARIANCE_HIGH_SPLIT: 'variance_high_split',
  STANDARD: 'standard',
} as const

/** 状態タイプの定義（id → label） */
export const STATE_TYPES: Record<string, StateType> = {
  [STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW]: {
    id: STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW,
    label: '安全性高・挑戦不足型',
  },
  [STATE_TYPE_IDS.CHALLENGE_HIGH_CHAOS]: {
    id: STATE_TYPE_IDS.CHALLENGE_HIGH_CHAOS,
    label: '挑戦高・混乱型',
  },
  [STATE_TYPE_IDS.PRACTICE_HIGH_REPRODUCIBLE]: {
    id: STATE_TYPE_IDS.PRACTICE_HIGH_REPRODUCIBLE,
    label: '実践高・再現性あり型',
  },
  [STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT]: {
    id: STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT,
    label: 'ばらつき大・分断型',
  },
  [STATE_TYPE_IDS.EAGLE_LOW_BUG_HIGH]: {
    id: STATE_TYPE_IDS.EAGLE_LOW_BUG_HIGH,
    label: '鷹低・虫高型',
  },
  [STATE_TYPE_IDS.STANDARD]: {
    id: STATE_TYPE_IDS.STANDARD,
    label: '標準型',
  },
}

const ROLE_DIFF_THRESHOLD = 0.5
const SECTION_GAP_THRESHOLD = 0.5
const HIGH_MEAN = 3.8
const LOW_MEAN = 3.5

/** 6軸から合成スコア（従来の鷹・虫・魚に相当）を算出。状態タイプ判定に使用。 */
function compositeMeans(bySection: Record<string, { mean: number } | undefined>): {
  eagle: number
  bug: number
  fish: number
} {
  const d = bySection.design?.mean ?? 0
  const v = bySection.visibility?.mean ?? 0
  const o = bySection.observation?.mean ?? 0
  const h = bySection.hold?.mean ?? 0
  const q = bySection.questioning?.mean ?? 0
  const f = bySection.flow?.mean ?? 0
  return {
    eagle: (d + v) / 2,
    bug: (o + h + q) / 3,
    fish: f,
  }
}

/**
 * 分析結果から状態タイプを1つに分類する。
 * テンプレの「改善仮説」「次回アクション」の分岐に使う。
 * 6軸の bySection から合成スコア（鷹・虫・魚相当）を算出して判定。
 */
export function classifyWorkshopState(
  analysis: WorkshopAnalysisForClassification
): StateType {
  const { averages, highRoleDiffSections, highVarianceSections } = analysis
  const { eagle, bug, fish } = compositeMeans(averages.bySection)

  // 1) 役割差が大きい、またはばらつきが大きい視点が複数 → ばらつき大・分断型
  const hasLargeRoleDiff =
    highRoleDiffSections.some((s) => s.maxMinDiff >= ROLE_DIFF_THRESHOLD) ||
    highRoleDiffSections.length >= 2
  const hasLargeVariance = highVarianceSections.length >= 2
  if (hasLargeRoleDiff || hasLargeVariance) {
    return STATE_TYPES[STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT]
  }

  // 2) 虫高・魚低（安心感は高いが流れ・柔軟性に余裕なし）→ 安全性高・挑戦不足型
  if (bug >= HIGH_MEAN && fish < HIGH_MEAN && bug - fish >= SECTION_GAP_THRESHOLD) {
    return STATE_TYPES[STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW]
  }

  // 3) 鷹低・虫高（全体設計・伝達は弱め、参加者観察は強め）
  if (eagle < HIGH_MEAN && bug >= HIGH_MEAN) {
    return STATE_TYPES[STATE_TYPE_IDS.EAGLE_LOW_BUG_HIGH]
  }

  // 4) 魚高かつ鷹 or 虫が低い（流れは試したが設計・安心感が届いていない）→ 挑戦高・混乱型
  if (fish >= HIGH_MEAN && (eagle < LOW_MEAN || bug < LOW_MEAN)) {
    return STATE_TYPES[STATE_TYPE_IDS.CHALLENGE_HIGH_CHAOS]
  }

  // 5) 鷹・魚ともに高め（設計と流れが両方届いている）→ 実践高・再現性あり型
  if (eagle >= HIGH_MEAN && fish >= HIGH_MEAN) {
    return STATE_TYPES[STATE_TYPE_IDS.PRACTICE_HIGH_REPRODUCIBLE]
  }

  return STATE_TYPES[STATE_TYPE_IDS.STANDARD]
}
