import { Question } from './types';

export const questions: Question[] = [
  // 軸1: 介入スタイル（触発型 ⇔ 見守型）
  {
    id: 1,
    axis: 'intervention',
    text: 'ワークショップで沈黙が続いたとき、あなたはどうしますか？',
    optionA: 'すぐに声をかけて場を動かす',
    optionB: '参加者が動き出すまで待つ',
  },
  {
    id: 2,
    axis: 'intervention',
    text: '議論が停滞しているとき、あなたは...',
    optionA: '新しい視点や問いを投げかける',
    optionB: '参加者の内省の時間として見守る',
  },
  {
    id: 3,
    axis: 'intervention',
    text: '場のエネルギーが低いと感じたとき...',
    optionA: '自ら盛り上げ役になる',
    optionB: '自然な流れを待つ',
  },
  {
    id: 4,
    axis: 'intervention',
    text: '参加者の発言が少ないとき...',
    optionA: '積極的に指名や問いかけをする',
    optionB: '発言しやすい雰囲気作りに徹する',
  },
  {
    id: 5,
    axis: 'intervention',
    text: 'グループワークの途中で...',
    optionA: '各グループに声をかけて回る',
    optionB: '必要な時だけサポートに入る',
  },
  {
    id: 6,
    axis: 'intervention',
    text: '意見が出にくい場面で...',
    optionA: '自分から例を出して呼び水にする',
    optionB: '参加者が自分の言葉で話し出すのを待つ',
  },
  {
    id: 7,
    axis: 'intervention',
    text: 'ファシリテーション中、あなたの存在感は...',
    optionA: '場の中心にいることが多い',
    optionB: '場の端から見守ることが多い',
  },
  {
    id: 8,
    axis: 'intervention',
    text: '参加者同士の対話が始まったとき...',
    optionA: '必要に応じて介入・補足する',
    optionB: '対話の邪魔にならないよう控える',
  },

  // 軸2: 知覚対象（観察型 ⇔ 洞察型）
  {
    id: 9,
    axis: 'perception',
    text: '参加者の状態を把握するとき、重視するのは...',
    optionA: '発言内容や表情など具体的な情報',
    optionB: '場の空気や雰囲気',
  },
  {
    id: 10,
    axis: 'perception',
    text: '議論を整理するとき...',
    optionA: '発言をそのまま記録・可視化する',
    optionB: '言葉の背景にある意図を読み取る',
  },
  {
    id: 11,
    axis: 'perception',
    text: '参加者の変化に気づくきっかけは...',
    optionA: '発言の内容や頻度の変化',
    optionB: 'なんとなく感じる空気の変化',
  },
  {
    id: 12,
    axis: 'perception',
    text: 'グループの状態を見るとき...',
    optionA: '各メンバーの発言を追う',
    optionB: 'グループ全体の雰囲気を感じる',
  },
  {
    id: 13,
    axis: 'perception',
    text: '振り返りの場面で注目するのは...',
    optionA: '具体的な成果や発言',
    optionB: '参加者の表情や場のエネルギー',
  },
  {
    id: 14,
    axis: 'perception',
    text: '対立が起きたとき、まず確認するのは...',
    optionA: '何について対立しているか（事実）',
    optionB: 'なぜ対立しているか（感情・背景）',
  },
  {
    id: 15,
    axis: 'perception',
    text: '議論の進捗を判断するとき...',
    optionA: 'アウトプットの量や質',
    optionB: '参加者の納得感や熱量',
  },
  {
    id: 16,
    axis: 'perception',
    text: '自分のファシリテーションを振り返るとき...',
    optionA: '発言記録や成果物を見返す',
    optionB: 'そのときの場の感覚を思い出す',
  },

  // 軸3: 判断基準（目的型 ⇔ 関係型）
  {
    id: 17,
    axis: 'judgment',
    text: '時間が足りなくなったとき...',
    optionA: 'ゴールに向けて議論を絞る',
    optionB: '参加者の納得感を優先して延長を検討',
  },
  {
    id: 18,
    axis: 'judgment',
    text: '議論がゴールから逸れたとき...',
    optionA: '軌道修正して本題に戻す',
    optionB: '逸れた話にも意味があると捉える',
  },
  {
    id: 19,
    axis: 'judgment',
    text: '参加者全員の合意が取れないとき...',
    optionA: '多数決や時間で区切る',
    optionB: '全員が納得するまで対話を続ける',
  },
  {
    id: 20,
    axis: 'judgment',
    text: 'ワークショップの成功を測るとき...',
    optionA: '目標の達成度',
    optionB: '参加者の満足度や関係性の変化',
  },
  {
    id: 21,
    axis: 'judgment',
    text: '予定したアジェンダと参加者の関心がずれたとき...',
    optionA: 'アジェンダを優先する',
    optionB: '参加者の関心に寄り添う',
  },
  {
    id: 22,
    axis: 'judgment',
    text: 'グループワークの成果物について...',
    optionA: '質と量を重視する',
    optionB: 'プロセスでの学びを重視する',
  },
  {
    id: 23,
    axis: 'judgment',
    text: '参加者から個人的な相談を受けたとき...',
    optionA: '本題に関係するか判断して対応',
    optionB: 'まず話を聴いて関係性を大切にする',
  },
  {
    id: 24,
    axis: 'judgment',
    text: 'ファシリテーターとして大切にしているのは...',
    optionA: '決めたゴールへ導くこと',
    optionB: '参加者が安心して話せる場を作ること',
  },

  // 軸4: 場への関わり（設計型 ⇔ 即興型）
  {
    id: 25,
    axis: 'engagement',
    text: 'ワークショップの準備で重視するのは...',
    optionA: '詳細なタイムラインと進行表',
    optionB: '大まかな流れと柔軟性',
  },
  {
    id: 26,
    axis: 'engagement',
    text: '予定通りに進まないとき...',
    optionA: '計画に戻す方法を考える',
    optionB: 'その場の流れに任せる',
  },
  {
    id: 27,
    axis: 'engagement',
    text: 'ファシリテーション中に新しいアイデアが浮かんだとき...',
    optionA: 'メモして次回に活かす',
    optionB: 'その場で試してみる',
  },
  {
    id: 28,
    axis: 'engagement',
    text: '参加者から予想外の質問が来たとき...',
    optionA: '準備した内容に沿って対応',
    optionB: 'その場で一緒に考える',
  },
  {
    id: 29,
    axis: 'engagement',
    text: 'ワークショップの構成は...',
    optionA: '事前に細かく決めておく',
    optionB: '当日の参加者を見て調整する',
  },
  {
    id: 30,
    axis: 'engagement',
    text: '想定外のトラブルが起きたとき...',
    optionA: '事前に用意したプランBを使う',
    optionB: 'その場で最善策を考える',
  },
  {
    id: 31,
    axis: 'engagement',
    text: '成功したファシリテーションを振り返ると...',
    optionA: '計画通りに進んだとき',
    optionB: '予想外の展開が良い結果になったとき',
  },
  {
    id: 32,
    axis: 'engagement',
    text: 'ファシリテーションで大切にしているのは...',
    optionA: '再現性のある進行',
    optionB: '一期一会の場作り',
  },
];

// 質問をシャッフルする関数
export function shuffleQuestions(questions: Question[]): Question[] {
  const shuffled = [...questions];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
