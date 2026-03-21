/**
 * 結果画面で使う「回答の集計・分析」ロジック
 * - 評価一覧から項目別平均を算出
 * - 役割別件数
 * - ルームのメインファシリタイプに応じた振り返り文言の取得
 */

import {
  allItemIds,
  SIX_AXIS_IDS,
  SIX_AXIS_ITEM_IDS,
  type SixAxisId,
} from '../data/evaluationItems'
import type { ReflectionContent } from '../data/reflectionByType'
import { reflectionByType } from '../data/reflectionByType'

const SCORE_MIN = 1
const SCORE_MAX = 5

/** スコアが有効な 1〜5 の数値か */
function isValidScore(v: unknown): v is number {
  return typeof v === 'number' && v >= SCORE_MIN && v <= SCORE_MAX
}

/** 評価行の scores のみ必要とする型 */
export interface EvaluationWithScores {
  scores?: Record<string, number> | null
}

/**
 * 複数件の評価から、各項目（E1〜F4）の平均を算出する
 * - 各評価の scores[id] が 1〜5 のときのみ加算
 * - 1件も有効でない項目は 0 を返す
 */
export function computeAverages(
  evaluations: EvaluationWithScores[],
  itemIds: string[] = allItemIds
): Record<string, number> {
  const averages: Record<string, number> = {}
  for (const id of itemIds) {
    let sum = 0
    let count = 0
    for (const row of evaluations) {
      const v = row.scores?.[id]
      if (isValidScore(v)) {
        sum += v
        count += 1
      }
    }
    averages[id] = count > 0 ? sum / count : 0
  }
  return averages
}

/** 役割別の送信件数 */
export interface RoleCounts {
  main: number
  sub: number
  participant: number
}

/**
 * 評価一覧から役割別の件数を集計する
 */
export function getRoleCounts(evaluations: { role: string }[]): RoleCounts {
  let main = 0
  let sub = 0
  let participant = 0
  for (const row of evaluations) {
    if (row.role === 'main') main += 1
    else if (row.role === 'sub') sub += 1
    else if (row.role === 'participant') participant += 1
  }
  return { main, sub, participant }
}

/**
 * ルームのメインファシリタイプ ID に対応する振り返りの問い・アクション提案を返す
 * typeId が空や未登録の場合は null
 */
export function getReflectionContent(typeId: string | null): ReflectionContent | null {
  if (!typeId || !typeId.trim()) return null
  const content = reflectionByType[typeId]
  return content ?? null
}

/** 役割別の項目別平均（メイン vs その他） */
export interface AveragesByRole {
  main: Record<string, number>
  others: Record<string, number>
}

/** 役割付き評価行 */
export interface EvaluationWithScoresAndRole extends EvaluationWithScores {
  role: string
}

/**
 * 指定した項目 ID について、メインの自己評価と「参加者・サブ」の平均をそれぞれ算出する
 * レーダーチャートでメイン vs 他役割の差分表示に利用
 */
export function computeAveragesByRole(
  evaluations: EvaluationWithScoresAndRole[],
  itemIds: string[]
): AveragesByRole {
  const main: Record<string, number> = {}
  const others: Record<string, number> = {}
  const mainRows = evaluations.filter((r) => r.role === 'main')
  const otherRows = evaluations.filter((r) => r.role !== 'main')

  for (const id of itemIds) {
    let sumMain = 0
    let countMain = 0
    for (const row of mainRows) {
      const v = row.scores?.[id]
      if (isValidScore(v)) {
        sumMain += v
        countMain += 1
      }
    }
    main[id] = countMain > 0 ? sumMain / countMain : 0

    let sumOthers = 0
    let countOthers = 0
    for (const row of otherRows) {
      const v = row.scores?.[id]
      if (isValidScore(v)) {
        sumOthers += v
        countOthers += 1
      }
    }
    others[id] = countOthers > 0 ? sumOthers / countOthers : 0
  }
  return { main, others }
}

/** 役割別・6軸の総合点（六角形レーダー用・03 §4） */
export type SixAxisAveragesByRole = {
  main: Record<SixAxisId, number>
  sub: Record<SixAxisId, number>
  participant: Record<SixAxisId, number>
}

/**
 * 役割別・6軸の総合点を算出する（各軸に属する項目の平均・03 §4）
 * 結果画面の六角形レーダーと reportAgent 入力に使用
 */
export function computeSixAxisAveragesByRole(
  evaluations: EvaluationWithScoresAndRole[]
): SixAxisAveragesByRole {
  const byRole = {
    main: evaluations.filter((r) => r.role === 'main'),
    sub: evaluations.filter((r) => r.role === 'sub'),
    participant: evaluations.filter((r) => r.role === 'participant'),
  }

  function axisAverage(rows: EvaluationWithScoresAndRole[], itemIds: string[]): number {
    let sum = 0
    let count = 0
    for (const row of rows) {
      for (const id of itemIds) {
        const v = row.scores?.[id]
        if (isValidScore(v)) {
          sum += v
          count += 1
        }
      }
    }
    return count > 0 ? sum / count : 0
  }

  return {
    main: Object.fromEntries(
      SIX_AXIS_IDS.map((axisId) => [
        axisId,
        axisAverage(byRole.main, SIX_AXIS_ITEM_IDS[axisId]),
      ])
    ) as Record<SixAxisId, number>,
    sub: Object.fromEntries(
      SIX_AXIS_IDS.map((axisId) => [
        axisId,
        axisAverage(byRole.sub, SIX_AXIS_ITEM_IDS[axisId]),
      ])
    ) as Record<SixAxisId, number>,
    participant: Object.fromEntries(
      SIX_AXIS_IDS.map((axisId) => [
        axisId,
        axisAverage(byRole.participant, SIX_AXIS_ITEM_IDS[axisId]),
      ])
    ) as Record<SixAxisId, number>,
  }
}
