import { useNavigate } from 'react-router-dom'

export default function SurveyThanksPage() {
  const navigate = useNavigate()

  return (
    <div className="flex items-center justify-center py-16 px-4">
      <div className="bg-white rounded-xl border border-ad-border p-10 text-center max-w-sm w-full">
        <div className="w-14 h-14 bg-brand rounded-full flex items-center justify-center mx-auto mb-5">
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <path d="M4 11l5 5 9-9" stroke="#333" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <p className="text-[10px] font-semibold text-ad-gray tracking-widest uppercase mb-1">awareness:design</p>
        <h1 className="text-lg font-bold text-ad-dark mb-2">回答ありがとうございました</h1>
        <p className="text-sm text-ad-gray leading-relaxed mb-6">
          あなたの回答がチームの状態を映し出します。<br />
          結果はファシリテーターが分析し、<br />
          セッション後に共有されます。
        </p>
        <button
          onClick={() => navigate('/')}
          className="w-full bg-brand text-ad-dark py-2.5 rounded-lg text-sm font-semibold hover:bg-brand-dark transition-all"
        >
          ホームへ戻る
        </button>
      </div>
    </div>
  )
}
