import { AxisScores, AxisContent } from '../data/types';
import { getTendencyStrength } from '../utils/scoring';

interface ScoreChartProps {
  scores: AxisScores;
  tendencies: {
    intervention: AxisContent;
    perception: AxisContent;
    judgment: AxisContent;
    engagement: AxisContent;
  };
}

interface AxisBarProps {
  axisName: string;
  score: number;
  leftLabel: string;
  rightLabel: string;
  tendency: AxisContent;
  colorClass: string;
}

function AxisBar({ axisName, score, leftLabel, rightLabel, tendency, colorClass }: AxisBarProps) {
  // スコア8-40を0-100%に変換
  const percentage = ((score - 8) / 32) * 100;
  const strength = getTendencyStrength(score);
  
  // 傾向の方向（左か右か）
  const isLeftTendency = score <= 24;
  
  // パーセンテージ表示用（中央からの偏り）
  const deviationPercentage = Math.abs(50 - percentage);
  
  const colorClasses: Record<string, { fill: string; text: string; lightBg: string }> = {
    primary: {
      fill: 'bg-slate-600',
      text: 'text-slate-700',
      lightBg: 'bg-slate-50',
    },
    accent: {
      fill: 'bg-emerald-500',
      text: 'text-emerald-700',
      lightBg: 'bg-emerald-50',
    },
    blue: {
      fill: 'bg-sky-500',
      text: 'text-sky-700',
      lightBg: 'bg-sky-50',
    },
    green: {
      fill: 'bg-teal-500',
      text: 'text-teal-700',
      lightBg: 'bg-teal-50',
    },
  };
  
  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <div className={`p-5 rounded-xl ${colors.lightBg} mb-4 last:mb-0 border border-gray-100`}>
      {/* 軸名とタイプ */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-xs text-gray-400 uppercase tracking-wider">{axisName}</span>
          <div className="flex items-center gap-2 mt-1">
            <span className={`font-bold text-lg ${colors.text}`}>{tendency.label}</span>
            <span className="text-xs px-2 py-0.5 bg-white rounded-full text-gray-500 border border-gray-100">
              {Math.round(deviationPercentage * 2)}%
            </span>
          </div>
        </div>
        <span className="text-xs text-gray-400 bg-white px-3 py-1 rounded-full border border-gray-100">
          {strength.label}
        </span>
      </div>
      
      {/* スコアバー */}
      <div className="relative mb-3">
        {/* 背景バー */}
        <div className="h-2 rounded-full bg-white border border-gray-100">
          {/* 中央線 */}
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gray-200 z-10" />
          
          {/* カラーバー（傾向の方向に伸びる） */}
          {isLeftTendency ? (
            <div
              className={`absolute top-0 bottom-0 right-1/2 rounded-l-full ${colors.fill}`}
              style={{ width: `${50 - percentage}%` }}
            />
          ) : (
            <div
              className={`absolute top-0 bottom-0 left-1/2 rounded-r-full ${colors.fill}`}
              style={{ width: `${percentage - 50}%` }}
            />
          )}
          
          {/* スコアインジケーター */}
          <div
            className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full ${colors.fill} z-20 border-2 border-white transition-all duration-500`}
            style={{ left: `calc(${percentage}% - 8px)` }}
          />
        </div>
        
        {/* ラベル */}
        <div className="flex justify-between mt-2 text-xs">
          <span className={`font-medium ${!isLeftTendency ? 'text-gray-300' : colors.text}`}>
            {leftLabel}
          </span>
          <span className={`font-medium ${isLeftTendency ? 'text-gray-300' : colors.text}`}>
            {rightLabel}
          </span>
        </div>
      </div>
      
      {/* 簡易説明 */}
      <p className="text-xs text-gray-500 leading-relaxed">
        {tendency.description}
      </p>
    </div>
  );
}

export function ScoreChart({ scores, tendencies }: ScoreChartProps) {
  return (
    <div>
      <AxisBar
        axisName="介入スタイル"
        score={scores.intervention}
        leftLabel="触発型"
        rightLabel="見守型"
        tendency={tendencies.intervention}
        colorClass="primary"
      />
      <AxisBar
        axisName="知覚対象"
        score={scores.perception}
        leftLabel="観察型"
        rightLabel="洞察型"
        tendency={tendencies.perception}
        colorClass="accent"
      />
      <AxisBar
        axisName="判断基準"
        score={scores.judgment}
        leftLabel="目的型"
        rightLabel="関係型"
        tendency={tendencies.judgment}
        colorClass="blue"
      />
      <AxisBar
        axisName="場への関わり"
        score={scores.engagement}
        leftLabel="設計型"
        rightLabel="即興型"
        tendency={tendencies.engagement}
        colorClass="green"
      />
    </div>
  );
}
