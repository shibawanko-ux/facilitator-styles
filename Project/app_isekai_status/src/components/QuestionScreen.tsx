import { useState } from 'react';
import type { Answer } from '../logic/types';
import { QUESTIONS } from '../logic/questions';
import StarField from './StarField';

interface Props {
  onComplete: (answers: Record<number, Answer>) => void;
}

export default function QuestionScreen({ onComplete }: Props) {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<number, Answer>>({});
  const [selected, setSelected] = useState<Answer | null>(null);
  const [animating, setAnimating] = useState(false);

  const question = QUESTIONS[current];
  const progress = ((current) / QUESTIONS.length) * 100;

  const handleSelect = (label: Answer) => {
    if (animating) return;
    setSelected(label);
  };

  const handleNext = () => {
    if (!selected || animating) return;
    setAnimating(true);

    const newAnswers = { ...answers, [question.id]: selected };
    setAnswers(newAnswers);

    setTimeout(() => {
      if (current + 1 >= QUESTIONS.length) {
        onComplete(newAnswers);
      } else {
        setCurrent(current + 1);
        setSelected(null);
        setAnimating(false);
      }
    }, 300);
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-950 via-indigo-950 to-slate-950 px-4 py-10">
      <StarField />

      <div className="relative z-10 w-full max-w-lg animate-fade-in">
        {/* プログレスバー */}
        <div className="mb-6">
          <div className="flex justify-between text-indigo-300 text-sm mb-2">
            <span>Q{question.id} / {QUESTIONS.length}</span>
            <span>{Math.round((current / QUESTIONS.length) * 100)}% 解析済</span>
          </div>
          <div className="h-2 bg-indigo-900/60 rounded-full overflow-hidden border border-indigo-700/40">
            <div
              className="h-full bg-gradient-to-r from-indigo-400 to-yellow-400 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 質問ウィンドウ */}
        <div className="border-2 border-indigo-400/50 rounded-xl bg-slate-900/80 backdrop-blur-sm shadow-xl shadow-indigo-900/40 overflow-hidden">
          {/* ウィンドウヘッダー */}
          <div className="bg-gradient-to-r from-indigo-900 to-slate-900 px-5 py-3 border-b border-indigo-500/30 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-400 shadow-sm shadow-yellow-400/80" />
            <span className="text-indigo-300 text-sm font-medium tracking-wider">ANALYSIS SYSTEM</span>
          </div>

          {/* 質問文 */}
          <div className="px-6 pt-6 pb-4">
            <p className="text-white text-lg font-bold leading-relaxed">
              {question.text}
            </p>
          </div>

          {/* 選択肢 */}
          <div className="px-6 pb-6 space-y-3">
            {question.choices.map((choice) => (
              <button
                key={choice.label}
                onClick={() => handleSelect(choice.label)}
                className={`w-full text-left px-4 py-3 rounded-lg border transition-all duration-200 flex items-start gap-3 ${
                  selected === choice.label
                    ? 'border-yellow-400 bg-yellow-400/10 shadow-md shadow-yellow-400/20'
                    : 'border-indigo-600/40 bg-indigo-900/30 hover:border-indigo-400 hover:bg-indigo-900/50'
                }`}
              >
                <span className={`shrink-0 w-7 h-7 rounded flex items-center justify-center text-sm font-black ${
                  selected === choice.label
                    ? 'bg-yellow-400 text-slate-900'
                    : 'bg-indigo-800 text-indigo-300'
                }`}>
                  {choice.label}
                </span>
                <span className={`text-sm leading-relaxed ${
                  selected === choice.label ? 'text-yellow-100' : 'text-indigo-200'
                }`}>
                  {choice.text}
                </span>
              </button>
            ))}
          </div>

          {/* 次へボタン */}
          <div className="px-6 pb-6">
            <button
              onClick={handleNext}
              disabled={!selected}
              className={`w-full py-3 rounded-lg font-bold text-base transition-all duration-200 ${
                selected
                  ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white hover:from-indigo-400 hover:to-indigo-500 shadow-md'
                  : 'bg-indigo-900/40 text-indigo-600 cursor-not-allowed'
              }`}
            >
              {current + 1 >= QUESTIONS.length ? '解析する →' : '次へ →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
