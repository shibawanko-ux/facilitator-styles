/** 05_evaluation_items.md に準拠。評価項目 ID と文言 */

/** 6軸の軸ID（09 sectionComments キー・03 §4 の順） */
export const SIX_AXIS_IDS = [
  'design',
  'visibility',
  'observation',
  'hold',
  'questioning',
  'flow',
] as const
export type SixAxisId = (typeof SIX_AXIS_IDS)[number]

/** 6軸と項目IDの対応（03 §4 集計・レーダー用） */
export const SIX_AXIS_ITEM_IDS: Record<SixAxisId, string[]> = {
  design: ['E2', 'E3'], // 説明・設計
  visibility: ['E1', 'E4'], // 見える化・編集
  observation: ['B4'], // 場の観察
  hold: ['B2', 'B3', 'B6', 'B1'], // 場のホールド・安心感
  questioning: ['B5', 'B7', 'B8', 'B9', 'B10'], // 問いかけ・リフレーミング
  flow: ['F1', 'F2', 'F3', 'F4'], // 流れ・即興
}

/** 6軸の表示ラベル（入力・結果画面用） */
export const SIX_AXIS_LABELS: Record<SixAxisId, string> = {
  design: '説明・設計',
  visibility: '見える化・編集',
  observation: '場の観察',
  hold: '場のホールド・安心感',
  questioning: '問いかけ・リフレーミング',
  flow: '流れ・即興',
}

/** 6軸の説明（結果画面の観点「？」ツールチップ用・03 §4 コアスキル対応・各200字程度） */
export const SIX_AXIS_DESCRIPTIONS: Record<SixAxisId, string> = {
  design:
    '目的・進め方・問いが参加者に伝わっていたかを表す軸です。ワークのオブジェクト（何を学ぶか・何をするか）が明確で、説明が届いていたかどうかが評価の中心になります。ファシリテーターの「説明力」に相当し、設計の見せ方や言葉の選び方が反映されます。',
  visibility:
    '発言や成果が全体で整理され、見える形で編集されていたかを表す軸です。付箋のまとめ方、板書、共有の仕方など、情報が参加者にどう届いたかが問われます。ファシリテーションの的確さや「情報編集力」に相当し、場のアウトプットの質につながります。',
  observation:
    '参加者の反応や空気を捉え、場に活かしていたかを表す軸です。表情・発言の量・沈黙・盛り上がりなどに気を配り、それに応じて進め方や問いを変えていたかが評価されます。ファシリテーターの「場の観察力」に相当し、一方的にならずに場を読めていたかがポイントです。',
  hold:
    '参加者と共創できていたか、対話や安心して話せる場が保たれていたかを表す軸です。発言しやすい雰囲気、意見の受け止め方、役割の分かち合いなどが含まれます。ファシリテーターの「場のホールド力」に相当し、安心感や信頼が場にあったかどうかが反映されます。',
  questioning:
    '発言を違う角度で返す、個性を引き出す問いかけ、凝り固まった発想をほぐす問いかけなどができていたかを表す軸です。リフレーミングや「問いかけの定石」の活用が評価の中心で、参加者の気づきや深まりを促せていたかが問われます。ファシリテーターの「リフレーミング力」に相当します。',
  flow:
    'ワークショップの流れの的確さ、状況に合わせた柔軟な進め方、時間と内容のバランスが取れていたかを表す軸です。予定通り進める力と、その場で調整する力の両方が含まれます。即興力や情報編集力（流れの設計）に相当し、全体のテンポや区切り方が参加者にどう感じられたかが反映されます。',
}

export interface EvaluationItem {
  id: string
  label: string
}

/** 鷹の目（全体を見る）E1〜E4 */
export const itemsEagle: EvaluationItem[] = [
  { id: 'E1', label: 'ファシリテーションは的確だったか？（テーブルファシリの行動含む）' },
  { id: 'E2', label: 'オブジェクト（ワーク内容や学び）は提供できていたか？' },
  { id: 'E3', label: '目的・進め方・問いが参加者に伝わっていたか？' },
  { id: 'E4', label: '発言や成果が全体で整理され、見える化されていたか？' },
]

/** 虫の目（参加者の行動を見る）B1〜B10 */
export const itemsBug: EvaluationItem[] = [
  { id: 'B1', label: '参加者と共創できていたか？' },
  { id: 'B2', label: '参加者は対話できていたか？' },
  { id: 'B3', label: 'ファシリテーターは誰も学びを取りこぼしていないか？' },
  { id: 'B4', label: '参加者の反応や空気を捉え、場に活かしていたか？' },
  { id: 'B5', label: '発言を違う角度で返し、気づきや深まりを促せていたか？' },
  { id: 'B6', label: '安心して話せる・挑戦できる場が保たれていたか？' },
  { id: 'B7', label: '相手の個性・こだわりを引き出せる問いかけだったか？' },
  { id: 'B8', label: '適度な制約で考えを深める問いかけだったか？' },
  { id: 'B9', label: '答えたくなる・遊び心のある問いかけだったか？' },
  { id: 'B10', label: '凝り固まった発想をほぐす問いかけだったか？' },
]

/** 魚の目（WSの流れを見る）F1〜F4 */
export const itemsFish: EvaluationItem[] = [
  { id: 'F1', label: 'WSの流れは的確だったか？' },
  { id: 'F2', label: 'ワーク内容のマッチングとフィット感はあったか？' },
  { id: 'F3', label: '状況に合わせて柔軟に進め方や問いを変えられていたか？' },
  { id: 'F4', label: '時間と内容のバランスが取れ、流れが編集されていたか？' },
]

/** 全項目ID（scores のキー順）。6軸の表示順（03 §4）に合わせる */
export const allItemIds: string[] = SIX_AXIS_IDS.flatMap((axisId) => SIX_AXIS_ITEM_IDS[axisId])

/** id → EvaluationItem のマップ（6軸グループ用） */
const itemById: Record<string, EvaluationItem> = {}
;[...itemsEagle, ...itemsBug, ...itemsFish].forEach((item) => {
  itemById[item.id] = item
})

/** 6軸ごとの評価項目リスト（入力画面のセクション表示用・03 §4 順） */
export const itemsBySixAxis: { axisId: SixAxisId; label: string; items: EvaluationItem[] }[] =
  SIX_AXIS_IDS.map((axisId) => ({
    axisId,
    label: SIX_AXIS_LABELS[axisId],
    items: SIX_AXIS_ITEM_IDS[axisId].map((id) => itemById[id]).filter(Boolean),
  }))
