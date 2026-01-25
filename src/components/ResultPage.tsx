import { useRef } from 'react';
import { DiagnosisResult } from '../data/types';
import { ScoreChart } from './ScoreChart';
import { AxisDetail } from './AxisDetail';
import { CofaciliSection } from './CofaciliSection';
import { ShareSection } from './ShareSection';

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
            <p className="text-lg text-primary-100">
              {result.type.catchcopy}
            </p>
          </div>
          
          {/* タイプの詳細説明（複数段落） */}
          <div className="space-y-4 mb-8">
            {result.type.detailedDescription.map((paragraph, index) => (
              <p key={index} className="text-gray-600 leading-relaxed">
                {paragraph}
              </p>
            ))}
          </div>
          
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

        {/* 性格特性セクション：4軸のスコア */}
        <div className="card mb-10 animate-fade-in-up">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-slate-100">
              <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">性格特性</h2>
              <p className="text-sm text-gray-500">4つの軸であなたの傾向を分析</p>
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

        {/* 各軸の詳細 */}
        <div className="card mb-10 animate-fade-in-up animate-stagger-3">
          <div className="flex items-center gap-4 mb-8">
            <div className="icon-square bg-sky-100">
              <svg className="w-5 h-5 text-sky-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">各軸の詳細分析</h2>
              <p className="text-sm text-gray-500">クリックして詳細を確認</p>
            </div>
          </div>
          <div className="space-y-4">
            <AxisDetail
              axisName="介入スタイル"
              content={result.tendencies.intervention}
              score={result.scores.intervention}
              colorClass="primary"
            />
            <AxisDetail
              axisName="知覚対象"
              content={result.tendencies.perception}
              score={result.scores.perception}
              colorClass="accent"
            />
            <AxisDetail
              axisName="判断基準"
              content={result.tendencies.judgment}
              score={result.scores.judgment}
              colorClass="blue"
            />
            <AxisDetail
              axisName="場への関わり"
              content={result.tendencies.engagement}
              score={result.scores.engagement}
              colorClass="green"
            />
          </div>
        </div>

        {/* コーファシリヒント */}
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
          <CofaciliSection hints={result.cofaciliHints} />
        </div>

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
