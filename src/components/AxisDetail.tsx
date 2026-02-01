import { useState } from 'react';
import { AxisContent } from '../data/types';
import { getTendencyStrength } from '../utils/scoring';

interface AxisDetailProps {
  axisName: string;
  content: AxisContent;
  score: number;
  colorClass: string;
}

export function AxisDetail({ axisName, content, score, colorClass }: AxisDetailProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const strength = getTendencyStrength(score);

  const colorClasses: Record<string, { bg: string; border: string; text: string; lightBg: string; iconBg: string }> = {
    primary: {
      bg: 'bg-slate-600',
      border: 'border-slate-200',
      text: 'text-slate-700',
      lightBg: 'bg-slate-50',
      iconBg: 'bg-slate-600',
    },
    accent: {
      bg: 'bg-emerald-500',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
      lightBg: 'bg-emerald-50',
      iconBg: 'bg-emerald-500',
    },
    blue: {
      bg: 'bg-sky-500',
      border: 'border-sky-200',
      text: 'text-sky-700',
      lightBg: 'bg-sky-50',
      iconBg: 'bg-sky-500',
    },
    green: {
      bg: 'bg-teal-500',
      border: 'border-teal-200',
      text: 'text-teal-700',
      lightBg: 'bg-teal-50',
      iconBg: 'bg-teal-500',
    },
  };

  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <div className={`border rounded-2xl ${colors.border} overflow-hidden transition-all duration-300 ${isExpanded ? 'shadow-sm' : ''}`}>
      {/* ヘッダー（クリックで展開） */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full p-5 ${colors.lightBg} flex items-center justify-between transition-all hover:opacity-90`}
      >
        <div className="flex items-center gap-4">
          <div className={`w-11 h-11 rounded-xl ${colors.iconBg} flex items-center justify-center`}>
            <span className="text-white font-bold text-lg">
              {content.label.charAt(0)}
            </span>
          </div>
          <div className="text-left">
            <span className="text-xs text-slate-400 uppercase tracking-wider">{axisName}</span>
            <h3 className={`font-bold text-lg ${colors.text}`}>
              {content.label}
            </h3>
            <span className="text-xs text-slate-400">
              {strength.label}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400 hidden sm:block">
            {isExpanded ? '閉じる' : '詳細を見る'}
          </span>
          <svg
            className={`w-5 h-5 text-slate-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* コンテンツ（展開時） */}
      {isExpanded && (
        <div className="p-6 bg-white animate-fade-in">
          {/* 詳細説明 */}
          <div className="mb-8">
            <p className="text-slate-600 leading-relaxed">
              {content.detailedDescription}
            </p>
          </div>

          {/* 強み */}
          <div className="mb-8">
            <h4 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
              強み
            </h4>
            <div className="grid gap-3">
              {content.strengths.map((item, index) => (
                <div key={index} className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                  <h5 className="font-medium text-slate-700 mb-1">{item.title}</h5>
                  <p className="text-sm text-slate-500">{item.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 弱み・注意点 */}
          <div className="mb-8">
            <h4 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              注意点
            </h4>
            <div className="grid gap-3">
              {content.weaknesses.map((item, index) => (
                <div key={index} className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                  <h5 className="font-medium text-slate-700 mb-1">{item.title}</h5>
                  <p className="text-sm text-slate-500">{item.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 成長のヒント */}
          <div>
            <h4 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-sky-100 flex items-center justify-center">
                <svg className="w-4 h-4 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </span>
              成長のヒント
            </h4>
            <div className="p-4 bg-sky-50 rounded-xl border border-sky-100">
              <ul className="space-y-2">
                {content.growthHints.map((item, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="text-sky-500 font-medium mt-0.5">→</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
