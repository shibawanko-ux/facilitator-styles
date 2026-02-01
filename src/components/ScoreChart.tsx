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
  // スコア8-48を0-100%に変換。0%=左端、50%=中央、100%=右端
  const percentage = ((score - 8) / 40) * 100;
  const strength = getTendencyStrength(score);
  
  // 傾向の方向（左か右か）。中央28でA/Bを分ける
  const isLeftTendency = score <= 27;
  // 表示用％：中心を0%として「該当の型に○%寄っている」（中心から端までが0→100%）
  const displayPercent = isLeftTendency
    ? Math.round(((50 - percentage) / 50) * 100)
    : Math.round(((percentage - 50) / 50) * 100);
  
  // 軸色: 介入=赤, 判断=黄, 知覚=緑, 場の関わり=青
  const colorClasses: Record<string, { fill: string; text: string; lightBg: string }> = {
    red: {
      fill: 'bg-red-500',
      text: 'text-red-700',
      lightBg: 'bg-red-50',
    },
    accent: {
      fill: 'bg-emerald-500',
      text: 'text-emerald-700',
      lightBg: 'bg-emerald-50',
    },
    amber: {
      fill: 'bg-amber-500',
      text: 'text-amber-700',
      lightBg: 'bg-amber-50',
    },
    blue: {
      fill: 'bg-sky-500',
      text: 'text-sky-700',
      lightBg: 'bg-sky-50',
    },
  };
  
  const colors = colorClasses[colorClass] || colorClasses.red;

  return (
    <div className={`p-5 rounded-xl ${colors.lightBg} mb-4 last:mb-0 border border-slate-100`}>
      {/* 1. スコアバーを上に（添付画像準拠：バー→タイトル→リード文） */}
      <div className="relative mb-2">
        <div className="h-2.5 rounded-full bg-slate-200 border border-slate-100 w-full relative">
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-300 z-10 -translate-x-px" />
          <div
            className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 rounded-full ${colors.fill} z-20 border-2 border-white shadow transition-all duration-500`}
            style={{ left: `calc(${percentage}% - 10px)` }}
          />
        </div>
        <div className="flex justify-between mt-1.5 text-xs">
          <span className={`font-medium ${!isLeftTendency ? 'text-slate-300' : colors.text}`}>
            {leftLabel}
          </span>
          <span className={`font-medium ${isLeftTendency ? 'text-slate-300' : colors.text}`}>
            {rightLabel}
          </span>
        </div>
      </div>

      {/* 2. 直下にタイトル行（軸名: XX% 〇〇型）・余白を詰める */}
      <div className="flex justify-between items-center mb-1">
        <p className="text-base font-semibold text-slate-800 leading-tight">
          <span className="text-slate-600">{axisName}: </span>
          <span className={`font-bold text-lg ${colors.text}`}>{displayPercent}%</span>
          <span className={`font-semibold ml-1 ${colors.text}`}>{tendency.label}</span>
        </p>
        <span className="text-xs text-slate-400 bg-white px-2.5 py-0.5 rounded-full border border-slate-100 shrink-0">
          {strength.label}
        </span>
      </div>

      {/* 3. 直下にリード文（タイトルと近づけて一まとまりに） */}
      <p className="text-sm text-slate-600 leading-relaxed">
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
        colorClass="red"
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
        colorClass="amber"
      />
      <AxisBar
        axisName="場への関わり"
        score={scores.engagement}
        leftLabel="設計型"
        rightLabel="即興型"
        tendency={tendencies.engagement}
        colorClass="blue"
      />
    </div>
  );
}
