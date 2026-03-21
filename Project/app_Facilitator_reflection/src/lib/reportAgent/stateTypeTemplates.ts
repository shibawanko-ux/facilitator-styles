/**
 * 状態タイプごとのテンプレ（改善仮説・次回アクション）
 * classifyWorkshopState の結果で分岐して使用する。
 */

import type { StateType } from './types'
import type { BulletsBlock, NextActionsBlock } from './types'
import { STATE_TYPE_IDS } from './classifyWorkshopState'

export interface StateTypeTemplateBlock {
  strengths: BulletsBlock
  improvementHypotheses: BulletsBlock
  nextActions: NextActionsBlock
}

const TEMPLATES: Record<string, StateTypeTemplateBlock> = {
  [STATE_TYPE_IDS.SAFETY_HIGH_CHALLENGE_LOW]: {
    strengths: {
      bullets: [
        '参加者観察・安心感が最も高く、安心感・問いかけが役割を超えて共有されていると読める。（場のホールド・問いかけ）',
        '目的・進め方の伝達が役割間で近く、認識されている可能性。（説明・設計）',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '流れの編集や即興的な軌道修正に余裕がなかった可能性。内省で次回の改善点を探れる。（流れ・即興）',
        'メインが参加者より低めなのは、自己評価が厳しいか、参加者には流れがよく見えていた可能性。（流れ・即興）',
      ],
    },
    nextActions: {
      summary: '流れの見え方の差を埋め、安心感を参加者と共有するための一歩を決める。',
      bullets: [
        '時間の区切りを入れるタイミングを1つ決め、終了後に参加者に「流れはどう感じたか」を一言聞く。',
        '次回、状況に合わせて進め方や問いを変えるタイミングを1つだけ意図して試す。',
      ],
    },
  },
  [STATE_TYPE_IDS.CHALLENGE_HIGH_CHAOS]: {
    strengths: {
      bullets: [
        '流れの編集や即興は高め。手が入っている可能性。（流れ・即興）',
        '挑戦的な進行が試されている。',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '流れの編集は試されている一方、全体の設計や安心感の届き方が相対的に低め。ずれがある可能性。',
        '挑戦的な進行と、参加者が「見えている」感覚のすり合わせが次のテーマ。',
      ],
    },
    nextActions: {
      summary: '設計の伝達と場の安心感を1つずつ確認する。',
      bullets: [
        '冒頭で目的と進め方を1文で書き、参加者に一言確認する。',
        '振り返りで「何が伝わったか・伝わらなかったか」を参加者に1つずつ聞く。',
      ],
    },
  },
  [STATE_TYPE_IDS.PRACTICE_HIGH_REPRODUCIBLE]: {
    strengths: {
      bullets: [
        '全体設計と流れの編集がともに高め。役割を超えて共有されていると読める。',
        '再現性の高いファシリテーションになっている可能性。',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '全体の設計と流れの編集が役割を超えて共有されていると読める。',
        '再現性の高いファシリテーションになっている可能性。強みを言語化して次回に引き継ぐとよい。',
      ],
    },
    nextActions: {
      summary: '強みを維持しつつ、参加者観察・安心感をさらに届ける一歩を決める。',
      bullets: [
        '今回「うまくいった」と感じたポイントを1つ書き出し、次回も意識する。',
        '参加者に「安心して話せた瞬間」を1つ挙げてもらい、メインは聴くだけの時間を取る。',
      ],
    },
  },
  [STATE_TYPE_IDS.EAGLE_LOW_BUG_HIGH]: {
    strengths: {
      bullets: [
        '場の観察・ホールド・問いかけが高く、対話や問いが届いている可能性。',
        '参加者の反応や空気を捉え、場に活かせていると読める。',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '目的や進め方の伝達に改善余地があり、届かず内省の時間を取る余地あり。（説明・設計）',
        '参加者観察や安心感は高め。一方、全体の設計の見え方にずれがある可能性。（場の観察・ホールド）',
      ],
    },
    nextActions: {
      summary: '全体の設計の伝わりを次回に改善するため、1つだけ試す。',
      bullets: [
        '冒頭で目的と進め方を1文で書き、参加者に一言確認する。',
        '流れの編集を1か所だけ意図して変えてみる。（流れ・即興）',
      ],
    },
  },
  [STATE_TYPE_IDS.VARIANCE_HIGH_SPLIT]: {
    strengths: {
      bullets: [
        '役割間で点差が大きい視点は、振り返りで対話すると改善の手がかりになる。',
        '6つの観点のうち高めの領域を強みとして次回に活かせる。',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '役割間で見え方の差が大きい視点がある。メイン・サブ・参加者で感じ方がずれている可能性。',
        '振り返りで「どこが届いたか・届かなかったか」を対話し、認識をすり合わせるとよい。',
      ],
    },
    nextActions: {
      summary: '役割間の認識差を埋めるため、一言確認を1つずつ入れる。',
      bullets: [
        '差が大きかった視点について、参加者に「どう感じたか」を一言聞く時間を取る。',
        'メインが「こう伝えたかった」と1つ述べ、参加者から「どう受け取ったか」を一言もらう。',
      ],
    },
  },
  [STATE_TYPE_IDS.STANDARD]: {
    strengths: {
      bullets: [
        '6つの観点のバランスから、強みと改善の入り口が読める。',
        '役割間の点差が小さい領域は、認識が共有されている可能性。',
      ],
    },
    improvementHypotheses: {
      bullets: [
        '6つの観点のバランスを確認し、相対的に低い観点に改善の入り口がある可能性。',
        '役割間の点差が大きい項目は、振り返りで「何が届いたか」を対話するとよい。',
      ],
    },
    nextActions: {
      summary: '強みと改善の入り口を踏まえ、次回1つだけ試すアクションを決める。',
      bullets: [
        '最低だった視点に紐づく行動を1つ選び、次回意図して試す。',
        '振り返りで「6つの観点のうち、今日特に話したい視点」を参加者に選んでもらう。',
      ],
    },
  },
}

/**
 * 状態タイプに応じた改善仮説・次回アクションのテンプレを返す。
 * 未定義の id の場合は標準型を使用する。
 */
export function getTemplatesForStateType(stateType: StateType): StateTypeTemplateBlock {
  return TEMPLATES[stateType.id] ?? TEMPLATES[STATE_TYPE_IDS.STANDARD]
}
