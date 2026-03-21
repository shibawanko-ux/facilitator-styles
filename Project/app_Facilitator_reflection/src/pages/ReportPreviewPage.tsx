/**
 * レポートプレビュー（確認専用）
 * 構造: 状態タイプ・最高/最低視点 → 総評 → 6軸 sectionComments → 強み/改善仮説/次回アクション → 振り返りの問い・アクション提案
 */

import { useMemo, useState } from 'react'
import {
  generateReportSync,
  validateReportComment,
  classifyWorkshopState,
} from '../lib/reportAgent'
import type { ReportAgentInput, ReportAgentOutput, SectionKey } from '../lib/reportAgent'
import { SECTION_KEYS } from '../lib/reportAgent/types'
import { inputFixtureCase1, inputFixtureCase2 } from '../data/reportPreviewFixtures'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

const SECTION_LABEL_JA: Record<SectionKey, string> = {
  design: '説明・設計',
  visibility: '見える化・編集',
  observation: '場の観察',
  hold: '場のホールド・安心感',
  questioning: '問いかけ・リフレーミング',
  flow: '流れ・即興',
}

const FIXTURES: { id: string; label: string; input: ReportAgentInput }[] = [
  { id: 'case1', label: 'ケース1（安全性高・挑戦不足型）', input: inputFixtureCase1 },
  { id: 'case2', label: 'ケース2（説明・設計低・場の観察等高）', input: inputFixtureCase2 },
]

function Bullets({ bullets }: { bullets: string[] }) {
  return (
    <ul className="list-disc pl-5 space-y-1">
      {bullets.map((b, i) => (
        <li key={i}>{b}</li>
      ))}
    </ul>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section className="mb-6">
      <h2 className="text-lg font-semibold border-b border-slate-200 pb-1 mb-2">
        {title}
      </h2>
      {children}
    </section>
  )
}

export function ReportPreviewPage() {
  const [fixtureId, setFixtureId] = useState('case1')

  const fixture = useMemo(
    () => FIXTURES.find((f) => f.id === fixtureId) ?? FIXTURES[0],
    [fixtureId]
  )

  const { output, validation, stateType, highestSection, lowestSection } =
    useMemo(() => {
      const out: ReportAgentOutput = generateReportSync(fixture.input)
      const val = validateReportComment(out)
      const state = classifyWorkshopState(fixture.input)
      return {
        output: out,
        validation: val,
        stateType: state,
        highestSection: fixture.input.highestSection,
        lowestSection: fixture.input.lowestSection,
      }
    }, [fixture.input])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="p-4 border-b">
        <AppBrandHeading />
        <h1 className="text-xl font-bold">レポートプレビュー（fixture）</h1>
        <div className="mt-2 flex flex-wrap items-center gap-4">
          <span>
            <label className="mr-2 text-sm text-slate-600">fixture:</label>
            <select
              value={fixtureId}
              onChange={(e) => setFixtureId(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
            >
              {FIXTURES.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.label}
                </option>
              ))}
            </select>
          </span>
          <span className="text-sm text-slate-700">
            状態タイプ: <strong>{stateType.label}</strong>
          </span>
          <span className="text-sm text-slate-700">
            最高視点: {SECTION_LABEL_JA[highestSection.section]}（{highestSection.mean}）
          </span>
          <span className="text-sm text-slate-700">
            最低視点: {SECTION_LABEL_JA[lowestSection.section]}（{lowestSection.mean}）
          </span>
        </div>
        <div className="mt-2">
          <span
            className={
              validation.ok ? 'text-green-700 text-sm' : 'text-red-700 text-sm'
            }
          >
            検証: {validation.ok ? 'OK' : 'NG'}
          </span>
          {validation.errors.length > 0 && (
            <ul className="list-disc pl-5 mt-1 text-sm text-red-700">
              {validation.errors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      </header>

      <main className="p-4 flex-1 max-w-6xl mx-auto w-full">
        <Section title="総評">
          <p className="mb-2">{output.summary.factSentence}</p>
          <Bullets bullets={output.summary.bullets} />
        </Section>

        <div className="space-y-4 mb-6">
          {SECTION_KEYS.map((key) => (
            <Section key={key} title={SECTION_LABEL_JA[key]}>
              <Bullets bullets={output.sectionComments[key].bullets} />
            </Section>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <Section title="強み">
            <Bullets bullets={output.strengths.bullets} />
          </Section>
          <Section title="改善仮説">
            <Bullets bullets={output.improvementHypotheses.bullets} />
          </Section>
          <Section title="次回アクション">
            <p className="mb-2">{output.nextActions.summary}</p>
            <Bullets bullets={output.nextActions.bullets} />
          </Section>
        </div>

        <Section title="振り返りの問い">
          <ul className="space-y-3">
            {output.reflectionQuestions.map((q, i) => (
              <li key={i} className="border-l-2 border-slate-200 pl-3">
                <p className="font-medium">{q.question}</p>
                <p className="text-sm text-slate-600">意図: {q.intent}</p>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="アクション提案">
          <p className="mb-2">{output.actionProposal.summary}</p>
          <Bullets bullets={output.actionProposal.bullets} />
        </Section>
      </main>

      <AppFooter />
    </div>
  )
}
