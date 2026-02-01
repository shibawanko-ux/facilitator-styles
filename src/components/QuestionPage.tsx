import { Question, Answer } from '../data/types';

interface QuestionPageProps {
  question: Question;
  currentIndex: number;
  totalQuestions: number;
  currentAnswer?: Answer;
  progress: number;
  onAnswer: (score: number) => void;
  onNext: () => void;
  onPrev: () => void;
}

const scaleLabels = [
  { score: 1, label: 'とてもAに近い' },
  { score: 2, label: 'ややAに近い' },
  { score: 3, label: 'どちらかといえばA' },
  { score: 4, label: 'どちらかといえばB' },
  { score: 5, label: 'ややBに近い' },
  { score: 6, label: 'とてもBに近い' },
];

export function QuestionPage({
  question,
  currentIndex,
  totalQuestions,
  currentAnswer,
  progress,
  onAnswer,
  onNext,
  onPrev,
}: QuestionPageProps) {
  const handleSelect = (score: number) => {
    onAnswer(score);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* ヘッダー・プログレス（Q-PROGRESS-01: sticky で常時視認可能） */}
      <section
        className="sticky top-0 z-10 px-6 pt-8 pb-4 bg-white border-b border-slate-200 shadow-sm"
        aria-label="進捗"
      >
        <div className="max-w-2xl w-full mx-auto">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-slate-400 font-medium">
            質問 {currentIndex + 1} / {totalQuestions}
          </span>
          <span className="text-sm text-slate-400 font-medium">
            {progress}%
          </span>
        </div>
        <div className="score-bar">
          <div
            className="score-bar-fill bg-primary-600"
            style={{ width: `${progress}%` }}
          />
        </div>
        </div>
      </section>

      {/* 質問カード */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-8 max-w-2xl mx-auto w-full animate-fade-in" aria-label="質問">
        <div className="card w-full mb-10">
          {/* 質問文 */}
          <h2 className="text-xl md:text-2xl font-semibold text-slate-800 mb-10 text-center leading-relaxed">
            {question.text}
          </h2>

          {/* 選択肢の両極（A＝赤・B＝青）。アイコン・文字は中央寄せ。中央に隙間を入れてA/Bエリアを明確に */}
          <div className="flex gap-6 md:gap-8 mb-8 text-sm">
            <div className="flex-1 min-w-0 flex flex-col items-center text-center">
              <span className="inline-block px-3 py-1 rounded-full font-semibold text-xs bg-red-100 text-red-800 border border-red-300 mb-2">
                A
              </span>
              <p className="text-red-800 font-bold">{question.optionA}</p>
            </div>
            <div className="flex-1 min-w-0 flex flex-col items-center text-center">
              <span className="inline-block px-3 py-1 rounded-full font-semibold text-xs bg-blue-100 text-blue-800 border border-blue-300 mb-2">
                B
              </span>
              <p className="text-blue-800 font-bold">{question.optionB}</p>
            </div>
          </div>

          {/* 6段階スケール（未選択は空の◯、選択時は✓。案H: 大きさで度合い 大→中→小｜小→中→大） */}
          <div className="flex flex-col items-center w-full">
            <div className="flex items-center justify-center gap-2 md:gap-3 mb-1">
              {scaleLabels.filter((s) => s.score <= 3).map(({ score }) => {
                const isSelected = currentAnswer?.score === score;
                const sizeClass =
                  score === 1
                    ? 'w-14 h-14 md:w-16 md:h-16'
                    : score === 2
                      ? 'w-12 h-12 md:w-14 md:h-14'
                      : 'min-w-[44px] min-h-[44px] w-11 h-11 md:w-12 md:h-12';
                return (
                  <button
                    key={score}
                    onClick={() => handleSelect(score)}
                    title={scaleLabels.find((l) => l.score === score)?.label}
                    className={`
                      flex items-center justify-center rounded-full
                      transition-all duration-300 transform
                      ${sizeClass}
                      ${isSelected
                        ? 'bg-red-600 text-white scale-105 ring-2 ring-red-400 ring-offset-2'
                        : 'border-2 border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100'
                      }
                    `}
                  >
                    {isSelected ? (
                      <svg className="w-2/3 h-2/3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3} aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    ) : null}
                  </button>
                );
              })}
              <div className="w-px h-14 md:h-16 bg-slate-200 shrink-0 mx-0.5" aria-hidden="true" />
              {scaleLabels.filter((s) => s.score >= 4).map(({ score }) => {
                const isSelected = currentAnswer?.score === score;
                const sizeClass =
                  score === 6
                    ? 'w-14 h-14 md:w-16 md:h-16'
                    : score === 5
                      ? 'w-12 h-12 md:w-14 md:h-14'
                      : 'min-w-[44px] min-h-[44px] w-11 h-11 md:w-12 md:h-12';
                return (
                  <button
                    key={score}
                    onClick={() => handleSelect(score)}
                    title={scaleLabels.find((l) => l.score === score)?.label}
                    className={`
                      flex items-center justify-center rounded-full
                      transition-all duration-300 transform
                      ${sizeClass}
                      ${isSelected
                        ? 'bg-blue-600 text-white scale-105 ring-2 ring-blue-400 ring-offset-2'
                        : 'border-2 border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100'
                      }
                    `}
                  >
                    {isSelected ? (
                      <svg className="w-2/3 h-2/3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3} aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    ) : null}
                  </button>
                );
              })}
            </div>
            {/* 記号（←＝A側・→＝B側・｜＝境目） */}
            <p className="text-base text-slate-400 mt-2 mb-1 tracking-wider" aria-hidden="true">
              ←｜→
            </p>
            {/* 補足ラベル（とてもA / とてもB：視認性のため太字） */}
            <div className="flex justify-between w-full text-sm text-slate-600 font-bold px-1 mt-2">
              <span className="text-left">とてもA</span>
              <span className="text-right">とてもB</span>
            </div>
          </div>
        </div>

        {/* ナビゲーションボタン */}
        <div className="flex gap-4 w-full max-w-sm">
          <button
            onClick={onPrev}
            disabled={currentIndex === 0}
            className={`
              flex-1 py-4 rounded-full font-medium transition-all duration-300
              ${currentIndex === 0
                ? 'bg-slate-100 text-slate-300 cursor-not-allowed'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:scale-[1.02]'
              }
            `}
          >
            戻る
          </button>
          <button
            onClick={onNext}
            disabled={!currentAnswer}
            className={`
              flex-1 py-4 rounded-full font-medium transition-all duration-300
              ${!currentAnswer
                ? 'bg-slate-100 text-slate-300 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700 hover:scale-[1.02]'
              }
            `}
          >
            {currentIndex === totalQuestions - 1 ? '結果を見る' : '次へ'}
          </button>
        </div>
      </section>

      {/* フッター（TOP と統一） */}
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
