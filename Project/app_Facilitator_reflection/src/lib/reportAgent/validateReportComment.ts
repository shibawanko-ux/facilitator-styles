/**
 * レポートコメント品質ゲート（docs/13_quality_gate_and_polish.md §1 準拠）
 * - テンプレ出力は必ず合格する設計とする
 * - AI 自然化後に validate → NG ならテンプレにフォールバックする
 */

import type { ReportAgentOutput } from './types'

const MAX_CHARS_PER_BLOCK = 200
const MIN_BULLET_CHARS = 15
const MIN_QUESTION_CHARS = 12
const MIN_INTENT_CHARS = 10

/** 6軸の観点名（少なくとも1つは全文に含まれること） */
const SECTION_NAMES_6 = [
  '説明・設計',
  '見える化',
  '場の観察',
  '場のホールド',
  '問いかけ',
  '流れ',
]

/** 相対差の言及パターン（1回以上あること） */
const RELATIVE_DIFF_PATTERNS = [
  /平均との差|高低差|点差|高め|低め|[\d.]*点\s*[高低]|差がある|役割間で|メインが.*(高め|低め)|参加者より|〇点|約?\d*\.?\d*点/
]

/** 相対差の具体性：数値または highest/lowest に紐づく言及が1回以上 */
const CONCRETE_DIFF_PATTERNS = [
  /\d+\.?\d*点|差が\s*\d|約?\s*\d+\.?\d*\s*点|最高|最低|最も\s*高|最も\s*低|highest|lowest/
]

/** 抽象語のみとみなすパターン（これだけの文で終わっていないこと） */
const ABSTRACT_ONLY_PATTERN = /^(良かった|学びがあった|よかったです|満足でした|とても良かった|ありがとうございました)[。.]*$/u

/** 具体語（観点語）辞書：strengths / improvementHypotheses の少なくとも1 bullet が含むこと */
const CONCRETE_TERMS = [
  '心理的安全性',
  '挑戦',
  '実践',
  '内省',
  '対話',
  '問い',
  '関係性',
]

export interface ValidateReportCommentResult {
  ok: boolean
  errors: string[]
}

/**
 * レポート生成結果を品質ゲートで検証する。
 * 合格時: { ok: true, errors: [] }
 * 不合格時: { ok: false, errors: ['理由1', '理由2', ...] }
 */
export function validateReportComment(
  output: ReportAgentOutput
): ValidateReportCommentResult {
  const errors: string[] = []

  // 検証用に全文を集約（4ブロック＋sectionComments で観点名・相対差を判定）
  const allText = collectAllRelevantText(output)

  // 1) 6軸の観点名が少なくとも1つは含まれる
  const hasSectionName = SECTION_NAMES_6.some((name) => allText.includes(name))
  if (!hasSectionName) {
    errors.push('6軸の観点名（説明・設計、見える化、場の観察、場のホールド、問いかけ、流れのいずれか）が少なくとも1回は含まれる必要があります。')
  }

  // 2) 4ブロックが揃っている（強み・改善仮説・次回アクション2点・総評）
  const summaryOk =
    output.summary &&
    typeof output.summary.factSentence === 'string' &&
    Array.isArray(output.summary.bullets)
  const strengthsOk =
    output.strengths && Array.isArray(output.strengths.bullets) && output.strengths.bullets.length > 0
  const improvementOk =
    output.improvementHypotheses &&
    Array.isArray(output.improvementHypotheses.bullets) &&
    output.improvementHypotheses.bullets.length > 0
  const nextActionsOk =
    output.nextActions &&
    typeof output.nextActions.summary === 'string' &&
    Array.isArray(output.nextActions.bullets) &&
    output.nextActions.bullets.length >= 2

  if (!summaryOk) errors.push('総評（summary）が空でない必要があります。')
  if (!strengthsOk) errors.push('強み（strengths）が1件以上必要です。')
  if (!improvementOk) errors.push('改善仮説（improvementHypotheses）が1件以上必要です。')
  if (!nextActionsOk) errors.push('次回アクション（nextActions）に説明と箇条書き2点以上が必要です。')

  const reflectionOk =
    Array.isArray(output.reflectionQuestions) &&
    output.reflectionQuestions.length >= 3 &&
    output.reflectionQuestions.every((q) => q?.question && q?.intent)
  if (!reflectionOk) errors.push('振り返りの問い（reflectionQuestions）が3問以上必要です。')

  const actionProposalOk =
    output.actionProposal &&
    typeof output.actionProposal.summary === 'string' &&
    Array.isArray(output.actionProposal.bullets) &&
    output.actionProposal.bullets.length > 0
  if (!actionProposalOk) errors.push('アクション提案（actionProposal）に説明と箇条書き1点以上が必要です。')

  // 3) 抽象語のみで終わっていない
  const bulletsFromFourBlocks = [
    ...(output.summary?.bullets ?? []),
    ...(output.strengths?.bullets ?? []),
    ...(output.improvementHypotheses?.bullets ?? []),
    ...(output.nextActions?.bullets ?? []),
  ].filter(Boolean)
  const allAbstractOnly =
    bulletsFromFourBlocks.length > 0 &&
    bulletsFromFourBlocks.every((line) => ABSTRACT_ONLY_PATTERN.test(line.trim()))
  if (allAbstractOnly) {
    errors.push('抽象語のみ（例：良かった、学びがあった）で終わっていません。具体的な観察・相対差・アクションを含めてください。')
  }

  // 4) 相対差・数値差の言及が1回以上（summary.factSentence でも可）
  const hasRelativeDiff = RELATIVE_DIFF_PATTERNS.some((re) => re.test(allText))
  const hasNumericDiff =
    /\d+\.?\d*点|diffFromOverall|maxMinDiff|平均との差|点差|約?\d*\.?\d*点\s*[高低]/.test(allText)
  if (!hasRelativeDiff && !hasNumericDiff) {
    errors.push('相対差または数値差（平均との差・高め／低め・点差・〇点など）の言及が1回以上必要です。')
  }

  // 5) 各ブロック 200 字以内
  const summaryText = [output.summary?.factSentence ?? '', ...(output.summary?.bullets ?? [])].join('')
  const strengthsText = (output.strengths?.bullets ?? []).join('')
  const improvementText = (output.improvementHypotheses?.bullets ?? []).join('')
  const nextActionsText = [
    output.nextActions?.summary ?? '',
    ...(output.nextActions?.bullets ?? []),
  ].join('')

  if (summaryText.length > MAX_CHARS_PER_BLOCK) {
    errors.push(`総評（summary）は${MAX_CHARS_PER_BLOCK}字以内にしてください（現在${summaryText.length}字）。`)
  }
  if (strengthsText.length > MAX_CHARS_PER_BLOCK) {
    errors.push(`強み（strengths）は${MAX_CHARS_PER_BLOCK}字以内にしてください（現在${strengthsText.length}字）。`)
  }
  if (improvementText.length > MAX_CHARS_PER_BLOCK) {
    errors.push(`改善仮説（improvementHypotheses）は${MAX_CHARS_PER_BLOCK}字以内にしてください（現在${improvementText.length}字）。`)
  }
  if (nextActionsText.length > MAX_CHARS_PER_BLOCK) {
    errors.push(`次回アクション（nextActions）は${MAX_CHARS_PER_BLOCK}字以内にしてください（現在${nextActionsText.length}字）。`)
  }

  // 6) 6軸カバレッジ: sectionComments は各軸ちょうど2 bullets
  const sc = output.sectionComments
  const sixAxisKeys = ['design', 'visibility', 'observation', 'hold', 'questioning', 'flow'] as const
  for (const key of sixAxisKeys) {
    if (!sc?.[key]?.bullets || sc[key].bullets.length !== 2) {
      errors.push(`sectionComments.${key} の bullets はちょうど2つ必要です。`)
    }
  }

  const summaryOrStrengthsImprove =
    [output.summary?.factSentence ?? '', ...(output.summary?.bullets ?? [])]
      .concat(output.strengths?.bullets ?? [])
      .concat(output.improvementHypotheses?.bullets ?? [])
      .join('')
  const hasEnoughAxisNames =
    SECTION_NAMES_6.filter((name) => summaryOrStrengthsImprove.includes(name)).length >= 1
  if (!hasEnoughAxisNames) {
    errors.push('summary または strengths/improvementHypotheses のどこかで、6軸の観点名のいずれかが1回以上含まれる必要があります。')
  }

  // 7) 相対差の具体性: 数値または highest/lowest に紐づく言及が1回以上
  const hasConcreteDiff = CONCRETE_DIFF_PATTERNS.some((re) => re.test(allText))
  if (!hasConcreteDiff) {
    errors.push('相対差の具体性として、数値（例：4.2点、差が0.8）または最高/最低に紐づく言及が1回以上必要です。')
  }

  // 8) bullet の最小情報量
  const contentBullets = [
    ...(output.strengths?.bullets ?? []),
    ...(output.improvementHypotheses?.bullets ?? []),
    ...(output.nextActions?.bullets ?? []),
  ]
  for (const b of contentBullets) {
    if (b.length < MIN_BULLET_CHARS) {
      errors.push(`strengths/improvementHypotheses/nextActions の各 bullet は${MIN_BULLET_CHARS}文字以上必要です（${b.length}文字）。`)
      break
    }
  }
  if (Array.isArray(output.reflectionQuestions)) {
    for (const q of output.reflectionQuestions) {
      if (q.question && q.question.length < MIN_QUESTION_CHARS) {
        errors.push(`reflectionQuestions の question は${MIN_QUESTION_CHARS}文字以上必要です。`)
        break
      }
      if (q.intent && q.intent.length < MIN_INTENT_CHARS) {
        errors.push(`reflectionQuestions の intent は${MIN_INTENT_CHARS}文字以上必要です。`)
        break
      }
    }
  }

  // 9) 具体語（観点語）を少なくとも1 bullet が含む
  const hasConcreteInStrengths =
    (output.strengths?.bullets ?? []).some((b) =>
      CONCRETE_TERMS.some((term) => b.includes(term))
    )
  if (!hasConcreteInStrengths && (output.strengths?.bullets ?? []).length > 0) {
    errors.push('strengths の bullets の少なくとも1つに、観点語（心理的安全性・挑戦・実践・内省・対話・問い・関係性など）を含めてください。')
  }
  const hasConcreteInImprovement =
    (output.improvementHypotheses?.bullets ?? []).some((b) =>
      CONCRETE_TERMS.some((term) => b.includes(term))
    )
  if (!hasConcreteInImprovement && (output.improvementHypotheses?.bullets ?? []).length > 0) {
    errors.push('improvementHypotheses の bullets の少なくとも1つに、観点語（心理的安全性・挑戦・実践・内省・対話・問い・関係性など）を含めてください。')
  }

  // 10) 重複抑制: summary.bullets と strengths.bullets で同じ文が重複していないこと
  const summaryBullets = output.summary?.bullets ?? []
  const strengthBullets = output.strengths?.bullets ?? []
  const duplicateSentence = summaryBullets.some((s) =>
    strengthBullets.some((t) => s.trim() === t.trim())
  )
  if (duplicateSentence) {
    errors.push('summary.bullets と strengths.bullets に同一文が含まれています。重複を避けてください。')
  }

  return {
    ok: errors.length === 0,
    errors,
  }
}

/** 観点名・相対差判定用に、レポート本文から参照するテキストを連結する */
function collectAllRelevantText(output: ReportAgentOutput): string {
  const parts: string[] = []
  if (output.summary) {
    parts.push(output.summary.factSentence, ...(output.summary.bullets ?? []))
  }
  if (output.strengths) parts.push(...(output.strengths.bullets ?? []))
  if (output.improvementHypotheses) parts.push(...(output.improvementHypotheses.bullets ?? []))
  if (output.nextActions) {
    parts.push(output.nextActions.summary, ...(output.nextActions.bullets ?? []))
  }
  if (output.sectionComments) {
    const keys = ['design', 'visibility', 'observation', 'hold', 'questioning', 'flow'] as const
    for (const key of keys) {
      const block = output.sectionComments[key]
      if (block?.bullets) parts.push(...block.bullets)
    }
  }
  return parts.filter(Boolean).join('')
}
