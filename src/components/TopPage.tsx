import { useState } from 'react';
import { facilitatorTypes } from '../data/facilitatorTypes';
import { FacilitatorType } from '../data/types';
import { TypeDetailModal } from './TypeDetailModal';

interface TopPageProps {
  onStart: () => void;
}

// タイプカードコンポーネント（クリックで詳細モーダル表示）
function TypeCard({
  type,
  colorClass,
  onClick,
}: {
  type: FacilitatorType;
  colorClass: string;
  onClick: () => void;
}) {
  // 案D改3: 塊の色の同系統で2グループ濃淡。触発型=深い赤系統、見守型=添付参照の青系統。
  const colorClasses: Record<string, { bg: string; border: string; text: string; iconBg: string }> = {
    primary: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-900', iconBg: 'bg-red-900' },   // 推進者（深い赤・濃いめ）
    accent: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', iconBg: 'bg-red-800' },   // 共感者（深い赤・薄め）
    blue: { bg: 'bg-[#F0F8FF]', border: 'border-[#B8D4E8]', text: 'text-[#1e3a8a]', iconBg: 'bg-[#1F86C8]' },   // 戦略家（参照青・濃いめ）
    green: { bg: 'bg-[#F0F8FF]', border: 'border-[#B8D4E8]', text: 'text-[#1e3a8a]', iconBg: 'bg-[#38a5d8]' },  // 守護者（参照青・薄め）
  };

  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border ${colors.border} ${colors.bg} hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg ${colors.iconBg} flex items-center justify-center flex-shrink-0`}>
          <span className="text-white font-bold text-sm">
            {type.name.charAt(0)}
          </span>
        </div>
        <div className="min-w-0">
          <h4 className={`font-bold ${colors.text} text-sm`}>{type.name}</h4>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{type.catchcopy.replace(/\*\*/g, '')}</p>
        </div>
      </div>
    </button>
  );
}

// タイプカテゴリコンポーネント
function TypeCategory({
  title,
  description,
  types,
  colorClass,
  onTypeClick,
}: {
  title: string;
  description: string;
  types: FacilitatorType[];
  colorClass: string;
  onTypeClick: (type: FacilitatorType) => void;
}) {
  // 案D改3: 塊の色の同系統で2グループ濃淡。触発型=深い赤、見守型=添付参照の青（#1F86C8）。
  const colorClasses: Record<string, { headerBg: string; headerText: string; accent: string }> = {
    primary: { headerBg: 'bg-red-900', headerText: 'text-white', accent: 'text-red-200' },   // 推進者（深い赤・濃いめ）
    accent: { headerBg: 'bg-red-800', headerText: 'text-white', accent: 'text-red-200' },   // 共感者（深い赤・薄め）
    blue: { headerBg: 'bg-[#1F86C8]', headerText: 'text-white', accent: 'text-blue-200' },   // 戦略家（参照青・濃いめ）
    green: { headerBg: 'bg-[#38a5d8]', headerText: 'text-white', accent: 'text-blue-200' },  // 守護者（参照青・薄め）
  };

  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <div className="mb-6 animate-fade-in-up">
      <div className={`${colors.headerBg} rounded-t-2xl px-6 py-4`}>
        <h3 className={`font-bold ${colors.headerText}`}>{title}</h3>
        <p className={`text-sm ${colors.accent}`}>{description}</p>
      </div>
      <div className="bg-white rounded-b-2xl border border-t-0 border-gray-100 p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {types.map((type) => (
            <TypeCard
              key={type.id}
              type={type}
              colorClass={colorClass}
              onClick={() => onTypeClick(type)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export function TopPage({ onStart }: TopPageProps) {
  const [selectedType, setSelectedType] = useState<FacilitatorType | null>(null);

  // タイプをカテゴリ別に分類
  const triggerGoalTypes = facilitatorTypes.filter(
    t => t.intervention === 'trigger' && t.judgment === 'goal'
  );
  const triggerRelationTypes = facilitatorTypes.filter(
    t => t.intervention === 'trigger' && t.judgment === 'relation'
  );
  const watchGoalTypes = facilitatorTypes.filter(
    t => t.intervention === 'watch' && t.judgment === 'goal'
  );
  const watchRelationTypes = facilitatorTypes.filter(
    t => t.intervention === 'watch' && t.judgment === 'relation'
  );

  return (
    <div className="min-h-screen bg-white">
      {/* ヒーローセクション */}
      <div className="section flex flex-col items-center justify-center px-6">
        <div className="max-w-2xl w-full text-center animate-fade-in">
          {/* ロゴ・タイトル */}
          <div className="mb-12">
            <img 
              src="/logo.png" 
              alt="awareness=design" 
              className="h-5 md:h-6 mx-auto mb-6 object-contain"
            />
            <img
              src="/logo_facilitatorstyles.png"
              alt="FacilitatorStyles"
              className="h-32 md:h-40 mx-auto mb-4 object-contain"
            />
            <p className="text-lg text-gray-500">
              ファシリテーター特性診断
            </p>
          </div>

          {/* 説明 */}
          <div className="card mb-10 text-left">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 text-center">
              あなたのファシリテーションスタイルを発見しよう
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              32の質問に答えることで、あなたのファシリテーターとしての傾向が分かります。
              4つの軸であなたのスタイルを可視化し、強みや成長のヒントをお伝えします。
            </p>

            {/* Step1: 診断で測る4つの軸（軸色: 介入=赤, 知覚=緑, 判断=黄, 場の関わり=青） */}
            <p className="text-sm font-medium text-gray-700 mb-3 text-center">診断で測定する4つの軸</p>
            <p className="text-xs text-gray-600 leading-relaxed mb-4 text-center">
              32問で以下の4つの軸を測定します。これらの組み合わせから16スタイルに判定されます。
            </p>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-red-50 rounded-xl border border-red-100 hover:border-red-200 transition-colors">
                <p className="text-sm font-medium text-red-700">介入スタイル</p>
                <p className="text-xs text-red-500 mt-1">触発型 ⇔ 見守型</p>
                <p className="text-xs text-red-600/80 mt-2">場に自分から働きかけるか、相手を受け止めるか</p>
              </div>
              <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 hover:border-emerald-200 transition-colors">
                <p className="text-sm font-medium text-emerald-700">知覚対象</p>
                <p className="text-xs text-emerald-500 mt-1">観察型 ⇔ 洞察型</p>
                <p className="text-xs text-emerald-600/80 mt-2">言葉・事実を拾うか、空気・感情を読むか</p>
              </div>
              <div className="p-4 bg-amber-50 rounded-xl border border-amber-100 hover:border-amber-200 transition-colors">
                <p className="text-sm font-medium text-amber-700">判断基準</p>
                <p className="text-xs text-amber-500 mt-1">目的型 ⇔ 関係型</p>
                <p className="text-xs text-amber-600/80 mt-2">ゴール達成を優先するか、納得感・関係性を優先するか</p>
              </div>
              <div className="p-4 bg-sky-50 rounded-xl border border-sky-100 hover:border-sky-200 transition-colors">
                <p className="text-sm font-medium text-sky-700">場への関わり</p>
                <p className="text-xs text-sky-500 mt-1">設計型 ⇔ 即興型</p>
                <p className="text-xs text-sky-600/80 mt-2">計画通りに進めるか、その場で柔軟に変えるか</p>
              </div>
            </div>

            <p className="text-sm text-gray-400 text-center">
              所要時間：約5分
            </p>
          </div>

          {/* スタートボタン */}
          <button
            onClick={onStart}
            className="btn-primary text-lg"
          >
            診断を始める
          </button>
          <p className="mt-6 text-xs text-gray-600 text-center font-bold">
            スタイルはあくまで得意としている傾向であり、どの視点もバランスよく持つことが重要だと考えています。
          </p>
          <p className="mt-3 text-xs text-gray-400">
            ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
          </p>
        </div>
      </div>

      {/* ファシリテーター16スタイル一覧セクション */}
      <div className="section px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="section-title">
              ファシリテーター16スタイル
            </h2>
            <p className="section-subtitle">
              4つの軸の組み合わせによって分類されます
            </p>
          </div>

          {/* 触発型グループ */}
          <div className="mb-16">
            <div className="flex items-center gap-4 mb-8">
              <div className="icon-circle bg-red-900">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">触発型ファシリテーター</h3>
                <p className="text-sm text-gray-500">場に積極的に働きかけ、エネルギーを引き出す</p>
              </div>
            </div>

            <TypeCategory
              title="推進者グループ"
              description="場を動かしながら、ゴールに向けて推進する"
              types={triggerGoalTypes}
              colorClass="primary"
              onTypeClick={setSelectedType}
            />

            <TypeCategory
              title="共感者グループ"
              description="場を盛り上げながら、関係性を育てる"
              types={triggerRelationTypes}
              colorClass="accent"
              onTypeClick={setSelectedType}
            />
          </div>

          {/* 見守型グループ */}
          <div>
            <div className="flex items-center gap-4 mb-8">
              <div className="icon-circle bg-[#1F86C8]">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">見守型ファシリテーター</h3>
                <p className="text-sm text-gray-500">静かに見守り、参加者の主体性を引き出す</p>
              </div>
            </div>

            <TypeCategory
              title="戦略家グループ"
              description="裏方として、確実にゴールへ導く"
              types={watchGoalTypes}
              colorClass="blue"
              onTypeClick={setSelectedType}
            />

            <TypeCategory
              title="守護者グループ"
              description="安心感を与え、関係性を守り育てる"
              types={watchRelationTypes}
              colorClass="green"
              onTypeClick={setSelectedType}
            />
          </div>

          {/* もう一度診断ボタン */}
          <div className="text-center mt-16">
            <button
              onClick={onStart}
              className="btn-primary text-lg"
            >
              診断を始める
            </button>
            <p className="mt-6 text-xs text-gray-600 text-center font-bold">
              スタイルはあくまで得意としている傾向であり、どの視点もバランスよく持つことが重要だと考えています。
            </p>
            <p className="mt-3 text-xs text-gray-400">
              ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
            </p>
          </div>
        </div>
      </div>

      {/* タイプ詳細モーダル */}
      <TypeDetailModal type={selectedType} onClose={() => setSelectedType(null)} />

      {/* フッター */}
      <div className="px-6 py-8 text-center bg-white border-t border-gray-100">
        <a
          href="https://awareness-design.studio.site/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-600 no-underline hover:no-underline focus:no-underline"
        >
          awareness=design
        </a>
        <p className="mt-2 text-xs text-gray-400">
          ファシリテーション研究を参考にした診断です。
        </p>
      </div>
    </div>
  );
}
