/** メインファシリの16タイプ（診断アプリと id を揃える） */
export type FacilitatorTypeItem = { id: string; name: string }

export const facilitatorTypes: FacilitatorTypeItem[] = [
  { id: 'conductor', name: '場の指揮者' },
  { id: 'engine', name: '推進のエンジン' },
  { id: 'tuner', name: '場の調律師' },
  { id: 'spark', name: '共感のスパーク' },
  { id: 'navigator', name: '戦略のナビゲーター' },
  { id: 'pioneer', name: '直感の開拓者' },
  { id: 'director', name: '場の演出家' },
  { id: 'moodmaker', name: 'ムードメーカー' },
  { id: 'helmsman', name: '静かな舵取り' },
  { id: 'recorder', name: '柔軟な記録者' },
  { id: 'foundation', name: '信頼の土台' },
  { id: 'listener', name: '寄り添う聴き手' },
  { id: 'strategist', name: '静かな戦略家' },
  { id: 'compass', name: '流れを読む羅針盤' },
  { id: 'guardian', name: '場の守り人' },
  { id: 'resonator', name: '静かな共鳴者' },
]
