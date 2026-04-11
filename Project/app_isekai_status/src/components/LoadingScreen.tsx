import { useEffect, useState } from 'react';
import StarField from './StarField';

interface Props {
  onDone: () => void;
}

const MESSAGES = [
  '異世界転生処理中...',
  'ステータスを解析中...',
  '特殊スキルを検出中...',
  '固有スキルを付与中...',
  'ステータスウィンドウを生成中...',
];

export default function LoadingScreen({ onDone }: Props) {
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          setTimeout(onDone, 300);
          return 100;
        }
        return p + 4;
      });
      setMessageIndex((i) => Math.min(i + 1, MESSAGES.length - 1));
    }, 120);
    return () => clearInterval(interval);
  }, [onDone]);

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-950 via-indigo-950 to-slate-950">
      <StarField />

      <div className="relative z-10 text-center px-6 w-full max-w-sm">
        {/* アニメーションアイコン */}
        <div className="mb-8 animate-float">
          <div className="w-24 h-24 mx-auto rounded-full border-4 border-indigo-400 bg-indigo-900/60 flex items-center justify-center shadow-lg shadow-indigo-400/30">
            <span className="text-4xl">🌀</span>
          </div>
        </div>

        {/* メッセージ */}
        <p className="text-indigo-300 text-base mb-6 h-6 transition-all duration-300">
          {MESSAGES[messageIndex]}
        </p>

        {/* プログレスバー */}
        <div className="h-3 bg-indigo-900/60 rounded-full overflow-hidden border border-indigo-700/40 mb-3">
          <div
            className="h-full bg-gradient-to-r from-indigo-400 via-purple-400 to-yellow-400 rounded-full transition-all duration-100 shadow-sm shadow-yellow-400/40"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-yellow-400 font-bold text-lg">{progress}%</p>
      </div>
    </div>
  );
}
