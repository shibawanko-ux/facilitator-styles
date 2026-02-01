import { useState } from 'react';
import { DiagnosisResult, FacilitatorType } from '../data/types';
import { ScoreChart } from './ScoreChart';
import { CofaciliSection } from './CofaciliSection';
import { ShareSection } from './ShareSection';
import { TypeDetailModal } from './TypeDetailModal';
import { getCofaciliSummary } from '../data/typeCofaciliSummary';
import { getTypeCompatibility, type CompatibilityItem } from '../data/typeCompatibility';
import { getQuadrantKeywords } from '../data/typeKeywords';
import { getFacilitatorTypeById } from '../data/facilitatorTypes';
import { FormattedText } from './FormattedText';

interface ResultPageProps {
  result: DiagnosisResult;
  onRestart: () => void;
}

export function ResultPage({ result, onRestart }: ResultPageProps) {
  const [selectedCompatType, setSelectedCompatType] = useState<FacilitatorType | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <div className="flex-1 flex flex-col max-w-3xl w-full mx-auto py-12 px-6">
        {/* ヘッダー：ロゴ（TOP・質問画面と統一・次の要素との隙間は控えめ） */}
        <section className="text-center mb-4" aria-label="結果のヘッダー">
          <div className="mb-2">
            <img
              src="/logo.png"
              alt="awareness=design"
              className="h-8 md:h-10 mx-auto object-contain"
            />
          </div>
        </section>
        {/* 結果カード（ヒーロー・詳細・傾向キーワード・得意な場面） */}
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 mb-8" aria-label="診断結果">
          {/* ヒーローセクション：タイプ概要 */}
          <div className="card mb-0 animate-fade-in">
          {/* ヘッダー */}
          <div className="bg-primary-600 -mx-8 -mt-8 px-8 py-10 mb-8 rounded-t-2xl text-white text-center">
            <p className="text-sm text-primary-200 mb-2">あなたのファシリテータースタイルは...</p>
            <h1 className="text-3xl md:text-4xl font-bold mb-3">
              {result.type.name}
            </h1>
            <div className="text-lg text-white font-normal">
              {result.type.catchcopy.replace(/\*\*/g, '')}
            </div>
            {/* 4軸タグ（1-A）：角Rのピル型チップで何型かが一目で分かる */}
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {[
                result.tendencies.intervention.label,
                result.tendencies.perception.label,
                result.tendencies.judgment.label,
                result.tendencies.engagement.label,
              ].map((label) => (
                <span
                  key={label}
                  className="inline-block px-4 py-2 rounded-full text-sm font-medium bg-slate-100 text-slate-700"
                >
                  {label}
                </span>
              ))}
            </div>
          </div>
          
          {/* タイプの詳細説明（複数段落・太字対応） */}
          <div className="space-y-4 mb-8">
            {result.type.detailedDescription.map((paragraph, index) => (
              <p key={index} className="text-slate-600 leading-relaxed">
                <FormattedText text={paragraph} as="span" />
              </p>
            ))}
          </div>

          {/* 傾向キーワード：4象限＋タイプ名（2.8: 重なり解消・階層・軸色） */}
          {(() => {
            const q = getQuadrantKeywords(
              {
                intervention: result.tendencies.intervention.label,
                perception: result.tendencies.perception.label,
                judgment: result.tendencies.judgment.label,
                engagement: result.tendencies.engagement.label,
              },
              {
                intervention: result.type.intervention,
                perception: result.type.perception,
                judgment: result.type.judgment,
                engagement: result.type.engagement,
              }
            );
            // 軸色ルール: 介入=赤, 判断=黄, 知覚=緑, 場の関わり=青
            const axisColors = {
              intervention: { bg: 'bg-red-50', border: 'border-red-200', axisText: 'text-red-700', labelText: 'text-red-600' },
              perception: { bg: 'bg-emerald-50', border: 'border-emerald-200', axisText: 'text-emerald-700', labelText: 'text-emerald-600' },
              judgment: { bg: 'bg-amber-50', border: 'border-amber-200', axisText: 'text-amber-700', labelText: 'text-amber-600' },
              engagement: { bg: 'bg-sky-50', border: 'border-sky-200', axisText: 'text-sky-700', labelText: 'text-sky-600' },
            } as const;
            const Cell = ({
              axisName,
              typeLabel,
              keywords,
              axisKey,
            }: {
              axisName: string;
              typeLabel: string;
              keywords: string[];
              axisKey: keyof typeof axisColors;
            }) => {
              const c = axisColors[axisKey];
              return (
                <div className={`${c.bg} border-l-4 ${c.border} p-3 h-full`}>
                  <div className={`text-sm font-semibold ${c.axisText} mb-2`}>
                    {axisName}：<span className={`font-bold ${c.labelText}`}>{typeLabel}</span>
                  </div>
                  <ul className="text-xs text-slate-600 space-y-0.5 list-none break-words">
                    {keywords.map((kw, i) => (
                      <li key={i}>・{kw}</li>
                    ))}
                  </ul>
                </div>
              );
            };
            // 型の階層：介入スタイル×グループ
            const interventionLabel =
              result.type.intervention === 'trigger' ? '触発型ファシリテーター' : '見守型ファシリテーター';
            const groupLabel =
              result.type.intervention === 'trigger' && result.type.judgment === 'goal'
                ? '推進者グループ'
                : result.type.intervention === 'trigger' && result.type.judgment === 'relation'
                  ? '共感者グループ'
                  : result.type.intervention === 'watch' && result.type.judgment === 'goal'
                    ? '戦略家グループ'
                    : '守護者グループ';
            // 塊と同じフォント色：推進者=赤, 共感者=赤薄, 戦略家=青, 守護者=青薄
            const subtitleColorClass =
              result.type.intervention === 'trigger' && result.type.judgment === 'goal'
                ? 'text-red-900'
                : result.type.intervention === 'trigger' && result.type.judgment === 'relation'
                  ? 'text-red-800'
                  : result.type.intervention === 'watch' && result.type.judgment === 'goal'
                    ? 'text-[#1F86C8]'
                    : 'text-[#38a5d8]';
            // リード文：介入スタイル＋グループの説明を組み合わせ
            const leadText =
              result.type.intervention === 'trigger' && result.type.judgment === 'goal'
                ? '場に積極的に働きかけ、エネルギーを引き出し、場を動かしながら、ゴールに向けて推進する'
                : result.type.intervention === 'trigger' && result.type.judgment === 'relation'
                  ? '場に積極的に働きかけ、エネルギーを引き出し、場を盛り上げながら、関係性を育てる'
                  : result.type.intervention === 'watch' && result.type.judgment === 'goal'
                    ? '静かに見守り、参加者の主体性を引き出し、裏方として、確実にゴールへ導く'
                    : '静かに見守り、参加者の主体性を引き出し、安心感を与え、関係性を守り育てる';

            return (
              <div className="mb-8 max-w-2xl mx-auto">
                {/* タイトル（小さく） */}
                <h3 className="text-center text-sm font-bold text-slate-600 mb-1">あなたのファシリテーション特性</h3>
                {/* サブタイトル：型×グループ（塊と同色） */}
                <p className={`text-center text-base md:text-lg font-bold mb-1 ${subtitleColorClass}`}>
                  {interventionLabel} × {groupLabel}
                </p>
                {/* リード文 */}
                <p className="text-center text-sm text-slate-600 mb-4">{leadText}</p>
                {/* 4象限：2×2グリッド・軸色・罫線 */}
                <div className="grid grid-cols-2 border border-slate-300">
                  <div className="border-b border-r border-slate-300">
                    <Cell axisKey="intervention" axisName={q.intervention.axisName} typeLabel={q.intervention.typeLabel} keywords={q.intervention.keywords} />
                  </div>
                  <div className="border-b border-slate-300">
                    <Cell axisKey="perception" axisName={q.perception.axisName} typeLabel={q.perception.typeLabel} keywords={q.perception.keywords} />
                  </div>
                  <div className="border-r border-slate-300">
                    <Cell axisKey="judgment" axisName={q.judgment.axisName} typeLabel={q.judgment.typeLabel} keywords={q.judgment.keywords} />
                  </div>
                  <div>
                    <Cell axisKey="engagement" axisName={q.engagement.axisName} typeLabel={q.engagement.typeLabel} keywords={q.engagement.keywords} />
                  </div>
                </div>
              </div>
            );
          })()}

          {/* 得意な場面 */}
          <div className="pt-6 border-t border-slate-100">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">得意な場面</h3>
            <div className="flex flex-wrap gap-2">
              {result.type.goodScenes.map((scene, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-slate-50 text-slate-600 rounded-full text-sm border border-slate-100 hover:border-slate-200 transition-colors"
                >
                  {scene}
                </span>
              ))}
            </div>
          </div>
        </div>
        </section>

        {/* ファシリテーター特性セクション：4軸のスコア */}
        <div className="card mb-10 animate-fade-in-up">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-slate-100">
              <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-800">ファシリテーター特性</h2>
              <p className="text-sm text-slate-500">4つの軸であなたのファシリテーター傾向を分析</p>
            </div>
          </div>
          <ScoreChart scores={result.scores} tendencies={result.tendencies} />
        </div>

        {/* 強み・弱みセクション */}
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          {/* 強み */}
          <div className="card animate-fade-in-up animate-stagger-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="icon-square bg-emerald-100">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-slate-800">強み</h2>
            </div>
            <div className="space-y-3">
              {[
                result.tendencies.intervention,
                result.tendencies.perception,
                result.tendencies.judgment,
                result.tendencies.engagement,
              ].map((tendency, tendencyIndex) => (
                <div key={tendencyIndex} className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                  <h4 className="font-medium text-slate-800 text-sm">
                    {tendency.strengths[0].title}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1">
                    {tendency.strengths[0].description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* 弱み */}
          <div className="card animate-fade-in-up animate-stagger-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="icon-square bg-amber-100">
                <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-slate-800">注意点</h2>
            </div>
            <div className="space-y-3">
              {[
                result.tendencies.intervention,
                result.tendencies.perception,
                result.tendencies.judgment,
                result.tendencies.engagement,
              ].map((tendency, tendencyIndex) => (
                <div key={tendencyIndex} className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                  <h4 className="font-medium text-slate-800 text-sm">
                    {tendency.weaknesses[0].title}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1">
                    {tendency.weaknesses[0].description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ファシリテーターとしての影響力（3-B） */}
        <div className="card mb-10 animate-fade-in-up animate-stagger-3">
          <div className="flex items-center gap-4 mb-6">
            <div className="icon-square bg-sky-100">
              <svg className="w-5 h-5 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-800">ファシリテーターとしての影響力</h2>
              <p className="text-sm text-slate-500">場や参加者にあなたが与える影響</p>
            </div>
          </div>
          <FormattedText
            text={result.type.influenceDescription}
            className="text-slate-600 leading-relaxed"
          />
        </div>

        {/* コーファシリヒント（4-A, 4-C） */}
        <div className="card mb-10 animate-fade-in-up animate-stagger-4">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-violet-100">
              <svg className="w-5 h-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-800">コーファシリとの組み合わせヒント</h2>
              <p className="text-sm text-slate-500">他のファシリテーターとの協力方法</p>
            </div>
          </div>
          <CofaciliSection
            typeId={result.type.id}
            summary={getCofaciliSummary(result.type.id)}
          />
        </div>

        {/* 他のスタイルとの相性（独立項目・4-C） */}
        {(() => {
          const compatibility = getTypeCompatibility(result.type.id);
          if (!compatibility || (compatibility.good.length === 0 && compatibility.difficult.length === 0)) return null;
          return (
            <div className="card mb-10 animate-fade-in-up animate-stagger-5">
              <div className="flex items-center gap-4 mb-8">
                <div className="icon-square bg-amber-100">
                  <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-800">他のスタイルとの相性</h2>
                  <p className="text-sm text-slate-500">相性が良いスタイル・難しいスタイルと振る舞いのヒント</p>
                </div>
              </div>
              <div className="space-y-6">
                {compatibility.good.length > 0 && (
                  <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                    <h3 className="text-sm font-semibold text-emerald-800 mb-4">相性が良いスタイル</h3>
                    <div className="space-y-4">
                      {compatibility.good.map((item: CompatibilityItem) => (
                        <button
                          key={item.typeId}
                          type="button"
                          onClick={() => setSelectedCompatType(getFacilitatorTypeById(item.typeId) ?? null)}
                          className="w-full text-left p-3 bg-white rounded-xl border border-emerald-100 hover:border-emerald-200 hover:shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1"
                        >
                          <p className="font-bold text-emerald-800 text-base">{item.typeName}</p>
                          <p className="text-sm text-slate-600 mt-1 leading-relaxed">{item.hint}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {compatibility.difficult.length > 0 && (
                  <div className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                    <h3 className="text-sm font-semibold text-amber-800 mb-4">難しいかもという相性</h3>
                    <div className="space-y-4">
                      {compatibility.difficult.map((item: CompatibilityItem) => (
                        <button
                          key={item.typeId}
                          type="button"
                          onClick={() => setSelectedCompatType(getFacilitatorTypeById(item.typeId) ?? null)}
                          className="w-full text-left p-3 bg-white rounded-xl border border-amber-100 hover:border-amber-200 hover:shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-1"
                        >
                          <p className="font-bold text-amber-800 text-base">{item.typeName}</p>
                          <p className="text-sm text-slate-600 mt-1 leading-relaxed">{item.hint}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })()}

        {/* 相性タイプ詳細モーダル */}
        <TypeDetailModal
          type={selectedCompatType}
          onClose={() => setSelectedCompatType(null)}
        />

        {/* シェア・保存セクション（09_sns_share_requirements 準拠） */}
        <section id="share-section" className="card mb-10" aria-label="結果をシェア・保存">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-rose-100">
              <svg className="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-800">結果をシェア・保存</h2>
              <p className="text-sm text-slate-500">SNSでシェアまたは画像で保存</p>
            </div>
          </div>
          <ShareSection result={result} />
        </section>

        {/* awareness=design 導線カード（TOP と同内容・シェアとの隙間は他セクション同様 mb-10 のみ） */}
        <div className="w-full">
          <a
            href="https://awareness-design.studio.site/"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex flex-col sm:flex-row items-stretch sm:items-center gap-4 p-5 rounded-2xl border border-slate-200 bg-white shadow-sm hover:border-slate-300 hover:shadow-md transition-all duration-300 text-left no-underline focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            aria-label="awareness=design のサイトへ"
          >
            <div className="min-w-0 flex-1">
              <h3 className="font-bold text-slate-800 text-lg">awareness=design</h3>
              <p className="text-sm text-slate-600 mt-1 leading-relaxed">
                awareness=designは、対話を通じて、チームや家族といった身近な関係性に気づきと変化が生まれる場をデザインしています。
              </p>
              <p className="text-xs text-slate-500 mt-1 font-medium">awareness-design.studio.site</p>
            </div>
            <div className="flex-shrink-0 flex items-center justify-center">
              <img
                src="/awareness_design_sc.png"
                alt="awareness=design"
                className="h-20 sm:h-24 w-auto object-contain"
              />
            </div>
          </a>
        </div>

        {/* もう一度診断する（視認性のためプライマリ・やや大きめ） */}
        <div className="text-center mt-10">
          <button
            onClick={onRestart}
            className="btn-primary text-lg font-bold py-5 px-10"
          >
            もう一度診断する
          </button>
        </div>
      </div>

      {/* フッター（TOP・Question と統一・全幅） */}
      <footer className="mt-auto px-6 py-10 text-center bg-white border-t border-slate-200">
        <a
          href="https://awareness-design.studio.site/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-600 no-underline hover:no-underline focus:no-underline"
        >
          awareness=design
        </a>
        <p className="mt-2 text-xs text-slate-400">
          ファシリテーション研究を参考にした診断です。
        </p>
      </footer>
    </div>
  );
}
