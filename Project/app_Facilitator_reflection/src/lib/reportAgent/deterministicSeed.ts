/**
 * seed 固定の決定的選択（同じ seed は常に同じ index / 同じ文）
 * seed = roomId + sectionKey + band + stateType 等で固定する。
 * 候補は配列（1文=1要素）。index = hash(seed) % candidates.length で選ぶ。
 */

/**
 * 文字列を数値ハッシュに変換する（決定的）
 */
export function hashStringToNumber(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h + s.charCodeAt(i)) | 0
  }
  return Math.abs(h)
}

/**
 * 配列から seed で決定的に index を選ぶ（0 ～ arr.length - 1）
 * index = hash(seed) % arr.length
 */
export function selectIndex<T>(arr: T[], seed: string): number {
  if (arr.length === 0) return 0
  return hashStringToNumber(seed) % arr.length
}

/**
 * 配列から seed で決定的に 1 件選ぶ。
 * 同じ seed → 同じ index → 同じ文。バリエーション追加時も index 計算は同じ式で後方互換。
 */
export function selectOne<T>(arr: T[], seed: string): T {
  if (arr.length === 0) throw new RangeError('selectOne: array is empty')
  return arr[hashStringToNumber(seed) % arr.length]
}

/**
 * 配列から seed で決定的に N 件を重複なしで選ぶ（N ≦ length のとき）。
 * N ＞ length のときは index を繰り返して埋める（同じ seed では同じ並び）。
 * 各 index は hash(seed + i) % length をベースに、衝突時は (idx+1)%length で distinct 化。
 */
export function selectN<T>(arr: T[], n: number, seed: string): T[] {
  if (arr.length === 0) return []
  const indices: number[] = []
  for (let i = 0; i < n; i++) {
    let idx = hashStringToNumber(seed + String(i)) % arr.length
    if (indices.length < arr.length) {
      while (indices.includes(idx)) idx = (idx + 1) % arr.length
    }
    indices.push(idx)
  }
  return indices.map((i) => arr[i])
}
