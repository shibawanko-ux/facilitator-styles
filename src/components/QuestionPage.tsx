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
    <div className="min-h-screen flex flex-col px-6 py-8 bg-white">
      {/* ヘッダー・プログレス */}
      <div className="max-w-2xl w-full mx-auto mb-10">
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

      {/* 質問カード */}
      <div className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full animate-fade-in">
        <div className="card w-full mb-10">
          {/* 質問文 */}
          <h2 className="text-xl md:text-2xl font-semibold text-slate-800 mb-10 text-center leading-relaxed">
            {question.text}
          </h2>

          {/* 選択肢の両極 */}
          <div className="flex justify-between mb-8 text-sm">
            <div className="flex-1 text-left">
              <span className="inline-block px-3 py-1 bg-slate-100 text-slate-700 rounded-full font-medium text-xs mb-2">
                A
              </span>
              <p className="text-slate-600">{question.optionA}</p>
            </div>
            <div className="flex-1 text-right">
              <span className="inline-block px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full font-medium text-xs mb-2">
                B
              </span>
              <p className="text-slate-600">{question.optionB}</p>
            </div>
          </div>

          {/* 6段階スケール（3と4の間に境界線、線の下は「←｜→」のみ） */}
          <div className="flex flex-col items-center w-full">
            <div className="flex items-center justify-center gap-2 md:gap-3 mb-2">
              {/* A側: 1〜3 */}
              <div className="flex gap-2 md:gap-3">
                {scaleLabels.filter((s) => s.score <= 3).map(({ score }) => (
                  <button
                    key={score}
                    onClick={() => handleSelect(score)}
                    className={`
                      w-11 h-11 md:w-12 md:h-12 rounded-full font-semibold text-base
                      transition-all duration-300 transform
                      ${currentAnswer?.score === score
                        ? 'bg-primary-600 text-white scale-105'
                        : 'bg-slate-100 text-slate-500 hover:bg-slate-200 hover:scale-[1.02]'
                      }
                    `}
                  >
                    {score}
                  </button>
                ))}
              </div>
              {/* 境界線（3と4の間） */}
              <div className="w-px h-12 md:h-14 bg-slate-200 mx-1 shrink-0" aria-hidden="true" />
              {/* B側: 4〜6 */}
              <div className="flex gap-2 md:gap-3">
                {scaleLabels.filter((s) => s.score >= 4).map(({ score }) => (
                  <button
                    key={score}
                    onClick={() => handleSelect(score)}
                    className={`
                      w-11 h-11 md:w-12 md:h-12 rounded-full font-semibold text-base
                      transition-all duration-300 transform
                      ${currentAnswer?.score === score
                        ? 'bg-primary-600 text-white scale-105'
                        : 'bg-slate-100 text-slate-500 hover:bg-slate-200 hover:scale-[1.02]'
                      }
                    `}
                  >
                    {score}
                  </button>
                ))}
              </div>
            </div>
            {/* 線の下：記号のみ（←＝A側・→＝B側・｜＝境目） */}
            <p className="text-base text-slate-400 mb-3 tracking-wider" aria-hidden="true">
              ←｜→
            </p>
            {/* スケールラベル（左寄せ・右寄せで中央に見えないようにする） */}
            <div className="flex justify-between w-full text-xs text-slate-400 px-1">
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
      </div>

      {/* フッター */}
      <div className="mt-auto px-6 py-6 text-center border-t border-slate-100">
        <a
          href="https://awareness-design.studio.site/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-600 no-underline hover:no-underline focus:no-underline"
        >
          awareness=design
        </a>
      </div>
    </div>
  );
}
