/**
 * 軸別傾向キーワード（各型4文×4軸＝16文）
 * 結果画面で4象限（介入スタイル・知覚対象・判断基準・場の関わり）＋中央にタイプ名を表示（2.7 採用）
 * 各軸の型に応じた強み文章を axisContents の strengths からそのまま使用（エンパワメント用）
 */

import { getAxisContent } from './axisContents';

const AXIS_NAMES: Record<string, string> = {
  intervention: '介入スタイル',
  perception: '知覚対象',
  judgment: '判断基準',
  engagement: '場の関わり',
};

const AXIS_KEYS = ['intervention', 'perception', 'judgment', 'engagement'] as const;

export interface QuadrantKeywords {
  axisName: string;
  typeLabel: string;
  keywords: string[]; // 強みタイトル（4つ、axisContents の strengths[].title をそのまま）
}

export interface QuadrantData {
  intervention: QuadrantKeywords;
  perception: QuadrantKeywords;
  judgment: QuadrantKeywords;
  engagement: QuadrantKeywords;
}

/** 軸＋型から強みタイトル4つを取得（axisContents の strengths をそのまま使用） */
function getStrengthTitles(axis: string, typeValue: string): string[] {
  const content = getAxisContent(axis, typeValue);
  if (!content?.strengths?.length) return [];
  return content.strengths.slice(0, 4).map((s) => s.title);
}

/** 診断結果から4象限の強み文章（各4文）を取得 */
export function getQuadrantKeywords(
  typeLabels: {
    intervention: string;
    perception: string;
    judgment: string;
    engagement: string;
  },
  typeValues: {
    intervention: 'trigger' | 'watch';
    perception: 'observe' | 'insight';
    judgment: 'goal' | 'relation';
    engagement: 'design' | 'improvise';
  }
): QuadrantData {
  const axes = AXIS_KEYS;
  const result: QuadrantData = {} as QuadrantData;
  axes.forEach((axis) => {
    const typeVal = typeValues[axis];
    result[axis] = {
      axisName: AXIS_NAMES[axis],
      typeLabel: typeLabels[axis],
      keywords: getStrengthTitles(axis, typeVal),
    };
  });
  return result;
}

/** 旧API互換：タイプIDから24語を返す（未使用時は空配列） */
export function getTypeKeywords(_typeId: string): string[] {
  return [];
}
