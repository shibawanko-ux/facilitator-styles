import StarField from './StarField';

interface Props {
  onStart: () => void;
}

export default function StartScreen({ onStart }: Props) {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-950 via-indigo-950 to-slate-950">
      <StarField />

      <div className="relative z-10 text-center px-6 animate-fade-in">
        {/* 装飾ライン */}
        <div className="flex items-center gap-4 mb-6 justify-center">
          <div className="h-px w-16 bg-gradient-to-r from-transparent to-yellow-400" />
          <span className="text-yellow-400 text-sm tracking-widest">STATUS DIAGNOSIS</span>
          <div className="h-px w-16 bg-gradient-to-l from-transparent to-yellow-400" />
        </div>

        {/* タイトル */}
        <h1 className="text-5xl font-black text-white mb-2 leading-tight drop-shadow-lg">
          異世界
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-amber-500">
            ステータス
          </span>
          診断
        </h1>
        <p className="text-indigo-300 text-lg mt-3 mb-10">
          6問の質問に答えて、あなたのステータスを解析せよ
        </p>

        {/* キャラクターアイコン（テキスト演出） */}
        <div className="mb-10 animate-float">
          <div className="w-28 h-28 mx-auto rounded-full border-4 border-yellow-400 bg-indigo-900/60 flex items-center justify-center shadow-lg shadow-yellow-400/20">
            <span className="text-5xl">⚔️</span>
          </div>
        </div>

        {/* スタートボタン */}
        <button
          onClick={onStart}
          className="relative px-12 py-4 text-xl font-bold text-slate-900 bg-gradient-to-r from-yellow-300 to-amber-400 rounded-lg shadow-lg shadow-yellow-400/40 hover:from-yellow-200 hover:to-amber-300 hover:scale-105 transition-all duration-200 animate-glow-pulse"
        >
          ▶ 診断を開始する
        </button>

        <p className="mt-6 text-indigo-400 text-sm">所要時間：約1分</p>
      </div>
    </div>
  );
}
