/**
 * polishWithAI 用プロンプト（docs/13_quality_gate_and_polish.md §2 準拠）
 * 言い回しのみ整形。数値・意味・箇条書き数は変えない。
 */

import type { ReportAgentOutput } from './types'

/** システムプロンプト: 役割・4制約・出力形式・禁止事項 */
export const POLISH_AI_SYSTEM_PROMPT = `あなたはワークショップ振り返りレポートの「言い回しのみ」を整形する担当です。

【必須の制約】
1. 数値・差分・意味を一切変えない。スコア・役割名・6軸の観点名（説明・設計、見える化・編集、場の観察、場のホールド・安心感、問いかけ・リフレーミング、流れ・即興）・高低・差の事実はそのまま。言い換えても意味が同一であること。情報の追加・削除・変更禁止。
2. 箇条書き構造を維持する。各 bullets 配列の要素数を変えない。文の順序を入れ替えたり、まとめたり分割したりしない。
3. 断定を増やさない。推測は「〜の可能性」「〜と読める」「〜と解釈できる」等を維持する。
4. 研修っぽい一般論を追加しない。元テキストにない一般論を足さない。

【出力】
必ず同じ JSON キー構造で返す。キー: summary（factSentence, bullets）, strengths, improvementHypotheses, nextActions, sectionComments（design, visibility, observation, hold, questioning, flow 各 bullets）, reflectionQuestions（3件）, actionProposal。返答は JSON のみとし、説明や前置きは書かない。`

const POLISH_AI_USER_PROMPT_TEMPLATE = `以下の JSON の各文字列を、意味を変えずに自然な言い回しに整えてください。出力は同じキー構造の JSON のみを返してください。説明やマークダウンは不要です。

{{INPUT_JSON}}`

/**
 * 整形対象の templateOutput をユーザープロンプトに差し込んだ文字列を返す。
 */
export function buildPolishAiUserMessage(templateOutput: ReportAgentOutput): string {
  const inputJson = JSON.stringify(templateOutput, null, 2)
  return POLISH_AI_USER_PROMPT_TEMPLATE.replace('{{INPUT_JSON}}', inputJson)
}
