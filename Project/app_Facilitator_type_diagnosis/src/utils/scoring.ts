import { Answer, AxisScores, DiagnosisResult, InterventionStyle, PerceptionTarget, JudgmentCriteria, EngagementStyle } from '../data/types';
import { questions } from '../data/questions';
import { determineType } from '../data/facilitatorTypes';
import { getAxisContent } from '../data/axisContents';
import { getCofaciliHint } from '../data/cofaciliHints';

// 軸ごとのスコアを計算
export function calculateAxisScores(answers: Answer[]): AxisScores {
  const scores: AxisScores = {
    intervention: 0,
    perception: 0,
    judgment: 0,
    engagement: 0,
  };

  answers.forEach((answer) => {
    const question = questions.find((q) => q.id === answer.questionId);
    if (question) {
      scores[question.axis] += answer.score;
    }
  });

  return scores;
}

// スコアから傾向を判定（中央28・6段階）
// 8-48の範囲、中央は28。27以下: A寄り、28以上: B寄り
export function getTendencyType(score: number, axis: string): string {
  if (score <= 27) {
    // A寄り
    switch (axis) {
      case 'intervention': return 'trigger';
      case 'perception': return 'observe';
      case 'judgment': return 'goal';
      case 'engagement': return 'design';
      default: return '';
    }
  } else {
    // B寄り
    switch (axis) {
      case 'intervention': return 'watch';
      case 'perception': return 'insight';
      case 'judgment': return 'relation';
      case 'engagement': return 'improvise';
      default: return '';
    }
  }
}

// 傾向の強さを取得（パーセンテージ）
export function getTendencyStrength(score: number): { percentage: number; label: string } {
  // 8-48のスコア、中央28からの距離を0-100%に変換
  const distance = Math.abs(score - 28);
  const maxDistance = 20; // 8から28、または48から28
  const percentage = Math.round((distance / maxDistance) * 100);
  
  if (distance <= 3) {
    return { percentage, label: 'バランス型' };
  } else if (distance <= 8) {
    return { percentage, label: 'やや傾向あり' };
  } else {
    return { percentage, label: '強い傾向' };
  }
}

// スコアから傾向のラベルを取得
export function getTendencyLabel(score: number, axis: string): string {
  const type = getTendencyType(score, axis);
  const content = getAxisContent(axis, type);
  const strength = getTendencyStrength(score);
  
  if (content) {
    if (strength.label === 'バランス型') {
      return `${content.label}・バランス型`;
    }
    return content.label;
  }
  return '';
}

// 診断結果を生成
export function generateDiagnosisResult(answers: Answer[]): DiagnosisResult | null {
  const scores = calculateAxisScores(answers);
  
  // 各軸の傾向を判定
  const interventionType = getTendencyType(scores.intervention, 'intervention') as InterventionStyle;
  const perceptionType = getTendencyType(scores.perception, 'perception') as PerceptionTarget;
  const judgmentType = getTendencyType(scores.judgment, 'judgment') as JudgmentCriteria;
  const engagementType = getTendencyType(scores.engagement, 'engagement') as EngagementStyle;
  
  // タイプを判定
  const type = determineType(interventionType, perceptionType, judgmentType, engagementType);
  
  if (!type) {
    return null;
  }
  
  // 各軸のコンテンツを取得
  const interventionContent = getAxisContent('intervention', interventionType);
  const perceptionContent = getAxisContent('perception', perceptionType);
  const judgmentContent = getAxisContent('judgment', judgmentType);
  const engagementContent = getAxisContent('engagement', engagementType);
  
  // コーファシリヒントを取得
  const interventionHint = getCofaciliHint('intervention', interventionType);
  const perceptionHint = getCofaciliHint('perception', perceptionType);
  const judgmentHint = getCofaciliHint('judgment', judgmentType);
  const engagementHint = getCofaciliHint('engagement', engagementType);
  
  if (!interventionContent || !perceptionContent || !judgmentContent || !engagementContent) {
    return null;
  }
  
  if (!interventionHint || !perceptionHint || !judgmentHint || !engagementHint) {
    return null;
  }
  
  return {
    type,
    scores,
    tendencies: {
      intervention: interventionContent,
      perception: perceptionContent,
      judgment: judgmentContent,
      engagement: engagementContent,
    },
    cofaciliHints: {
      intervention: interventionHint,
      perception: perceptionHint,
      judgment: judgmentHint,
      engagement: engagementHint,
    },
  };
}
