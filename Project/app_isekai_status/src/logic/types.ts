export type Answer = 'A' | 'B' | 'C' | 'D';

export interface Answers {
  q1: Answer;
  q2: Answer;
  q3: Answer;
  q4: Answer;
  q5: Answer;
  q6: Answer;
}

export interface Stats {
  // 生命系
  hp: number;
  mp: number;
  sp: number;
  // フィジカル系
  str: number;
  agi: number;
  vit: number;
  def: number;
  // 知性系
  int: number;
  wis: number;
  mnd: number;
  // 対人系
  cha: number;
  emp: number;
  ngt: number;
  ldr: number;
  // 技術・創造系
  tec: number;
  cre: number;
  ana: number;
  stz: number;
  // その他
  luk: number;
  foc: number;
  adp: number;
}

export interface SkillLevel {
  name: string;
  level: number;
  description: string;
  isMax?: boolean;
}

export interface StatusResult {
  stats: Stats;
  skills: SkillLevel[];
  titles: string[];
  starStat: keyof Stats;
  weaknesses: string[];
}
