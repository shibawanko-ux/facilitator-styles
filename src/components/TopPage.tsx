import { facilitatorTypes } from '../data/facilitatorTypes';
import { FacilitatorType } from '../data/types';

interface TopPageProps {
  onStart: () => void;
}

// タイプカードコンポーネント
function TypeCard({ type, colorClass }: { type: FacilitatorType; colorClass: string }) {
  const colorClasses: Record<string, { bg: string; border: string; text: string; iconBg: string }> = {
    primary: {
      bg: 'bg-slate-50',
      border: 'border-slate-200',
      text: 'text-slate-700',
      iconBg: 'bg-slate-600',
    },
    accent: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-700',
      iconBg: 'bg-emerald-600',
    },
    blue: {
      bg: 'bg-sky-50',
      border: 'border-sky-200',
      text: 'text-sky-700',
      iconBg: 'bg-sky-600',
    },
    green: {
      bg: 'bg-teal-50',
      border: 'border-teal-200',
      text: 'text-teal-700',
      iconBg: 'bg-teal-600',
    },
  };

  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <div className={`p-4 rounded-xl border ${colors.border} ${colors.bg} hover:shadow-md hover:-translate-y-0.5 transition-all duration-300`}>
      <div className="flex items-start gap-3">
        <div className={`w-10 h-10 rounded-lg ${colors.iconBg} flex items-center justify-center flex-shrink-0`}>
          <span className="text-white font-bold text-sm">
            {type.name.charAt(0)}
          </span>
        </div>
        <div className="min-w-0">
          <h4 className={`font-bold ${colors.text} text-sm`}>{type.name}</h4>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{type.catchcopy}</p>
        </div>
      </div>
    </div>
  );
}

// タイプカテゴリコンポーネント
function TypeCategory({ 
  title, 
  description, 
  types, 
  colorClass 
}: { 
  title: string; 
  description: string; 
  types: FacilitatorType[]; 
  colorClass: string;
}) {
  const colorClasses: Record<string, { headerBg: string; headerText: string; accent: string }> = {
    primary: { headerBg: 'bg-slate-700', headerText: 'text-white', accent: 'text-slate-300' },
    accent: { headerBg: 'bg-emerald-600', headerText: 'text-white', accent: 'text-emerald-200' },
    blue: { headerBg: 'bg-sky-600', headerText: 'text-white', accent: 'text-sky-200' },
    green: { headerBg: 'bg-teal-600', headerText: 'text-white', accent: 'text-teal-200' },
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
            <TypeCard key={type.id} type={type} colorClass={colorClass} />
          ))}
        </div>
      </div>
    </div>
  );
}

export function TopPage({ onStart }: TopPageProps) {
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
              className="h-8 md:h-10 mx-auto mb-6 object-contain"
            />
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-gray-800">
              FacilitatorStyles
            </h1>
            <p className="text-lg text-gray-500">
              ファシリテーター診断
            </p>
          </div>

          {/* 説明 */}
          <div className="card mb-10 text-left">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              あなたのファシリテーションスタイルを発見しよう
            </h2>
            <p className="text-gray-600 mb-8 leading-relaxed">
              32の質問に答えることで、あなたのファシリテーターとしての傾向が分かります。
              4つの軸であなたのスタイルを可視化し、強みや成長のヒントをお伝えします。
            </p>
            
            {/* 4軸の説明 */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-slate-200 transition-colors">
                <p className="text-sm font-medium text-slate-700">介入スタイル</p>
                <p className="text-xs text-slate-500 mt-1">触発型 ⇔ 見守型</p>
              </div>
              <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 hover:border-emerald-200 transition-colors">
                <p className="text-sm font-medium text-emerald-700">知覚対象</p>
                <p className="text-xs text-emerald-500 mt-1">観察型 ⇔ 洞察型</p>
              </div>
              <div className="p-4 bg-sky-50 rounded-xl border border-sky-100 hover:border-sky-200 transition-colors">
                <p className="text-sm font-medium text-sky-700">判断基準</p>
                <p className="text-xs text-sky-500 mt-1">目的型 ⇔ 関係型</p>
              </div>
              <div className="p-4 bg-teal-50 rounded-xl border border-teal-100 hover:border-teal-200 transition-colors">
                <p className="text-sm font-medium text-teal-700">場への関わり</p>
                <p className="text-xs text-teal-500 mt-1">設計型 ⇔ 即興型</p>
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
          <p className="mt-6 text-xs text-gray-400">
            ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
          </p>
        </div>
      </div>

      {/* 16タイプ一覧セクション */}
      <div className="section px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="section-title">
              ファシリテータータイプ
            </h2>
            <p className="section-subtitle">
              4つの軸の組み合わせによって分類されます
            </p>
          </div>

          {/* 触発型グループ */}
          <div className="mb-16">
            <div className="flex items-center gap-4 mb-8">
              <div className="icon-circle bg-slate-700">
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
            />

            <TypeCategory
              title="共感者グループ"
              description="場を盛り上げながら、関係性を育てる"
              types={triggerRelationTypes}
              colorClass="accent"
            />
          </div>

          {/* 見守型グループ */}
          <div>
            <div className="flex items-center gap-4 mb-8">
              <div className="icon-circle bg-teal-600">
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
            />

            <TypeCategory
              title="守護者グループ"
              description="安心感を与え、関係性を守り育てる"
              types={watchRelationTypes}
              colorClass="green"
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
            <p className="mt-6 text-xs text-gray-400">
              ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
            </p>
          </div>
        </div>
      </div>

      {/* フッター */}
      <div className="px-6 py-8 text-center bg-white border-t border-gray-100">
      </div>
    </div>
  );
}
