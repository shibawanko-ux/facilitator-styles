// 軸の型定義
export type InterventionStyle = 'trigger' | 'watch'; // 触発型 / 見守型
export type PerceptionTarget = 'observe' | 'insight'; // 観察型 / 洞察型
export type JudgmentCriteria = 'goal' | 'relation'; // 目的型 / 関係型
export type EngagementStyle = 'design' | 'improvise'; // 設計型 / 即興型

// 質問の型
export interface Question {
  id: number;
  axis: 'intervention' | 'perception' | 'judgment' | 'engagement';
  text: string;
  optionA: string; // スコア1（A寄り）の選択肢
  optionB: string; // スコア6（B寄り）の選択肢
}

// 回答の型
export interface Answer {
  questionId: number;
  score: number; // 1-6（6段階）
}

// 軸のスコア
export interface AxisScores {
  intervention: number; // 8-48: 低いほど触発型、高いほど見守型
  perception: number;   // 8-48: 低いほど観察型、高いほど洞察型
  judgment: number;     // 8-48: 低いほど目的型、高いほど関係型
  engagement: number;   // 8-48: 低いほど設計型、高いほど即興型
}

// 傾向の型
export interface Tendency {
  axis: string;
  label: string;
  description: string;
}

// 16タイプの型
export interface FacilitatorType {
  id: string;
  name: string;
  catchcopy: string;
  description: string;
  detailedDescription: string[]; // 複数段落の詳細説明
  goodScenes: string[];
  influenceDescription: string; // ファシリテーターとしての影響力（場・参加者への影響を1文で・3-B）
  // 組み合わせ条件
  intervention: InterventionStyle;
  perception: PerceptionTarget;
  judgment: JudgmentCriteria;
  engagement: EngagementStyle;
}

// 強み・弱みの詳細項目
export interface StrengthWeaknessItem {
  title: string;
  description: string;
}

// 軸コンテンツの型
export interface AxisContent {
  axis: string;
  type: string;
  label: string;
  description: string;
  detailedDescription: string; // 詳細説明（段落形式）
  strengths: StrengthWeaknessItem[];
  weaknesses: StrengthWeaknessItem[];
  growthHints: string[];
}

// コーファシリヒントの型
export interface CofaciliHint {
  axis: string;
  type: string;
  label: string;
  asMain: {
    benefit: string;
    focus: string;
  };
  asSub: {
    withSameType: string;
    withOppositeType: string;
  };
}

// 診断結果の型
export interface DiagnosisResult {
  type: FacilitatorType;
  scores: AxisScores;
  tendencies: {
    intervention: AxisContent;
    perception: AxisContent;
    judgment: AxisContent;
    engagement: AxisContent;
  };
  cofaciliHints: {
    intervention: CofaciliHint;
    perception: CofaciliHint;
    judgment: CofaciliHint;
    engagement: CofaciliHint;
  };
}
