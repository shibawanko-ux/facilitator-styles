import { useState, useEffect } from 'react';
import { facilitatorTypes } from '../data/facilitatorTypes';
import { FacilitatorType } from '../data/types';
import { TypeDetailModal } from './TypeDetailModal';
import { getResultTypeId } from '../utils/resultCookie';

interface TopPageProps {
  onStart: () => void;
}

// タイプカードコンポーネント（クリックで詳細モーダル表示）。自分の結果のカードにのみ✓表示。
function TypeCard({
  type,
  colorClass,
  isCurrentResult,
  onClick,
}: {
  type: FacilitatorType;
  colorClass: string;
  isCurrentResult: boolean;
  onClick: () => void;
}) {
  const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
    primary: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-900' },
    accent: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800' },
    blue: { bg: 'bg-[#F0F8FF]', border: 'border-[#B8D4E8]', text: 'text-[#1e3a8a]' },
    green: { bg: 'bg-[#F0F8FF]', border: 'border-[#B8D4E8]', text: 'text-[#1e3a8a]' },
  };

  const colors = colorClasses[colorClass] || colorClasses.primary;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border ${colors.border} ${colors.bg} hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 flex items-start gap-3`}
    >
      {/* キャラクターイラスト円形。自分の結果は緑チェックをオーバーレイ */}
      <div className="w-14 h-14 flex-shrink-0 relative" aria-hidden="true">
        <div className="w-14 h-14 rounded-full overflow-hidden border-2 border-slate-200">
          {type.illustration ? (
            <img
              src={type.illustration}
              alt=""
              className="w-full h-full object-cover object-top"
            />
          ) : (
            <span className="w-full h-full block bg-slate-50" />
          )}
        </div>
        {isCurrentResult && (
          <span className="absolute inset-0 flex items-center justify-center rounded-full bg-emerald-600/80" aria-label="診断結果">
            <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </span>
        )}
      </div>
      <div className="min-w-0 flex-1">
        <h4 className={`font-bold ${colors.text} text-base leading-snug`}>{type.name}</h4>
        <p className="text-sm text-slate-500 mt-1">{type.catchcopy.replace(/\*\*/g, '')}</p>
      </div>
      <span className={`flex items-center self-stretch flex-shrink-0 text-xl font-bold ${colors.text}`} aria-hidden="true">›</span>
    </button>
  );
}

// タイプカテゴリコンポーネント
function TypeCategory({
  title,
  description,
  types,
  colorClass,
  currentResultTypeId,
  onTypeClick,
}: {
  title: string;
  description: string;
  types: FacilitatorType[];
  colorClass: string;
  currentResultTypeId: string | null;
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
                <h3 className="font-bold text-white">{title}</h3>
        <p className={`text-sm ${colors.accent}`}>{description}</p>
      </div>
      <div className="bg-white rounded-b-2xl border border-t-0 border-slate-200 p-4 shadow-sm">
        <div className="grid grid-cols-1 gap-3">
          {types.map((type) => (
            <TypeCard
              key={type.id}
              type={type}
              colorClass={colorClass}
              isCurrentResult={currentResultTypeId === type.id}
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
  const [currentResultTypeId, setCurrentResultTypeId] = useState<string | null>(null);

  // TOP表示時：クッキーから診断結果のスタイルIDを読み取り
  useEffect(() => {
    setCurrentResultTypeId(getResultTypeId());
  }, []);

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
      {/* ヒーローセクション：上イラスト＋下テキスト縦積み */}
      <section aria-label="診断のご案内">
        {/* イラストエリア：全面配置・枠なし */}
        <div className="w-full bg-white overflow-hidden max-h-80 md:max-h-[600px]">
          <img
            src="/hero_illustration.png"
            alt=""
            className="w-full object-cover object-top max-h-80 md:max-h-[600px]"
            aria-hidden="true"
          />
        </div>

        {/* テキストエリア */}
        <div className="bg-white px-6 pt-1 pb-8 text-center animate-fade-in">
          {/* ロゴ */}
          <div className="flex flex-col items-center gap-3 mb-6 mt-2">
            <img
              src="/logo_facilitatorstyles.png"
              alt="Facilitator Styles"
              className="w-[260px] h-[100px] object-contain"
            />
            <img
              src="/logo_powered_by_awareness_design.png"
              alt="Powered by awareness=design"
              className="w-[180px] h-[22px] object-contain"
            />
          </div>

          <p className="text-base text-slate-500 mb-2">ファシリテーター特性診断</p>
          <p className="text-sm text-slate-500 leading-relaxed mb-6 max-w-sm mx-auto">
            32の質問に答えて、あなたのファシリテーションスタイルを発見しよう
          </p>

          {/* スタートボタン */}
          <button
            type="button"
            onClick={onStart}
            className="btn-primary text-lg md:w-[280px]"
          >
            診断を始める
          </button>
          <p className="mt-6 text-xs text-slate-600 text-center font-bold max-w-sm mx-auto">
            スタイルはあくまで得意としている傾向であり、どの視点もバランスよく持つことが重要だと考えています。
          </p>
          <p className="mt-3 text-xs text-slate-500">
            ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
          </p>
        </div>

      </section>

      {/* 4軸説明セクション */}
      <section className="px-6 py-12 bg-[#f8fafc]" aria-label="診断で測定する4つの軸">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold text-slate-800 text-center mb-2">
            あなたのファシリテーションスタイルを発見しよう
          </h2>
          <p className="text-sm text-slate-500 leading-relaxed mb-6 text-center">
            32の質問に答えることで、あなたのファシリテーターとしての傾向が分かります。
            4つの軸であなたのスタイルを可視化し、強みや成長のヒントをお伝えします。
          </p>
          <h3 className="text-sm font-bold text-slate-700 mb-2 text-center">診断で測定する4つの軸</h3>
          <p className="text-xs text-slate-600 leading-relaxed mb-5 text-center">
            32問で以下の4つの軸を測定します。これらの組み合わせから16スタイルに判定されます。
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-red-50 rounded-xl border border-red-100">
              <p className="text-sm font-medium text-red-700">介入スタイル</p>
              <p className="text-xs text-red-500 mt-1">触発型 ⇔ 見守型</p>
              <p className="text-xs text-red-600/80 mt-2">場に自分から働きかけるか、相手を受け止めるか</p>
            </div>
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
              <p className="text-sm font-medium text-emerald-700">知覚対象</p>
              <p className="text-xs text-emerald-500 mt-1">観察型 ⇔ 洞察型</p>
              <p className="text-xs text-emerald-600/80 mt-2">言葉・事実を拾うか、空気・感情を読むか</p>
            </div>
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-100">
              <p className="text-sm font-medium text-amber-700">判断基準</p>
              <p className="text-xs text-amber-500 mt-1">目的型 ⇔ 関係型</p>
              <p className="text-xs text-amber-600/80 mt-2">ゴール達成を優先するか、納得感・関係性を優先するか</p>
            </div>
            <div className="p-4 bg-sky-50 rounded-xl border border-sky-100">
              <p className="text-sm font-medium text-sky-700">場への関わり</p>
              <p className="text-xs text-sky-500 mt-1">設計型 ⇔ 即興型</p>
              <p className="text-xs text-sky-600/80 mt-2">計画通りに進めるか、その場で柔軟に変えるか</p>
            </div>
          </div>
          <p className="text-sm text-slate-400 text-center mt-6">所要時間：約5分</p>
          <div className="text-center mt-8">
            <button
              type="button"
              onClick={onStart}
              className="btn-primary text-lg md:w-[280px]"
            >
              診断を始める
            </button>
          </div>
        </div>
      </section>

      {/* awareness=design ブランド導線セクション */}
      <section className="px-6 py-12 bg-[#e0f2fe]" aria-label="提供元について">
        <div className="max-w-2xl mx-auto">
          <a
            href="https://awareness-design.studio.site/"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex flex-col sm:flex-row items-stretch sm:items-center gap-4 p-5 rounded-2xl border border-sky-200 bg-white shadow-sm hover:border-sky-300 hover:shadow-md transition-all duration-300 text-left no-underline focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
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
      </section>

      {/* ファシリテーター16スタイル一覧セクション */}
      <section className="section px-6 bg-[#f0f9ff]" aria-label="16スタイル一覧">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">16 styles</p>
            <h2 className="section-title">
              ファシリテーター16スタイル
            </h2>
            <p className="section-subtitle mt-3">
              4つの軸の組み合わせによって分類されます
            </p>
          </div>

          {/* 触発型グループ（赤系統で視認性・ブロックの一貫性） */}
          <div className="mb-16">
            <div className="mb-8">
              <h3 className="text-xl font-bold text-red-900">触発型ファシリテーター</h3>
              <p className="text-sm text-red-700">場に積極的に働きかけ、エネルギーを引き出す</p>
            </div>

            <div className="md:grid md:grid-cols-2 md:gap-6">
              <TypeCategory
                title="推進者グループ"
                description="場を動かしながら、ゴールに向けて推進する"
                types={triggerGoalTypes}
                colorClass="primary"
                currentResultTypeId={currentResultTypeId}
                onTypeClick={setSelectedType}
              />

              <TypeCategory
                title="共感者グループ"
                description="場を盛り上げながら、関係性を育てる"
                types={triggerRelationTypes}
                colorClass="accent"
                currentResultTypeId={currentResultTypeId}
                onTypeClick={setSelectedType}
              />
            </div>
          </div>

          {/* 見守型グループ（青系統で視認性・ブロックの一貫性） */}
          <div>
            <div className="mb-8">
              <h3 className="text-xl font-bold text-[#1F86C8]">見守型ファシリテーター</h3>
              <p className="text-sm text-[#1e3a8a]">静かに見守り、参加者の主体性を引き出す</p>
            </div>

            <div className="md:grid md:grid-cols-2 md:gap-6">
              <TypeCategory
                title="戦略家グループ"
                description="裏方として、確実にゴールへ導く"
                types={watchGoalTypes}
                colorClass="blue"
                currentResultTypeId={currentResultTypeId}
                onTypeClick={setSelectedType}
              />

              <TypeCategory
                title="守護者グループ"
                description="安心感を与え、関係性を守り育てる"
                types={watchRelationTypes}
                colorClass="green"
                currentResultTypeId={currentResultTypeId}
                onTypeClick={setSelectedType}
              />
            </div>
          </div>

          {/* もう一度診断ボタン */}
          <div className="text-center mt-16">
            <button
              type="button"
              onClick={onStart}
              className="btn-primary text-lg md:w-[280px]"
            >
              診断を始める
            </button>
            <p className="mt-6 text-xs text-slate-600 text-center font-bold">
              スタイルはあくまで得意としている傾向であり、どの視点もバランスよく持つことが重要だと考えています。
            </p>
            <p className="mt-3 text-xs text-slate-400">
              ※この診断は自己理解のためのツールです。結果は参考情報としてご活用ください。
            </p>
          </div>
        </div>
      </section>

      {/* タイプ詳細モーダル */}
      <TypeDetailModal type={selectedType} onClose={() => setSelectedType(null)} />

      {/* フッター */}
      <footer className="px-6 py-10 text-center bg-[#e0f2fe] border-t border-sky-200">
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
