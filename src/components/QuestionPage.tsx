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
  { score: 3, label: 'どちらとも言えない' },
  { score: 4, label: 'ややBに近い' },
  { score: 5, label: 'とてもBに近い' },
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
          <span className="text-sm text-gray-400 font-medium">
            質問 {currentIndex + 1} / {totalQuestions}
          </span>
          <span className="text-sm text-gray-400 font-medium">
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
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-10 text-center leading-relaxed">
            {question.text}
          </h2>

          {/* 選択肢の両極 */}
          <div className="flex justify-between mb-8 text-sm">
            <div className="flex-1 text-left">
              <span className="inline-block px-3 py-1 bg-slate-100 text-slate-700 rounded-full font-medium text-xs mb-2">
                A
              </span>
              <p className="text-gray-600">{question.optionA}</p>
            </div>
            <div className="flex-1 text-right">
              <span className="inline-block px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full font-medium text-xs mb-2">
                B
              </span>
              <p className="text-gray-600">{question.optionB}</p>
            </div>
          </div>

          {/* 5段階スケール */}
          <div className="flex justify-center gap-3 md:gap-4 mb-6">
            {scaleLabels.map(({ score }) => (
              <button
                key={score}
                onClick={() => handleSelect(score)}
                className={`
                  w-12 h-12 md:w-14 md:h-14 rounded-full font-semibold text-lg
                  transition-all duration-300 transform
                  ${currentAnswer?.score === score
                    ? 'bg-primary-700 text-white scale-110'
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200 hover:scale-105'
                  }
                `}
              >
                {score}
              </button>
            ))}
          </div>

          {/* スケールラベル */}
          <div className="flex justify-between text-xs text-gray-400 px-2">
            <span>とてもA</span>
            <span>どちらとも</span>
            <span>とてもB</span>
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
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:scale-105'
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
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-primary-700 text-white hover:bg-primary-800 hover:scale-105'
              }
            `}
          >
            {currentIndex === totalQuestions - 1 ? '結果を見る' : '次へ'}
          </button>
        </div>
      </div>
    </div>
  );
}
