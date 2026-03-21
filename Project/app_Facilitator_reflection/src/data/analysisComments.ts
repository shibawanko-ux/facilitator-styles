/**
 * 分析結果文章（鷹・虫・魚ごと・項目別）
 * 差分から見る分析結果文章（02 3.5）。項目ID（E1–E4 等）は使わない。
 * パターン: メインが他より高い / メインが他より低い / 役割間で近い / その他
 */

const DIFF_THRESHOLD = 0.5

/** 点差に基づく出し分けパターン */
export type AnalysisPattern = 'mainHigher' | 'mainLower' | 'close' | 'default'

export interface RoleCounts {
  main: number
  sub: number
  participant: number
}

/** 1つの目のメイン・サブ・参加者スコア */
export interface SectionScoresForPattern {
  main: number
  sub: number
  participant: number
}

/**
 * メイン・サブ・参加者の点差からパターンを判定する（差分から見る出し分け用）
 */
export function getAnalysisPattern(
  scores: SectionScoresForPattern,
  roleCounts: RoleCounts
): AnalysisPattern {
  const hasSub = roleCounts.sub > 0
  const hasParticipant = roleCounts.participant > 0
  if (!hasSub && !hasParticipant) return 'default'

  const others = [
    ...(hasSub ? [scores.sub] : []),
    ...(hasParticipant ? [scores.participant] : []),
  ]
  const maxOther = Math.max(...others)
  const minOther = Math.min(...others)
  const all = [scores.main, ...others]
  const range = Math.max(...all) - Math.min(...all)

  if (range < DIFF_THRESHOLD) return 'close'
  if (scores.main >= maxOther + DIFF_THRESHOLD) return 'mainHigher'
  if (scores.main <= minOther - DIFF_THRESHOLD) return 'mainLower'
  return 'default'
}

/** 差が「ほぼ同じ」とみなすしきい値（事実の1文で使用） */
const CLOSE_THRESHOLD = 0.3

/**
 * その目のスコアと役割の有無から「事実の1文」を組み立てる（総評の先頭表示用）
 * 例: 「メイン 4.2点、参加者 3.5点で、メインが約0.7点高めです。」
 */
export function getAnalysisFactSentence(
  scores: SectionScoresForPattern,
  roleCounts: RoleCounts
): string {
  const m = scores.main
  const mainStr = `メイン ${m.toFixed(1)}点`
  const hasSub = roleCounts.sub > 0
  const hasParticipant = roleCounts.participant > 0

  if (!hasSub && !hasParticipant) {
    return `${mainStr}です。`
  }

  const parts: string[] = [mainStr]
  if (hasSub) parts.push(`サブ ${scores.sub.toFixed(1)}点`)
  if (hasParticipant) parts.push(`参加者 ${scores.participant.toFixed(1)}点`)
  const others = [
    ...(hasSub ? [scores.sub] : []),
    ...(hasParticipant ? [scores.participant] : []),
  ]
  const maxOther = Math.max(...others)
  const minOther = Math.min(...others)
  const range = Math.max(m, ...others) - Math.min(m, ...others)

  if (range < CLOSE_THRESHOLD) {
    return `${parts.join('、')}で、ほぼ同じです。`
  }
  if (m >= maxOther + CLOSE_THRESHOLD) {
    const diff = (m - maxOther)
    const diffStr = diff < 1 ? '約0.5点' : `約${Math.round(diff * 10) / 10}点`
    return `${parts.join('、')}で、メインが${diffStr}高めです。`
  }
  if (m <= minOther - CLOSE_THRESHOLD) {
    const diff = minOther - m
    const diffStr = diff < 1 ? '約0.5点' : `約${Math.round(diff * 10) / 10}点`
    return `${parts.join('、')}で、メインが${diffStr}低めです。`
  }
  return `${parts.join('、')}で、差は小さいです。`
}

/** 鷹の目：総評はパターン別、その他は差分から見る1本（項目IDなし） */
export interface EagleComments {
  summaryByPattern: Record<AnalysisPattern, string>
  overallDesign: string
  explanation: string
  visualization: string
}

/** 虫の目 */
export interface BugComments {
  summaryByPattern: Record<AnalysisPattern, string>
  participantObservation: string
  safety: string
  infoEditing: string
  questioning: string
  reframing: string
  holding: string
}

/** 魚の目 */
export interface FishComments {
  summaryByPattern: Record<AnalysisPattern, string>
  flowAccuracy: string
  flexibleEditing: string
  improvisation: string
  balanceAndFlow: string
}

const defaultSummary =
  'メイン・サブ・参加者の点差から、全体の設計・説明の伝わり・見える化についての捉え方の違いが読み取れます。点差が小さいほど、役割を超えて認識が近い状態と考えられます。'

export const analysisCommentsEagle: EagleComments = {
  summaryByPattern: {
    mainHigher:
      'メインの自己評価がサブ・参加者より高めに出ています。全体設計や説明の伝わりを、メインは十分届いていると感じている一方、他役割にはもう一歩届いていなかった可能性があります。サブや参加者に「どこが伝わったか・伝わらなかったか」を聞くと、見え方の差がはっきりします。',
    mainLower:
      'メインの自己評価がサブ・参加者より低めに出ています。全体の設計や説明の伝わりを、メインは厳しめに見ている可能性があります。他役割の方が高くつけている場合は、参加者には届いていたと受け止められている読みもでき、対話で「何が届いていたか」を共有するとよいです。',
    close:
      'メイン・サブ・参加者の点が近く、全体の設計・説明の伝わり・見える化について、役割を超えて認識が揃っている状態です。目的や進め方の共有ができていると解釈できます。',
    default: defaultSummary,
  },
  overallDesign:
    '点差が大きいときは、目的・ゴール・進め方の設計が役割によってどう見えているかが異なっている可能性があります。点が近いときは、設計が役割を超えて共有されていると読めます。',
  explanation:
    '説明の届き方について、メインと他役割で感じ方が違うと点差になります。メインが低めのときは自己評価が厳しいか、他役割が高めのときは参加者には伝わっていたと受け止められている可能性があります。',
  visualization:
    '発言や成果の整理・見える化が、誰の目にどう映っているかが点差に表れます。役割間で点が揃うと、見える化が共有されていると解釈できます。',
}

export const analysisCommentsBug: BugComments = {
  summaryByPattern: {
    mainHigher:
      'メインの自己評価がサブ・参加者より高めです。参加者への観察・安心感・問いかけを、メインはよくできていると感じている一方、場の状態の捉え方や問いの届き方について、他役割とは温度差がある可能性があります。参加者やサブに「場の感じ方」を聞くと差が見えやすくなります。',
    mainLower:
      'メインの自己評価がサブ・参加者より低めです。参加者へのアプローチをメインは厳しめに見ている可能性があります。他役割が高くつけている場合は、参加者には安心感や問いかけが届いていたと受け止められている読みもでき、対話で確認するとよいです。',
    close:
      'メイン・サブ・参加者の点が近く、参加者への観察・安心感・問いかけについて、役割を超えて認識が揃っています。場の状態の共有ができていると解釈できます。',
    default:
      'メイン・サブ・参加者の点差から、場の観察・安心感・問いかけの捉え方の違いが読み取れます。点差が小さいほど、役割を超えて認識が近い状態と考えられます。',
  },
  participantObservation:
    '参加者の反応や空気の捉え方が、役割ごとにどう違うかが点差に現れます。メインが低めのときは、他役割の方が場をよく見えていると感じている可能性があります。',
  safety:
    '安心して話せる・挑戦できる場が保たれていたかについて、メインと他役割で感じ方が近いと点差は小さく、違うと点差が開きます。点が揃うと、安心感が役割を超えて共有されていると読めます。',
  infoEditing:
    '参加者発言の拾い方・まとめ方について、誰がどう編集していると感じているかが点差に表れます。役割間で点が近いと、情報の編集が共有されていると解釈できます。',
  questioning:
    '問いかけの届き方について、メインと他役割で認識が違うと点差になります。参加者やサブに「どの問いが効いたか」を聞くと、差の理由が見えやすくなります。',
  reframing:
    '発言を違う角度で返し、気づきや深まりを促せていたかについて、役割ごとの見え方が点差に表れます。メインが低めのときは、他役割の方が変化を感じている可能性があります。',
  holding:
    '誰が場をホールドしていると感じているかが点差に表れます。メインが低めで他が高めのときは、サブや参加者の支えが評価されている可能性があります。点が揃うと、場のホールドが役割を超えて共有されていると読めます。',
}

export const analysisCommentsFish: FishComments = {
  summaryByPattern: {
    mainHigher:
      'メインの自己評価がサブ・参加者より高めです。WSの流れや柔軟な編集を、メインはうまくいっていると感じている一方、他役割には流れの感じ方に差がある可能性があります。時間配分や軌道修正のタイミングについて、対話で確認するとよいです。',
    mainLower:
      'メインの自己評価がサブ・参加者より低めです。流れの的確さや柔軟な編集を、メインは厳しめに見ている可能性があります。他役割が高くつけている場合は、参加者には流れがよく編集されていたと受け止められている読みもでき、対話で共有するとよいです。',
    close:
      'メイン・サブ・参加者の点が近く、WSの流れ・柔軟な編集・時間と内容のバランスについて、役割を超えて認識が揃っています。流れの編集が共有されていると解釈できます。',
    default:
      'メイン・サブ・参加者の点差から、流れの的確さや柔軟な編集の捉え方の違いが読み取れます。点差が小さいほど、流れについて役割を超えて認識が近い状態と考えられます。',
  },
  flowAccuracy:
    '流れの的確さについて、メインと他役割で感じ方が違うと点差になります。点が近いときは、目的に向かう道筋が役割を超えて共有されていると読めます。',
  flexibleEditing:
    '状況に合わせた進め方や問いの変更について、誰がどう柔軟だったと感じているかが点差に表れます。役割間で点が揃うと、柔軟な編集が共有されていると解釈できます。',
  improvisation:
    'その場での出し入れや微修正について、メインと他役割の見え方が点差に表れます。メインが低めのときは、他役割の方が即興的な調整を感じている可能性があります。',
  balanceAndFlow:
    '時間と内容のバランス・流れの編集について、役割ごとの体験の違いが点差に現れます。点が近いときは、発散・収束・決定のプロセスが役割を超えて共有されていると読めます。',
}
