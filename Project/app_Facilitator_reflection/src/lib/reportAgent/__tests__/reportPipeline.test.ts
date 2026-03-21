/**
 * レポートコメント生成パイプラインのテスト
 * - docs 09 §10 ケース1・2 の fixture で snapshot
 * - validate NG 時にテンプレへフォールバックすることを2ケースで確認
 */

import { describe, it, expect } from 'vitest'
import { renderTemplateComment } from '../renderTemplateComment'
import { generateReport } from '../generateReport'
import { validateReportComment } from '../validateReportComment'
import { inputFixtureCase1, inputFixtureCase2 } from './fixtures_reportPipeline'
import type { ReportAgentOutput } from '../types'

describe('renderTemplateComment', () => {
  it('ケース1（安全性高・挑戦不足型）で snapshot 一致', () => {
    const output = renderTemplateComment(inputFixtureCase1)
    expect(validateReportComment(output).ok).toBe(true)
    expect(output).toMatchSnapshot()
  })

  it('ケース2（鷹低・虫高）で snapshot 一致', () => {
    const output = renderTemplateComment(inputFixtureCase2)
    expect(validateReportComment(output).ok).toBe(true)
    expect(output).toMatchSnapshot()
  })

  it('同じ入力で2回実行すると同一 output になる（seed 固定の決定的選択）', () => {
    const out1 = renderTemplateComment(inputFixtureCase1)
    const out2 = renderTemplateComment(inputFixtureCase1)
    expect(out1).toEqual(out2)
  })

  it('roomId を変えると output が変わる', () => {
    const out1 = renderTemplateComment(inputFixtureCase1)
    const inputOtherRoom = { ...inputFixtureCase1, meta: { roomId: 'room-other' } }
    const out2 = renderTemplateComment(inputOtherRoom)
    expect(out1).not.toEqual(out2)
  })
})

describe('generateReport フォールバック', () => {
  it('polish 結果が validate NG のときテンプレにフォールバックする（観点名なし）', async () => {
    const invalidOutput: ReportAgentOutput = {
      summary: { factSentence: 'バランスの取れた評価でした。', bullets: ['内容と進行がうまくいっていました。'] },
      strengths: { bullets: ['進行がスムーズでした。'] },
      improvementHypotheses: { bullets: ['時間配分を少し見直すとよいかもしれません。'] },
      nextActions: { summary: '次回も改善を続けましょう。', bullets: ['進行を振り返る。', '参加者に一言聞く。'] },
      sectionComments: {
        design: { bullets: ['全体が伝わっていた。', '意図が共有されていた。'] },
        visibility: { bullets: ['情報が整理されていた。', '発言がまとまっていた。'] },
        observation: { bullets: ['雰囲気が良かった。', '反応を捉えていた。'] },
        hold: { bullets: ['安心できた。', '場が保たれていた。'] },
        questioning: { bullets: ['深まりを促していた。', '引き出せていた。'] },
        flow: { bullets: ['編集されていた。', '時間配分が取れていた。'] },
      },
      reflectionQuestions: [
        { question: 'Q1', intent: 'I1' },
        { question: 'Q2', intent: 'I2' },
        { question: 'Q3', intent: 'I3' },
      ],
      actionProposal: { summary: '改善を続ける。', bullets: ['振り返る。'] },
    }
    expect(validateReportComment(invalidOutput).ok).toBe(false)

    const result = await generateReport(inputFixtureCase1, {
      useAI: true,
      polishWithAIFn: async () => invalidOutput,
    })

    expect(validateReportComment(result).ok).toBe(true)
    expect(result.summary.factSentence).toContain('メイン')
    expect(result.summary.factSentence).toMatch(/説明・設計|見える化|場の観察|流れ/)
  })

  it('polish 結果が validate NG のときテンプレにフォールバックする（次回アクション1本のみ）', async () => {
    const templateOutput = renderTemplateComment(inputFixtureCase2)
    const invalidOutput: ReportAgentOutput = {
      ...templateOutput,
      nextActions: {
        summary: '次回も頑張りましょう。',
        bullets: ['良かったです。'],
      },
    }
    expect(validateReportComment(invalidOutput).ok).toBe(false)

    const result = await generateReport(inputFixtureCase2, {
      useAI: true,
      polishWithAIFn: async () => invalidOutput,
    })

    expect(validateReportComment(result).ok).toBe(true)
    expect(result.nextActions.bullets.length).toBeGreaterThanOrEqual(2)
  })
})
