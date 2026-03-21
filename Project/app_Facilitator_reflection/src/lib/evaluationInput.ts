/**
 * 評価入力（回答）の検証・送信データ組み立てロジック
 * - 全項目が 1〜5 で埋まっているか検証
 * - DB 送信用の scores オブジェクトを組み立て
 */

import { allItemIds } from '../data/evaluationItems'

export const SCORE_MIN = 1
export const SCORE_MAX = 5

export type ValidateScoresResult =
  | { ok: true; scoresForDb: Record<string, number> }
  | { ok: false; error: string }

/**
 * フォームの scores を検証し、送信用の scores オブジェクトを返す
 * - 全項目が SCORE_MIN〜SCORE_MAX のときのみ ok: true
 * - 未入力や範囲外があれば ok: false とエラーメッセージ
 */
export function validateAndBuildScores(
  scores: Record<string, number>,
  itemIds: string[] = allItemIds
): ValidateScoresResult {
  const scoresForDb: Record<string, number> = {}
  for (const id of itemIds) {
    const v = scores[id]
    if (typeof v !== 'number' || v < SCORE_MIN || v > SCORE_MAX) {
      return { ok: false, error: 'すべての項目で1〜5のいずれかを選んでください。' }
    }
    scoresForDb[id] = v
  }
  return { ok: true, scoresForDb }
}
