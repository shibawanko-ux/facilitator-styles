import type { Answers, Stats, SkillLevel, StatusResult } from './types';

export function calculateStatus(answers: Answers): StatusResult {
  // ベース値（日記分析で補正済み）
  const stats: Stats = {
    hp: 60, mp: 91, sp: 72,       // HP: 日記で疲弊頻度が高いため60に下方修正
    str: 26, agi: 79, vit: 50, def: 74,  // VIT: 大仕事後に2日寝込む実績から50に修正, AGI: 即時カスタマイズ能力で上方修正
    int: 95, wis: 97, mnd: 84,
    cha: 88, emp: 95, ngt: 90, ldr: 85,
    tec: 78, cre: 86, ana: 94, stz: 98,
    luk: 71, foc: 80, adp: 88,
  };

  const skills: Record<string, SkillLevel> = {
    readRoom:   { name: '場を読む',           level: 8,  description: '場の緊張・停滞を即座に察知' },
    question:   { name: '問いを立てる',       level: 9,  description: '本質を射抜く問いで場の深さを変える' },
    customize:  { name: '場をカスタマイズ',   level: 9,  description: '現場の状態を見ながらリアルタイムで調整する（日記より）' },
    pattern:    { name: '型に変換',           level: 8,  description: '経験・知識を再現可能な型へ落とす' },
    design:     { name: '場を設計する',       level: 9,  description: '目的から逆算してWSを構造化する' },
    bridge:     { name: '橋を架ける',         level: 8,  description: '異なる文脈の人同士をつなぐ' },
    sauna:      { name: 'ととのう',           level: 9,  description: 'サウナでSP・MNDを全回復できる（日記より）' },
    ai:         { name: 'Claude召喚',         level: 7,  description: 'AIをチームメンバーとして使役する' },
    multi:      { name: '複数管理',           level: 7,  description: '案件・プロジェクトを並走で回す' },
    visualize:  { name: '可視化する',         level: 7,  description: '頭の中を図・文・画面に落とす' },
  };

  const titles: string[] = ['《型を紡ぐ者》', '《AIを使役せし人》', '《整いし者》'];
  let starStat: keyof Stats = 'stz';
  const weaknesses: string[] = [];

  // Q1：体力
  if (answers.q1 === 'A') { stats.str = 62; stats.vit = 68; }
  else if (answers.q1 === 'B') { stats.str = 38; stats.vit = 50; weaknesses.push('VITが低い。全力を出し切ると2〜3日は寝込む'); }
  else if (answers.q1 === 'C') { stats.str = 14; stats.vit = 38; weaknesses.push('STR・VITが壊滅的に低い。回復に要注意'); }
  else if (answers.q1 === 'D') { stats.str = 14; stats.vit = 38; stats.mp = 96; weaknesses.push('STR・VITが低い（精神力で補完中）'); }

  // Q2：運
  if (answers.q2 === 'A') { stats.luk = 88; }
  else if (answers.q2 === 'B') { stats.luk = 71; }
  else if (answers.q2 === 'C') { stats.luk = 55; weaknesses.push('LUKが低め（実力で補ってきた証拠でもある）'); }
  else if (answers.q2 === 'D') { stats.luk = 60; stats.ana = Math.min(99, stats.ana + 3); }

  // Q3：並走
  if (answers.q3 === 'A') { stats.foc = 75; stats.sp = 78; skills.multi.level = 8; skills.multi.description = '複数案件を軽やかに並走できる'; }
  else if (answers.q3 === 'B') { stats.foc = 80; stats.sp = 68; skills.multi.level = 6; skills.multi.description = 'こなせるが内心しんどい'; weaknesses.push('並走でSPを消耗しやすい'); }
  else if (answers.q3 === 'C') { stats.foc = 91; stats.sp = 58; skills.multi.level = 5; skills.multi.description = '得意ではないがこなしている'; weaknesses.push('並走が苦手なのに並走している（SP消費注意）'); }
  else if (answers.q3 === 'D') { stats.foc = 82; stats.sp = 62; skills.multi.level = 6; skills.multi.description = '優先順位の整理に時間がかかる'; }

  // Q4：問いを立てる
  if (answers.q4 === 'A') { skills.question.level = 10; skills.question.isMax = true; skills.question.description = '天性の才能。無意識に発動する'; stats.wis = 99; }
  else if (answers.q4 === 'B') { skills.question.level = 9; skills.question.description = '訓練で磨いた後天的技術'; }
  else if (answers.q4 === 'C') { skills.question.level = 8; skills.question.description = '場によってムラがある'; }
  else if (answers.q4 === 'D') { skills.question.level = 6; skills.question.description = 'まだ伸びしろがある'; stats.wis = 92; weaknesses.push('問いを立てる力はまだ発展途上'); }

  // Q5：最大の強み
  if (answers.q5 === 'A') {
    skills.readRoom.level = 10; skills.readRoom.isMax = true; skills.readRoom.description = '自認の最大強み。天性の察知力';
    stats.wis = Math.max(stats.wis, 99);
    starStat = 'wis';
    titles.push('《場を読む者》');
  } else if (answers.q5 === 'B') {
    stats.stz = 99; stats.int = 97; stats.ana = Math.max(stats.ana, 97);
    starStat = 'stz';
    titles.push('《言語化の魔術師》');
  } else if (answers.q5 === 'C') {
    stats.emp = 99; stats.cha = 92; stats.ldr = 90;
    starStat = 'emp';
    titles.push('《場を紡ぐ者》');
  } else if (answers.q5 === 'D') {
    stats.adp = 95; stats.tec = 85;
    starStat = 'adp';
    titles.push('《文明吸収者》');
  }

  // Q6：批判への対処
  if (answers.q6 === 'A') { stats.def = 82; stats.mnd = 88; }
  else if (answers.q6 === 'B') { stats.def = 68; stats.mnd = 78; weaknesses.push('批判・失敗を深く受け止める（回復に時間がかかる）'); }
  else if (answers.q6 === 'C') { stats.def = 55; stats.mnd = 65; weaknesses.push('DEF・MNDが低め。精神的ダメージを受けやすい'); }
  else if (answers.q6 === 'D') { stats.def = 75; stats.int = Math.min(99, stats.int + 3); }

  // 日記から判明した固定弱点
  weaknesses.push('集中が途切れるとSNSに逃げるクセがある（日記より）');
  weaknesses.push('強みが多すぎてラスボスが定まりにくい');

  return {
    stats,
    skills: Object.values(skills),
    titles,
    starStat,
    weaknesses,
  };
}
