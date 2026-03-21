/**
 * 状態タイプ分類 classifyWorkshopState のユニットテスト
 * - 2ケース分の fixture で stateType が期待通りになることを検証
 * - テンプレ分岐（改善仮説・次回アクション）が stateType ごとに返ることを検証
 */

import { describe, it, expect } from 'vitest'
import { classifyWorkshopState, STATE_TYPE_IDS, STATE_TYPES } from '../classifyWorkshopState'
import { getTemplatesForStateType } from '../stateTypeTemplates'
import type { WorkshopAnalysisForClassification } from '../types'

/** ケース1: 安全性高・挑戦不足型（観察/ホールド/問い高・流れ低、役割差は小さい） */
const fixtureSafetyHighChallengeLow: WorkshopAnalysisForClassification = {
  averages: {
    bySection: {
      design: { mean: 4.0 },
      visibility: { mean: 4.0 },
      observation: { mean: 4.2 },
      hold: { mean: 4.2 },
      questioning: { mean: 4.2 },
      flow: { mean: 3.5 },
    },
  },
  highestSection: { section: 'hold', mean: 4.2 },
  lowestSection: { section: 'flow', mean: 3.5 },
  highVarianceSections: [],
  highRoleDiffSections: [],
}

/** ケース2: ばらつき大・分断型（役割差が大きい） */
const fixtureVarianceHighSplit: WorkshopAnalysisForClassification = {
  averages: {
    bySection: {
      design: { mean: 3.8 },
      visibility: { mean: 3.8 },
      observation: { mean: 3.9 },
      hold: { mean: 3.9 },
      questioning: { mean: 3.9 },
      flow: { mean: 3.7 },
    },
  },
  highestSection: { section: 'observation', mean: 3.9 },
  lowestSection: { section: 'flow', mean: 3.7 },
  highVarianceSections: [],
  highRoleDiffSections: [
    { section: 'observation', maxMinDiff: 0.6 },
    { section: 'flow', maxMinDiff: 0.5 },
  ],
}

describe('classifyWorkshopState', () => {
  it('ケース1: 虫高・魚低で役割差なし → 安全性高・挑戦不足型', () => {
    const result = classifyWorkshopState(fixtureSafetyHighChallengeLow)
    expect(result.id).toBe(STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW)
    expect(result.label).toBe('安全性高・挑戦不足型')
    expect(result).toEqual(STATE_TYPES[STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW])
  })

  it('ケース2: 役割差が大きい → ばらつき大・分断型', () => {
    const result = classifyWorkshopState(fixtureVarianceHighSplit)
    expect(result.id).toBe(STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT)
    expect(result.label).toBe('ばらつき大・分断型')
    expect(result).toEqual(STATE_TYPES[STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT])
  })

  it('分類結果でテンプレ分岐: 安全性高・挑戦不足型の改善仮説・次回アクションが返る', () => {
    const stateType = classifyWorkshopState(fixtureSafetyHighChallengeLow)
    const t = getTemplatesForStateType(stateType)
    expect(t.improvementHypotheses.bullets.length).toBeGreaterThanOrEqual(1)
    expect(t.nextActions.summary).toBeTruthy()
    expect(t.nextActions.bullets.length).toBeGreaterThanOrEqual(2)
    expect(t.improvementHypotheses.bullets.some((b) => b.includes('流れ・即興') || b.includes('流れ'))).toBe(true)
  })

  it('分類結果でテンプレ分岐: ばらつき大・分断型の改善仮説・次回アクションが返る', () => {
    const stateType = classifyWorkshopState(fixtureVarianceHighSplit)
    const t = getTemplatesForStateType(stateType)
    expect(t.improvementHypotheses.bullets.length).toBeGreaterThanOrEqual(1)
    expect(t.nextActions.bullets.length).toBeGreaterThanOrEqual(2)
    expect(t.improvementHypotheses.bullets.some((b) => b.includes('役割') || b.includes('ずれ'))).toBe(true)
  })
})
