import { useRef } from 'react';
import { DiagnosisResult } from '../data/types';
import { ScoreChart } from './ScoreChart';
import { CofaciliSection } from './CofaciliSection';
import { ShareSection } from './ShareSection';
import { getCofaciliSummary } from '../data/typeCofaciliSummary';
import { getTypeCompatibility } from '../data/typeCompatibility';
import { getQuadrantKeywords } from '../data/typeKeywords';
import { FormattedText } from './FormattedText';

interface ResultPageProps {
  result: DiagnosisResult;
  onRestart: () => void;
}

export function ResultPage({ result, onRestart }: ResultPageProps) {
  const resultRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen bg-white py-12 px-6">
      <div className="max-w-3xl mx-auto">
        {/* ヒーローセクション：タイプ概要 */}
        <div ref={resultRef} className="card mb-10 animate-fade-in">
          {/* ヘッダー */}
          <div className="bg-primary-700 -mx-8 -mt-8 px-8 py-10 mb-8 rounded-t-2xl text-white text-center">
            <p className="text-sm text-primary-200 mb-2">あなたのファシリテータータイプは...</p>
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
                  className="inline-block px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-700"
                >
                  {label}
                </span>
              ))}
            </div>
          </div>
          
          {/* タイプの詳細説明（複数段落・太字対応） */}
          <div className="space-y-4 mb-8">
            {result.type.detailedDescription.map((paragraph, index) => (
              <p key={index} className="text-gray-600 leading-relaxed">
                <FormattedText text={paragraph} as="span" />
              </p>
            ))}
          </div>

          {/* 傾向キーワード：4象限に強み文章（axisContents の strengths をそのまま）＋中央にタイプ名（2.7 採用） */}
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
            const Cell = ({
              axisName,
              typeLabel,
              keywords,
            }: {
              axisName: string;
              typeLabel: string;
              keywords: string[];
            }) => (
              <div className="bg-white border border-gray-300 p-2">
                <div className="text-xs font-semibold text-gray-500 mb-0.5">{axisName}</div>
                <div className="text-xs font-medium text-gray-700 mb-1">{typeLabel}</div>
                <ul className="text-xs text-gray-600 space-y-0.5 list-none break-words">
                  {keywords.map((kw, i) => (
                    <li key={i}>{kw}</li>
                  ))}
                </ul>
              </div>
            );
            return (
              <div className="mb-8 max-w-2xl mx-auto">
                <table className="w-full border-collapse border border-gray-300" style={{ tableLayout: 'fixed' }}>
                  <tbody>
                    <tr>
                      <td className="w-1/3 align-top border border-gray-300 p-0">
                        <Cell axisName={q.intervention.axisName} typeLabel={q.intervention.typeLabel} keywords={q.intervention.keywords} />
                      </td>
                      <td rowSpan={2} className="w-1/3 align-middle text-center border border-gray-300 bg-primary-50 p-4">
                        <span className="text-sm font-bold text-primary-800">{result.type.name}</span>
                      </td>
                      <td className="w-1/3 align-top border border-gray-300 p-0">
                        <Cell axisName={q.perception.axisName} typeLabel={q.perception.typeLabel} keywords={q.perception.keywords} />
                      </td>
                    </tr>
                    <tr>
                      <td className="align-top border border-gray-300 p-0">
                        <Cell axisName={q.judgment.axisName} typeLabel={q.judgment.typeLabel} keywords={q.judgment.keywords} />
                      </td>
                      <td className="align-top border border-gray-300 p-0">
                        <Cell axisName={q.engagement.axisName} typeLabel={q.engagement.typeLabel} keywords={q.engagement.keywords} />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            );
          })()}

          {/* 得意な場面 */}
          <div className="pt-6 border-t border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">得意な場面</h3>
            <div className="flex flex-wrap gap-2">
              {result.type.goodScenes.map((scene, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-gray-50 text-gray-600 rounded-full text-sm border border-gray-100 hover:border-gray-200 transition-colors"
                >
                  {scene}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* ファシリテーター特性セクション：4軸のスコア */}
        <div className="card mb-10 animate-fade-in-up">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-slate-100">
              <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">ファシリテーター特性</h2>
              <p className="text-sm text-gray-500">4つの軸であなたのファシリテーター傾向を分析</p>
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
              <h2 className="text-xl font-semibold text-gray-800">強み</h2>
            </div>
            <div className="space-y-3">
              {[
                result.tendencies.intervention,
                result.tendencies.perception,
                result.tendencies.judgment,
                result.tendencies.engagement,
              ].map((tendency, tendencyIndex) => (
                <div key={tendencyIndex} className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                  <h4 className="font-medium text-gray-800 text-sm">
                    {tendency.strengths[0].title}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
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
              <h2 className="text-xl font-semibold text-gray-800">注意点</h2>
            </div>
            <div className="space-y-3">
              {[
                result.tendencies.intervention,
                result.tendencies.perception,
                result.tendencies.judgment,
                result.tendencies.engagement,
              ].map((tendency, tendencyIndex) => (
                <div key={tendencyIndex} className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                  <h4 className="font-medium text-gray-800 text-sm">
                    {tendency.weaknesses[0].title}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
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
              <h2 className="text-xl font-semibold text-gray-800">ファシリテーターとしての影響力</h2>
              <p className="text-sm text-gray-500">場や参加者にあなたが与える影響</p>
            </div>
          </div>
          <FormattedText
            text={result.type.influenceDescription}
            className="text-gray-600 leading-relaxed"
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
              <h2 className="text-xl font-semibold text-gray-800">コーファシリとの組み合わせヒント</h2>
              <p className="text-sm text-gray-500">他のファシリテーターとの協力方法</p>
            </div>
          </div>
          <CofaciliSection
            typeId={result.type.id}
            summary={getCofaciliSummary(result.type.id)}
          />
        </div>

        {/* 他のタイプとの相性（独立項目・4-C） */}
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
                  <h2 className="text-xl font-semibold text-gray-800">他のタイプとの相性</h2>
                  <p className="text-sm text-gray-500">相性が良いタイプ・難しいタイプと振る舞いのヒント</p>
                </div>
              </div>
              <div className="space-y-6">
                {compatibility.good.length > 0 && (
                  <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                    <h3 className="text-sm font-semibold text-emerald-800 mb-3">相性が良いタイプ</h3>
                    <ul className="space-y-3">
                      {compatibility.good.map((item) => (
                        <li key={item.typeId} className="text-sm">
                          <span className="font-medium text-emerald-800">{item.typeName}</span>
                          <p className="text-gray-600 mt-1">{item.hint}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {compatibility.difficult.length > 0 && (
                  <div className="p-4 bg-amber-50 rounded-xl border border-amber-100">
                    <h3 className="text-sm font-semibold text-amber-800 mb-3">難しいかもという相性</h3>
                    <ul className="space-y-3">
                      {compatibility.difficult.map((item) => (
                        <li key={item.typeId} className="text-sm">
                          <span className="font-medium text-amber-800">{item.typeName}</span>
                          <p className="text-gray-600 mt-1">{item.hint}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })()}

        {/* シェア・保存セクション */}
        <div className="card mb-10">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-rose-100">
              <svg className="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">結果をシェア・保存</h2>
              <p className="text-sm text-gray-500">SNSでシェアまたは画像で保存</p>
            </div>
          </div>
          <ShareSection result={result} resultRef={resultRef} />
        </div>

        {/* もう一度診断する */}
        <div className="text-center">
          <button
            onClick={onRestart}
            className="btn-secondary"
          >
            もう一度診断する
          </button>
        </div>
      </div>
    </div>
  );
}
