/**
 * タイプ別相性（4-C）
 * 相性が良い2〜3タイプ・難しい2〜3タイプ＋振る舞いヒント
 */

export interface CompatibilityItem {
  typeId: string;
  typeName: string;
  hint: string;
}

export interface TypeCompatibility {
  good: CompatibilityItem[];
  difficult: CompatibilityItem[];
}

const typeNames: Record<string, string> = {
  conductor: '場の指揮者',
  engine: '推進のエンジン',
  tuner: '場の調律師',
  spark: '共感のスパーク',
  navigator: '戦略のナビゲーター',
  pioneer: '直感の開拓者',
  director: '場の演出家',
  moodmaker: 'ムードメーカー',
  helmsman: '静かな舵取り',
  recorder: '柔軟な記録者',
  foundation: '信頼の土台',
  listener: '寄り添う聴き手',
  strategist: '静かな戦略家',
  compass: '流れを読む羅針盤',
  guardian: '場の守り人',
  resonator: '静かな共鳴者',
};

const compatibilities: Record<string, TypeCompatibility> = {
  conductor: {
    good: [
      { typeId: 'listener', typeName: typeNames.listener, hint: '参加者に寄り添うサブがいることで、あなたは進行に集中できる。聴き役を任せ、自分はゴールへ導く役に徹しよう。' },
      { typeId: 'recorder', typeName: typeNames.recorder, hint: '記録と柔軟な軌道修正を任せると、あなたの計画性と相性が良い。役割分担を明確に伝えよう。' },
    ],
    difficult: [
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型は計画より即興を好む。ゴールと時間は共有しつつ、「ここは任せる」と区切りを設けるとぶつかりにくい。' },
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: '盛り上がり優先になりがち。時間と論点の確認を「一緒にやろう」と伝え、二人で区切りを守ると良い。' },
    ],
  },
  engine: {
    good: [
      { typeId: 'foundation', typeName: typeNames.foundation, hint: '安心感を作るサブが参加者を支えてくれる。あなたは推進に集中し、関係性はサブに任せよう。' },
      { typeId: 'compass', typeName: typeNames.compass, hint: '流れを読んで導くサブと組むと、あなたのスピードに方向性が加わる。役割を事前にすり合わせよう。' },
    ],
    difficult: [
      { typeId: 'helmsman', typeName: typeNames.helmsman, hint: '堅実型は変化より計画を好む。変更の理由を短く伝え、「ここは一緒に進めよう」と声をかけると安心してもらえる。' },
      { typeId: 'strategist', typeName: typeNames.strategist, hint:  '裏方型は表に出るのを好まない。あなたが表に立ち、戦略の相談は「〇〇はどう思う？」と聞く形にすると良い。' },
    ],
  },
  tuner: {
    good: [
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型が前に進めている間、あなたは参加者の声をつなぐ役に。役割を分けると調和しやすい。' },
      { typeId: 'spark', typeName: typeNames.spark, hint: '共感型が火をつけ、あなたが調律する。盛り上がりと整理のタイミングを「ここでまとめよう」と伝えよう。' },
    ],
    difficult: [
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型は即興で道を変える。あなたの「一度まとめよう」を事前に伝え、区切りを作るとぶつかりにくい。' },
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は計画を優先しがち。あなたの「参加者の声を拾う」役割を明確に伝え、時間の折半を提案すると良い。' },
    ],
  },
  spark: {
    good: [
      { typeId: 'helmsman', typeName: typeNames.helmsman, hint: '堅実型が記録と進行を支えてくれる。あなたは盛り上げに集中し、時間の区切りはサブに任せよう。' },
      { typeId: 'tuner', typeName: typeNames.tuner, hint: '調律師型が参加者の声をつなぐ。あなたが火をつけ、サブがハーモニーを整える役割分担に。' },
    ],
    difficult: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は時間厳守を好む。盛り上がりの区切りを「〇分でまとめよう」と事前に決めておくと良い。' },
      { typeId: 'strategist', typeName: typeNames.strategist, hint: '戦略型は表に出ない。あなたが場を動かし、サブには「気になる点あったら教えて」と聞く形に。' },
    ],
  },
  navigator: {
    good: [
      { typeId: 'recorder', typeName: typeNames.recorder, hint: '記録型が事実を拾い、あなたが空気を読んで道筋を示す。役割が補い合いやすい。' },
      { typeId: 'guardian', typeName: typeNames.guardian, hint: '守り人型が関係性を守り、あなたが戦略を描く。表と裏の役割を分けると良い。' },
    ],
    difficult: [
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: 'ムード型は即興で盛り上げたがる。あなたの「ここで道筋を決めよう」を短く伝え、一緒に区切りを作ると良い。' },
      { typeId: 'listener', typeName: typeNames.listener, hint: '聴き手型は計画より参加者の状態を優先。あなたが時間とゴールを示し、「〇〇さんはどう？」とサブに聴き役を任せよう。' },
    ],
  },
  pioneer: {
    good: [
      { typeId: 'foundation', typeName: typeNames.foundation, hint: '土台型が参加者を支えてくれる。あなたは新しい道を切り拓き、安心感はサブに任せよう。' },
      { typeId: 'compass', typeName: typeNames.compass, hint: '羅針盤型がさりげなく方向を示す。あなたがブレークスルーを起こし、サブが参加者を導く役に。' },
    ],
    difficult: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は計画を大切にする。あなたの「ここは変えよう」を理由付きで短く伝え、了承を得てから動くと良い。' },
      { typeId: 'helmsman', typeName: typeNames.helmsman, hint: '舵取り型は着実な進行を好む。変更点は「〇〇の理由で、ここだけ変えたい」と伝え、範囲を限定すると安心してもらえる。' },
    ],
  },
  director: {
    good: [
      { typeId: 'strategist', typeName: typeNames.strategist, hint: '戦略型が裏で設計を支えてくれる。あなたは演出に集中し、進め方の相談はサブに。' },
      { typeId: 'listener', typeName: typeNames.listener, hint: '聴き手型が参加者の感情を拾う。あなたが山場を設計し、参加者の反応はサブから聞こう。' },
    ],
    difficult: [
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型はスピードを重視。演出の「間」を「〇分だけ」と伝え、短い区切りで盛り上がりを作ると良い。' },
      { typeId: 'recorder', typeName: typeNames.recorder, hint: '記録型は事実優先になりがち。感情の山場の意図を「ここで〇〇を感じてほしい」と伝えると合わせやすい。' },
    ],
  },
  moodmaker: {
    good: [
      { typeId: 'helmsman', typeName: typeNames.helmsman, hint: '舵取り型が時間と進行を守ってくれる。あなたは盛り上げに集中し、区切りはサブに任せよう。' },
      { typeId: 'guardian', typeName: typeNames.guardian, hint: '守り人型が場の安全を支える。あなたがエネルギーを高め、サブが参加者を守る役割に。' },
    ],
    difficult: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は計画と時間を優先。盛り上がりの時間を「〇分まで」と決め、その中で最大化すると良い。' },
      { typeId: 'strategist', typeName: typeNames.strategist, hint: '戦略型は表に出ない。あなたが表で盛り上げ、サブには「気になる点を後で教えて」と伝えよう。' },
    ],
  },
  helmsman: {
    good: [
      { typeId: 'spark', typeName: typeNames.spark, hint: '共感型が場に火をつけてくれる。あなたは記録と進行に集中し、盛り上げはサブに任せよう。' },
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: 'ムード型が参加者のエネルギーを高める。あなたが舵を取り、場の温度はサブに任せると良い。' },
    ],
    difficult: [
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型は計画を変えたがる。変更は「〇〇のため、ここだけ」と範囲を伝え、了承を得てから進めよう。' },
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型はスピードを出す。あなたの「ここは着実に」を理由付きで伝え、ペースの折半を提案すると良い。' },
    ],
  },
  recorder: {
    good: [
      { typeId: 'navigator', typeName: typeNames.navigator, hint: 'ナビ型が道筋を示し、あなたが記録と軌道修正をする。役割が補い合いやすい。' },
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型がゴールを示し、あなたが発言を拾いながら進める。計画と柔軟性のバランスが取りやすい。' },
    ],
    difficult: [
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: 'ムード型は盛り上がり優先。あなたの「一度まとめよう」を区切りとして伝え、一緒に時間を守ると良い。' },
      { typeId: 'resonator', typeName: typeNames.resonator, hint: '共鳴型は静けさを大切にする。あなたが「ここで確認を」と声をかける役割を担い、サブの静けさを尊重しよう。' },
    ],
  },
  foundation: {
    good: [
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型が前に進め、あなたが参加者を支える。役割が分かれると安心感と成果の両立がしやすい。' },
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型が新しい道を切り拓き、あなたが参加者の安心感を作る。挑戦と土台の役割分担に。' },
    ],
    difficult: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は時間厳守。あなたの「もう少し聴きたい」を「〇分だけ」と伝え、区切りを作ると良い。' },
      { typeId: 'navigator', typeName: typeNames.navigator, hint: 'ナビ型は戦略を優先。参加者への寄り添いを「この区切りで」と時間を決めて行うと合わせやすい。' },
    ],
  },
  listener: {
    good: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型がゴールへ導き、あなたが参加者に寄り添う。導く役と聴く役で補い合える。' },
      { typeId: 'director', typeName: typeNames.director, hint: '演出家型が山場を設計し、あなたが参加者の感情を拾う。演出と傾聴の役割分担に。' },
    ],
    difficult: [
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型はスピードを出す。あなたの「ここは聴こう」を「〇分だけ」と区切り、その中で深く聴くと良い。' },
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型は即興で進める。参加者を聴く時間を「このタイミングで」と決めて伝えるとぶつかりにくい。' },
    ],
  },
  strategist: {
    good: [
      { typeId: 'director', typeName: typeNames.director, hint: '演出家型が表で場を盛り上げ、あなたが裏で戦略を支える。表と裏の役割がはっきりする。' },
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: 'ムード型が場のエネルギーを高め、あなたが進め方の設計を支える。役割を事前に伝えよう。' },
    ],
    difficult: [
      { typeId: 'spark', typeName: typeNames.spark, hint: 'スパーク型は即興で火をつける。あなたの「ここで道筋を」を短く伝え、一緒に区切りを作ると良い。' },
      { typeId: 'listener', typeName: typeNames.listener, hint: '聴き手型は参加者優先。あなたの戦略を「参加者のためには〇〇」と伝えると納得してもらいやすい。' },
    ],
  },
  compass: {
    good: [
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型が新しい道を切り拓き、あなたがさりげなく方向を示す。挑戦と導きの役割に。' },
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型が前に進め、あなたが流れを読んで調整する。スピードと方向のバランスが取りやすい。' },
    ],
    difficult: [
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は計画を前面に。あなたの「流れで変えよう」を「〇〇の理由で」と短く伝え、了承を得ると良い。' },
      { typeId: 'helmsman', typeName: typeNames.helmsman, hint: '舵取り型は着実な進行を好む。変更は「ここだけ」と範囲を伝え、一緒に進めると安心してもらえる。' },
    ],
  },
  guardian: {
    good: [
      { typeId: 'navigator', typeName: typeNames.navigator, hint: 'ナビ型が戦略を描き、あなたが関係性を守る。道筋と安全の役割分担に。' },
      { typeId: 'moodmaker', typeName: typeNames.moodmaker, hint: 'ムード型が場を盛り上げ、あなたが参加者を守る。盛り上がりと安心感の両立がしやすい。' },
    ],
    difficult: [
      { typeId: 'pioneer', typeName: typeNames.pioneer, hint: '開拓型はリスクを取る。あなたの「ここは守ろう」を「参加者のため」と伝え、範囲を決めると良い。' },
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型はスピードを出す。対立しそうな場面では「少しペースを落として」と伝え、安全を優先する区切りを作ろう。' },
    ],
  },
  resonator: {
    good: [
      { typeId: 'tuner', typeName: typeNames.tuner, hint: '調律師型が参加者の声をつなぎ、あなたが静かに共鳴する。調和と静けさの役割に。' },
      { typeId: 'guardian', typeName: typeNames.guardian, hint: '守り人型が関係性を守り、あなたが場に寄り添う。安全と共鳴で深い場を作れる。' },
    ],
    difficult: [
      { typeId: 'engine', typeName: typeNames.engine, hint: '推進型は動きが速い。あなたの「ここは静かに」を「〇分だけ」と区切り、そのあとはサブに任せると良い。' },
      { typeId: 'conductor', typeName: typeNames.conductor, hint: '指揮型は進行を優先。静けさの時間を「この区切りで」と事前に決め、二人で守ると合わせやすい。' },
    ],
  },
};

export function getTypeCompatibility(typeId: string): TypeCompatibility | undefined {
  return compatibilities[typeId];
}
