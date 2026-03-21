/**
 * 品質ゲート validateReportComment のユニットテスト
 * - 合格ケース 2 件
 * - 不合格ケース 2 件
 */

import { describe, it, expect } from 'vitest'
import { validateReportComment } from '../validateReportComment'
import type { ReportAgentOutput } from '../types'

/** 6軸の sectionComments で各軸2 bullets のブロック */
const twoBullets = (a: string, b: string) => ({ bullets: [a, b] })

/** 合格用：09 仕様に沿った健全なレポート（6軸観点名・相対差・4ブロック・200字以内） */
const validOutput1: ReportAgentOutput = {
  summary: {
    factSentence: 'メイン4.2点、参加者3.8点で、メインが約0.4点高めです。',
    bullets: [
      '説明・設計は役割間で近く、全体の設計・説明の伝わりが共有されていると読める。',
      '場の観察でメインが参加者より高め。場の安心感や問いかけをメインは十分と感じている一方、参加者にはもう一歩届いていた可能性がある。',
    ],
  },
  strengths: {
    bullets: [
      '説明・設計の点が役割間で近い。目的・進め方の伝達が役割を超えて認識されている可能性。',
      '場のホールド・安心感がメインで高め。参加者観察や問いの設計に手が入っていると推測される。',
    ],
  },
  improvementHypotheses: {
    bullets: [
      '流れ・即興が他観点より低め。流れの編集や時間配分に、関係性の見え方の差がある可能性。',
    ],
  },
  nextActions: {
    summary: '流れの見え方の差を埋め、安心感を参加者と共有するための一歩を決める。',
    bullets: [
      '次回、時間の区切りを入れるタイミングを1つ決め、終了後に参加者に「流れはどう感じたか」を一言聞く。',
      '振り返りで「安心して話せた瞬間」を参加者に1つ挙げてもらい、メインは聴くだけの時間を取る。',
    ],
  },
  sectionComments: {
    design: twoBullets('総合点はメイン4.0・参加者3.8で近い。', '全体の説明・設計の伝わりが役割を超えて共有されていると解釈できる。'),
    visibility: twoBullets('見える化・編集は役割間で近い。', '発言や成果の整理が共有されていると読める。'),
    observation: twoBullets('総合点はメイン4.2・参加者3.6でメインが高め。', '場の観察をメインは十分と感じている一方、参加者には届き方に差がある可能性。'),
    hold: twoBullets('場のホールド・安心感はメインが高め。', '安心して話せる場が保たれていたと受け止められている可能性。'),
    questioning: twoBullets('問いかけ・リフレーミングは標準帯。', '問いの種類に応じて届き方に差がある可能性。'),
    flow: twoBullets('総合点はメイン3.5・参加者3.8でメインが低め。', '流れの編集や柔軟な軌道修正を、メインは厳しめに見ている可能性。'),
  },
  reflectionQuestions: [
    { question: '今回の場で、メインとして「うまくいった」と感じた瞬間はどこでしたか？', intent: '自己認識と他者からの見え方のすり合わせ。' },
    { question: '6つの観点のうち、今日の振り返りで特に話したい視点はどれですか？', intent: '優先して深掘りするテーマを選ぶ。' },
    { question: '次のファシリテーションで、メインが「1つだけ試してみる」としたら、何を試すと良さそうですか？', intent: '実行可能な一歩に落とす。' },
  ],
  actionProposal: {
    summary: '流れの見え方の差と、安心感の届き方を次回に活かすため、時間の区切りと一言確認を1つずつ試す。',
    bullets: [
      '時間の区切りを入れるタイミングを1つ決め、終了後に参加者に「流れはどう感じたか」を一言聞く。',
      '「安心して話せた瞬間」を参加者に1つ挙げてもらい、聴くだけの時間を取る。',
    ],
  },
}

/** 合格用：別パターン（説明・設計低・場の観察等高。6軸・数値・具体語・2 bullets 各軸・重複なし） */
const validOutput2: ReportAgentOutput = {
  summary: {
    factSentence: '説明・設計は3.5点で低め、場の観察は4.0点で高め、流れ・即興は標準帯です。',
    bullets: ['説明・設計に改善余地があり、場の観察は役割を超えて共有されていると読める。'],
  },
  strengths: {
    bullets: ['場のホールド・安心感が高く、対話や問いが届いている可能性。'],
  },
  improvementHypotheses: {
    bullets: ['説明・設計が低め。目的・進め方の伝達が届かず、内省の時間を取る余地あり。'],
  },
  nextActions: {
    summary: '全体の設計の伝わりを次回に改善するため、1つだけ試す。',
    bullets: [
      '冒頭で目的と進め方を1文で書き、参加者に一言確認する。',
      '流れ・即興の編集を1か所だけ意図して変えてみる。',
    ],
  },
  sectionComments: {
    design: twoBullets('説明・設計は標準より低め。設計の見え方にずれがある可能性。', '目的・進め方の伝達に改善の入り口があると読める。'),
    visibility: twoBullets('見える化・編集は標準帯。', '発言や成果の整理の届き方に差がある可能性。'),
    observation: twoBullets('場の観察は高め。安心感や問いかけが共有されていると読める。', '参加者観察に手が入っている可能性。'),
    hold: twoBullets('場のホールド・安心感は高め。', '安心して話せる場が保たれていたと読める。'),
    questioning: twoBullets('問いかけ・リフレーミングは標準帯。', '問いの種類に応じて届き方が異なる可能性。'),
    flow: twoBullets('流れ・即興は標準帯。流れの感じ方に役割間で差がある可能性。', '時間配分や柔軟な編集のどれに手を入れるか示唆が得られる。'),
  },
  reflectionQuestions: [
    { question: 'うまくいった瞬間はどこでしたか？', intent: '自己認識と他者見え方のすり合わせ。' },
    { question: '特に話したい視点はどれですか？', intent: '優先して深掘りするテーマを選ぶ。' },
    { question: '1つだけ試すとしたら何を試しますか？', intent: '実行可能な一歩に落とす。' },
  ],
  actionProposal: {
    summary: '設計の伝達を1つ試す。',
    bullets: ['目的を1文で書き、一言確認する。'],
  },
}

/** 不合格用：6軸観点名が一度も含まれない */
const invalidOutputNoSectionName: ReportAgentOutput = {
  ...validOutput1,
  summary: {
    factSentence: '全体としてバランスの取れた評価でした。',
    bullets: ['設計と進行がうまくいっていたと推測されます。'],
  },
  strengths: { bullets: ['進行がスムーズだった可能性があります。'] },
  improvementHypotheses: { bullets: ['時間配分を少し見直すとよいかもしれません。'] },
  nextActions: {
    summary: '次回も改善を続けましょう。',
    bullets: ['進行を振り返る時間を取る。', '参加者に一言聞く時間を設ける。'],
  },
  sectionComments: {
    design: twoBullets('全体が伝わっていたと解釈できる。', '意図が共有されていた。'),
    visibility: twoBullets('情報が整理されていた。', '発言がまとまっていた。'),
    observation: twoBullets('雰囲気が良かったと読める。', '反応を捉えていた。'),
    hold: twoBullets('安心できた。', '場が保たれていた。'),
    questioning: twoBullets('深まりを促していた。', '引き出せていた。'),
    flow: twoBullets('編集がされていた可能性。', '時間配分が取れていた。'),
  },
}

/** 不合格用：次回アクションが1点のみ＋抽象語のみのブロック */
const invalidOutputFewBulletsAndAbstract: ReportAgentOutput = {
  ...validOutput1,
  nextActions: {
    summary: '次回も頑張りましょう。',
    bullets: ['良かったです。'], // 1点のみ → 2点以上必要
  },
  strengths: {
    bullets: ['良かったです。', '学びがあった。'], // 抽象語のみ
  },
  improvementHypotheses: {
    bullets: ['よかったです。'],
  },
}

/** 不合格用（新ルール）：sectionComments の design が bullets 1つだけ → ちょうど2つ必要 */
const invalidOutputSectionCommentsNotTwo: ReportAgentOutput = {
  ...validOutput1,
  sectionComments: {
    ...validOutput1.sectionComments,
    design: { bullets: ['説明・設計は役割間で近い。'] }, // 1つだけ
  },
}

/** 不合格用（新ルール）：summary.bullets と strengths.bullets に同一文を入れる → 重複抑制でNG */
const invalidOutputDuplicateSummaryStrengths: ReportAgentOutput = {
  ...validOutput1,
  summary: {
    ...validOutput1.summary!,
    bullets: ['説明・設計は役割間で近く、全体の設計・説明の伝わりが共有されていると読める。'],
  },
  strengths: {
    bullets: [
      '説明・設計は役割間で近く、全体の設計・説明の伝わりが共有されていると読める。', // summary と同一
      '場のホールド・安心感がメインで高め。参加者観察や問いの設計に手が入っていると推測される。',
    ],
  },
}

describe('validateReportComment', () => {
  it('合格ケース1: 09仕様に沿った健全なレポートは ok: true', () => {
    const result = validateReportComment(validOutput1)
    expect(result.ok).toBe(true)
    expect(result.errors).toHaveLength(0)
  })

  it('合格ケース2: 鷹低・虫高パターンでも観点名・相対差ありで ok: true', () => {
    const result = validateReportComment(validOutput2)
    expect(result.ok).toBe(true)
    expect(result.errors).toHaveLength(0)
  })

  it('不合格ケース1: 観点名（鷹/虫/魚）が含まれない場合は ok: false', () => {
    const result = validateReportComment(invalidOutputNoSectionName)
    expect(result.ok).toBe(false)
    expect(result.errors.some((e) => e.includes('観点名'))).toBe(true)
  })

  it('不合格ケース2: 次回アクション2点未満 or 抽象語のみで ok: false', () => {
    const result = validateReportComment(invalidOutputFewBulletsAndAbstract)
    expect(result.ok).toBe(false)
    expect(result.errors.length).toBeGreaterThan(0)
    const hasNextActionsError = result.errors.some((e) => e.includes('次回アクション') || e.includes('2点'))
    const hasAbstractError = result.errors.some((e) => e.includes('抽象語'))
    expect(hasNextActionsError || hasAbstractError).toBe(true)
  })

  it('不合格ケース3（新ルール）: sectionComments の bullets がちょうど2つでない場合は ok: false', () => {
    const result = validateReportComment(invalidOutputSectionCommentsNotTwo)
    expect(result.ok).toBe(false)
    expect(result.errors.some((e) => e.includes('sectionComments.design') && e.includes('ちょうど2つ'))).toBe(true)
  })

  it('不合格ケース4（新ルール）: summary.bullets と strengths.bullets に同一文がある場合は ok: false', () => {
    const result = validateReportComment(invalidOutputDuplicateSummaryStrengths)
    expect(result.ok).toBe(false)
    expect(result.errors.some((e) => e.includes('同一文') && e.includes('重複'))).toBe(true)
  })
})
