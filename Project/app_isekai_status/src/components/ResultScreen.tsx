import { useEffect, useState } from 'react';
import type { StatusResult, Stats } from '../logic/types';
import StarField from './StarField';

interface Props {
  result: StatusResult;
  onRetry: () => void;
}

const STAT_LABELS: { key: keyof Stats; label: string; abbr: string; category: string }[] = [
  { key: 'hp',  label: '生命力',   abbr: 'HP',  category: '生命系' },
  { key: 'mp',  label: '精神力',   abbr: 'MP',  category: '生命系' },
  { key: 'sp',  label: '行動力',   abbr: 'SP',  category: '生命系' },
  { key: 'str', label: '筋　力',   abbr: 'STR', category: 'フィジカル系' },
  { key: 'agi', label: '俊　敏',   abbr: 'AGI', category: 'フィジカル系' },
  { key: 'vit', label: '耐　久',   abbr: 'VIT', category: 'フィジカル系' },
  { key: 'def', label: '防　御',   abbr: 'DEF', category: 'フィジカル系' },
  { key: 'int', label: '知　力',   abbr: 'INT', category: '知性系' },
  { key: 'wis', label: '洞　察',   abbr: 'WIS', category: '知性系' },
  { key: 'mnd', label: '精神力',   abbr: 'MND', category: '知性系' },
  { key: 'cha', label: 'カリスマ', abbr: 'CHA', category: '対人系' },
  { key: 'emp', label: '共　感',   abbr: 'EMP', category: '対人系' },
  { key: 'ngt', label: '交　渉',   abbr: 'NGT', category: '対人系' },
  { key: 'ldr', label: '統　率',   abbr: 'LDR', category: '対人系' },
  { key: 'tec', label: '技　術',   abbr: 'TEC', category: '技術・創造系' },
  { key: 'cre', label: '創　造',   abbr: 'CRE', category: '技術・創造系' },
  { key: 'ana', label: '分　析',   abbr: 'ANA', category: '技術・創造系' },
  { key: 'stz', label: '構造化',   abbr: 'STZ', category: '技術・創造系' },
  { key: 'luk', label: '運',       abbr: 'LUK', category: 'その他' },
  { key: 'foc', label: '集　中',   abbr: 'FOC', category: 'その他' },
  { key: 'adp', label: '適　応',   abbr: 'ADP', category: 'その他' },
];

const CATEGORY_COLORS: Record<string, { label: string; bar: string; border: string }> = {
  '生命系':       { label: 'text-emerald-400', bar: 'from-emerald-700 to-emerald-400', border: 'border-emerald-500/30' },
  'フィジカル系': { label: 'text-orange-400',  bar: 'from-orange-700  to-orange-400',  border: 'border-orange-500/30'  },
  '知性系':       { label: 'text-cyan-400',    bar: 'from-cyan-700    to-cyan-400',    border: 'border-cyan-500/30'    },
  '対人系':       { label: 'text-pink-400',    bar: 'from-pink-700    to-pink-400',    border: 'border-pink-500/30'    },
  '技術・創造系': { label: 'text-violet-400',  bar: 'from-violet-700  to-violet-400',  border: 'border-violet-500/30'  },
  'その他':       { label: 'text-slate-400',   bar: 'from-slate-600   to-slate-400',   border: 'border-slate-500/30'   },
};

function StatBar({ value, category, isStar, delay }: { value: number; category: string; isStar: boolean; delay: number }) {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setWidth(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  const colors = CATEGORY_COLORS[category];
  return (
    <div className="flex-1 h-2.5 bg-indigo-900/50 rounded-full overflow-hidden border border-indigo-800/40">
      <div
        className={`h-full rounded-full bg-gradient-to-r ${colors.bar} transition-all duration-700 ease-out ${isStar ? 'shadow-md shadow-yellow-400/50' : ''}`}
        style={{ width: `${width}%` }}
      />
    </div>
  );
}

function StatCategory({ cat, stats, starStat, baseDelay }: {
  cat: string; stats: Stats; starStat: keyof Stats; baseDelay: number;
}) {
  const catStats = STAT_LABELS.filter((s) => s.category === cat);
  const colors = CATEGORY_COLORS[cat];
  return (
    <div className={`border rounded-xl bg-slate-900/70 backdrop-blur-sm overflow-hidden ${colors.border}`}>
      <div className={`px-4 py-2 border-b ${colors.border}`}>
        <span className={`text-xs font-bold tracking-wider ${colors.label}`}>■ {cat}</span>
      </div>
      <div className="px-4 py-3 space-y-2">
        {catStats.map((s, i) => {
          const val = stats[s.key];
          const isStar = s.key === starStat;
          return (
            <div key={s.key} className="flex items-center gap-2 animate-slide-in" style={{ animationDelay: `${baseDelay + i * 60}ms` }}>
              <span className="text-indigo-400 text-xs w-7 shrink-0 font-mono">{s.abbr}</span>
              <span className="text-indigo-200 text-xs w-12 shrink-0">{s.label}</span>
              <span className={`text-sm font-black w-9 shrink-0 tabular-nums ${isStar ? 'text-yellow-300' : 'text-white'}`}>
                {val}{isStar && <span className="text-yellow-400 text-xs ml-0.5">★</span>}
              </span>
              <StatBar value={val} category={cat} isStar={isStar} delay={baseDelay + i * 60} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function ResultScreen({ result, onRetry }: Props) {
  const { stats, skills, titles, starStat, weaknesses } = result;
  const categories = ['生命系', 'フィジカル系', '知性系', '対人系', '技術・創造系', 'その他'];

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-slate-950 via-indigo-950 to-slate-950 py-8 px-4">
      <StarField />

      <div className="relative z-10 max-w-5xl mx-auto animate-fade-in">

        {/* ヘッダー */}
        <div className="border-2 border-yellow-400/60 rounded-xl bg-slate-900/80 backdrop-blur-sm shadow-xl shadow-yellow-400/10 mb-4 overflow-hidden animate-glow-pulse">
          <div className="bg-gradient-to-r from-yellow-900/60 to-indigo-900/60 px-5 py-2.5 border-b border-yellow-500/30">
            <span className="text-yellow-400 text-sm font-bold tracking-wider">⚔ STATUS WINDOW</span>
          </div>
          <div className="px-5 py-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full border-2 border-yellow-400 bg-indigo-900/60 flex items-center justify-center text-2xl shrink-0 animate-float">
                ⚔️
              </div>
              <div className="flex-1">
                <p className="text-indigo-300 text-xs mb-1">クラス：場の設計師 ／ 橋渡しの賢者</p>
                <div className="flex items-center gap-3">
                  <span className="text-yellow-300 font-black text-2xl">Lv. 73</span>
                  <span className="text-slate-400 text-sm">/ 999</span>
                </div>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {titles.map((t) => (
                <span key={t} className="text-xs bg-indigo-800/60 border border-indigo-500/40 text-indigo-300 px-2 py-0.5 rounded-full">
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* メインコンテンツ：PC = 2カラム / SP = 1カラム */}
        <div className="md:grid md:grid-cols-2 md:gap-4">

          {/* 左カラム：ステータス */}
          <div className="space-y-3">
            <p className="text-indigo-400 text-xs font-bold tracking-widest px-1">◆ ステータス</p>
            {categories.map((cat, ci) => (
              <StatCategory
                key={cat}
                cat={cat}
                stats={stats}
                starStat={starStat}
                baseDelay={ci * 80}
              />
            ))}
          </div>

          {/* 右カラム：スキル・固有スキル・弱点・役割 */}
          <div className="space-y-3 mt-3 md:mt-0">
            <p className="text-indigo-400 text-xs font-bold tracking-widest px-1">◆ スキル・詳細</p>

            {/* スキル */}
            <div className="border border-purple-700/40 rounded-xl bg-slate-900/70 backdrop-blur-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-purple-700/30">
                <span className="text-purple-400 text-xs font-bold tracking-wider">■ スキル</span>
              </div>
              <div className="px-4 py-3 space-y-2.5">
                {skills.map((skill) => (
                  <div key={skill.name} className="flex items-start gap-3">
                    <span className={`shrink-0 text-xs font-black px-2 py-0.5 rounded mt-0.5 ${skill.isMax ? 'bg-yellow-400 text-slate-900' : 'bg-indigo-800 text-indigo-300'}`}>
                      Lv.{skill.level}
                    </span>
                    <div>
                      <span className={`text-sm font-bold leading-tight ${skill.isMax ? 'text-yellow-300' : 'text-white'}`}>
                        [{skill.name}]{skill.isMax ? ' ★MAX' : ''}
                      </span>
                      <p className="text-indigo-400 text-xs mt-0.5 leading-relaxed">{skill.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 固有スキル */}
            <div className="border-2 border-purple-500/50 rounded-xl bg-purple-900/20 backdrop-blur-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-purple-500/30">
                <span className="text-purple-300 text-xs font-bold tracking-wider">★ 固有スキル（レア・パッシブ）</span>
              </div>
              <div className="px-4 py-4">
                <p className="text-purple-200 font-black text-base mb-1">【個が場をつくる】</p>
                <p className="text-purple-300 text-sm leading-relaxed">人を動かすのではなく、動きたくなる場をつくる</p>
                <div className="mt-2 space-y-0.5">
                  <p className="text-purple-400 text-xs">発動条件：チーム・組織・授業・WS全般</p>
                  <p className="text-purple-400 text-xs">副次効果：周囲のLvが自然と上がる</p>
                </div>
              </div>
            </div>

            {/* 弱点 */}
            <div className="border border-red-700/40 rounded-xl bg-slate-900/70 backdrop-blur-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-red-700/30">
                <span className="text-red-400 text-xs font-bold tracking-wider">■ 弱 点</span>
              </div>
              <div className="px-4 py-3 space-y-1.5">
                {weaknesses.map((w) => (
                  <p key={w} className="text-red-300 text-xs leading-relaxed">✗ {w}</p>
                ))}
              </div>
            </div>

            {/* パーティ役割 */}
            <div className="border border-yellow-600/40 rounded-xl bg-yellow-900/10 backdrop-blur-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-yellow-700/30">
                <span className="text-yellow-400 text-xs font-bold tracking-wider">■ パーティ内役割</span>
              </div>
              <div className="px-4 py-4 text-center">
                <p className="text-yellow-300 font-bold text-sm mb-1">後衛支援 ／ 場の設計 ／ 参謀</p>
                <p className="text-yellow-200/70 text-xs">「一人より、パーティがいると無双するタイプ」</p>
              </div>
            </div>

            {/* もう一度ボタン（PCではここに） */}
            <button
              type="button"
              onClick={onRetry}
              className="hidden md:block w-full py-4 rounded-xl font-bold text-base bg-gradient-to-r from-indigo-600 to-indigo-700 text-white hover:from-indigo-500 hover:to-indigo-600 hover:scale-[1.02] transition-all duration-200 shadow-lg"
            >
              🔄 もう一度診断する
            </button>
          </div>
        </div>

        {/* もう一度ボタン（SPではここに） */}
        <button
          type="button"
          onClick={onRetry}
          className="md:hidden w-full mt-4 py-4 rounded-xl font-bold text-base bg-gradient-to-r from-indigo-600 to-indigo-700 text-white hover:from-indigo-500 hover:to-indigo-600 transition-all duration-200 shadow-lg"
        >
          🔄 もう一度診断する
        </button>
      </div>
    </div>
  );
}
