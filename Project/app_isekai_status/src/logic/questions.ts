export interface Question {
  id: number;
  text: string;
  choices: { label: 'A' | 'B' | 'C' | 'D'; text: string }[];
}

export const QUESTIONS: Question[] = [
  {
    id: 1,
    text: '体を動かすこと・体力について、一番近いのはどれですか？',
    choices: [
      { label: 'A', text: '運動習慣がある。体力には自信がある' },
      { label: 'B', text: 'たまに動くくらい。体力は普通' },
      { label: 'C', text: '運動はほぼしない。体力は低め' },
      { label: 'D', text: '体力はないが、精神力でカバーしている' },
    ],
  },
  {
    id: 2,
    text: '「運が良い」と感じることはありますか？',
    choices: [
      { label: 'A', text: 'よくある。タイミングが合うことが多い' },
      { label: 'B', text: 'どちらとも言えない。普通だと思う' },
      { label: 'C', text: 'あまりない。実力でなんとかしてきた感じ' },
      { label: 'D', text: '運より、仕組みと準備で結果を出すタイプ' },
    ],
  },
  {
    id: 3,
    text: '複数のプロジェクトを同時に進めているとき、どんな感覚ですか？',
    choices: [
      { label: 'A', text: 'わりと得意。切り替えがうまくできる' },
      { label: 'B', text: 'できてはいるが、内心しんどい' },
      { label: 'C', text: '苦手。一つに集中したいタイプ' },
      { label: 'D', text: '並走はするが、優先順位の整理に時間がかかる' },
    ],
  },
  {
    id: 4,
    text: '「問いを立てる」スキルについて、意識的にやっていますか？',
    choices: [
      { label: 'A', text: '無意識にやっている。もはや癖になっている' },
      { label: 'B', text: '意識してやっている。訓練してきた感覚がある' },
      { label: 'C', text: '得意ではあるが、場によってムラがある' },
      { label: 'D', text: 'そこまで得意だとは思っていない' },
    ],
  },
  {
    id: 5,
    text: '自分の「最大の強み」は何だと思いますか？',
    choices: [
      { label: 'A', text: '場を読む力・空気を察知する力' },
      { label: 'B', text: '構造化・言語化する力（頭の中を整理して伝える）' },
      { label: 'C', text: '人とつながる力・場をつくる力' },
      { label: 'D', text: '新しいことへの適応・学習の速さ' },
    ],
  },
  {
    id: 6,
    text: '批判・否定・失敗を受けたとき、どう対処しますか？',
    choices: [
      { label: 'A', text: 'わりと引きずらない。気持ちの切り替えが早い' },
      { label: 'B', text: 'しばらく考え込むが、最終的には前に進める' },
      { label: 'C', text: '深く受け止めてしまう。回復に時間がかかる' },
      { label: 'D', text: '批判よりも「なぜそう言われたか」の分析を先にする' },
    ],
  },
];
