import { useEffect } from 'react';
import type { FacilitatorType } from '../data/types';
import { getAxisContent } from '../data/axisContents';
import { getQuadrantKeywords } from '../data/typeKeywords';
import { FormattedText } from './FormattedText';

interface TypeDetailModalProps {
  type: FacilitatorType | null;
  onClose: () => void;
}

/**
 * 診断結果用「あなた」文体を、モーダル用の事実説明「このタイプ」文体に変換する。
 * モーダルを開いた人（未診断含む）が「どんなタイプか」を理解するための表現に揃える。
 */
function toModalDescriptionText(paragraph: string): string {
  return paragraph
    .replace(/あなたには/g, 'このタイプには')
    .replace(/あなたの/g, 'このタイプの')
    .replace(/あなたが/g, 'このタイプが')
    .replace(/あなたを/g, 'このタイプを')
    .replace(/あなたに/g, 'このタイプに')
    .replace(/あなたは/g, 'このタイプは')
    .replace(/あなたも/g, 'このタイプも')
    .replace(/あなたと/g, 'このタイプと')
    .replace(/あなた/g, 'このタイプ');
}

/** タイプ詳細を結果画面風に表示するモーダル（TOP・相性セクションから共通利用） */
export function TypeDetailModal({ type, onClose }: TypeDetailModalProps) {
  useEffect(() => {
    if (!type) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = '';
    };
  }, [type, onClose]);

  if (!type) return null;

  const typeLabels = {
    intervention: getAxisContent('intervention', type.intervention)?.label ?? '',
    perception: getAxisContent('perception', type.perception)?.label ?? '',
    judgment: getAxisContent('judgment', type.judgment)?.label ?? '',
    engagement: getAxisContent('engagement', type.engagement)?.label ?? '',
  };

  const q = getQuadrantKeywords(typeLabels, {
    intervention: type.intervention,
    perception: type.perception,
    judgment: type.judgment,
    engagement: type.engagement,
  });

  const axisColors = {
    intervention: { bg: 'bg-red-50', border: 'border-red-200', axisText: 'text-red-700', labelText: 'text-red-600' },
    perception: { bg: 'bg-emerald-50', border: 'border-emerald-200', axisText: 'text-emerald-700', labelText: 'text-emerald-600' },
    judgment: { bg: 'bg-amber-50', border: 'border-amber-200', axisText: 'text-amber-700', labelText: 'text-amber-600' },
    engagement: { bg: 'bg-sky-50', border: 'border-sky-200', axisText: 'text-sky-700', labelText: 'text-sky-600' },
  } as const;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="type-detail-title"
      onClick={onClose}
    >
      <div
        className="relative bg-white rounded-2xl shadow-xl max-h-[90vh] w-full max-w-2xl overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 白い余白（モーダル最上部）＋閉じるボタンを右上に配置 */}
        <div className="flex shrink-0 items-start justify-end bg-white rounded-t-2xl pr-2 pt-2 min-h-[3rem]">
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-full text-slate-700 hover:bg-slate-200 hover:text-slate-900 transition-colors"
            aria-label="閉じる"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 pb-8">
          {/* ヒーロー（青ヘッダー） */}
          <div className="bg-primary-600 rounded-t-2xl px-6 pt-8 pb-8 mb-6 text-white text-center">
            <h2 id="type-detail-title" className="text-2xl md:text-3xl font-bold mb-3 mt-0">
              {type.name}
            </h2>
            <div className="text-base text-white font-normal mb-4">
              {type.catchcopy.replace(/\*\*/g, '')}
            </div>
            <div className="flex flex-wrap justify-center gap-2 mt-1">
              {[typeLabels.intervention, typeLabels.perception, typeLabels.judgment, typeLabels.engagement].map(
                (label) => (
                  <span
                    key={label}
                    className="inline-block px-3 py-1.5 rounded-full text-xs font-medium bg-white/20 text-white"
                  >
                    {label}
                  </span>
                )
              )}
            </div>
          </div>

          {/* 詳細説明（モーダル用に「あなた」→「このタイプ」で事実説明の文体に変換） */}
          <div className="space-y-4 mb-6">
            {type.detailedDescription.map((paragraph, index) => (
              <p key={index} className="text-slate-600 leading-relaxed text-sm">
                <FormattedText text={toModalDescriptionText(paragraph)} as="span" />
              </p>
            ))}
          </div>

          {/* ファシリテーション特性（型×グループ＋リード文＋4象限） */}
          <div className="mb-6">
            <h3 className="text-center text-sm font-bold text-slate-600 mb-1">ファシリテーション特性</h3>
            {/* 塊と同色：推進者=赤, 共感者=赤薄, 戦略家=青, 守護者=青薄 */}
            <p
              className={`text-center text-base md:text-lg font-bold mb-1 ${
                type.intervention === 'trigger' && type.judgment === 'goal'
                  ? 'text-red-900'
                  : type.intervention === 'trigger' && type.judgment === 'relation'
                    ? 'text-red-800'
                    : type.intervention === 'watch' && type.judgment === 'goal'
                      ? 'text-[#1F86C8]'
                      : 'text-[#38a5d8]'
              }`}
            >
              {type.intervention === 'trigger' ? '触発型ファシリテーター' : '見守型ファシリテーター'} ×{' '}
              {type.intervention === 'trigger' && type.judgment === 'goal'
                ? '推進者グループ'
                : type.intervention === 'trigger' && type.judgment === 'relation'
                  ? '共感者グループ'
                  : type.intervention === 'watch' && type.judgment === 'goal'
                    ? '戦略家グループ'
                    : '守護者グループ'}
            </p>
            <p className="text-center text-sm text-slate-600 mb-4">
              {type.intervention === 'trigger' && type.judgment === 'goal'
                ? '場に積極的に働きかけ、エネルギーを引き出し、場を動かしながら、ゴールに向けて推進する'
                : type.intervention === 'trigger' && type.judgment === 'relation'
                  ? '場に積極的に働きかけ、エネルギーを引き出し、場を盛り上げながら、関係性を育てる'
                  : type.intervention === 'watch' && type.judgment === 'goal'
                    ? '静かに見守り、参加者の主体性を引き出し、裏方として、確実にゴールへ導く'
                    : '静かに見守り、参加者の主体性を引き出し、安心感を与え、関係性を守り育てる'}
            </p>
            <div className="grid grid-cols-2 border border-slate-300">
              {(
                [
                  { key: 'intervention' as const, q: q.intervention },
                  { key: 'perception' as const, q: q.perception },
                  { key: 'judgment' as const, q: q.judgment },
                  { key: 'engagement' as const, q: q.engagement },
                ] as const
              ).map(({ key, q: cell }) => {
                const c = axisColors[key];
                const borderClass =
                  key === 'intervention' ? 'border-b border-r' : key === 'perception' ? 'border-b' : key === 'judgment' ? 'border-r' : '';
                return (
                  <div key={key} className={`${borderClass} border-slate-300 ${c.bg} border-l-4 ${c.border} p-3`}>
                    <div className={`text-sm font-semibold ${c.axisText} mb-2`}>
                      {cell.axisName}：<span className={`font-bold ${c.labelText}`}>{cell.typeLabel}</span>
                    </div>
                    <ul className="text-xs text-slate-600 space-y-0.5 list-none break-words">
                      {cell.keywords.map((kw, i) => (
                        <li key={i}>・{kw}</li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
