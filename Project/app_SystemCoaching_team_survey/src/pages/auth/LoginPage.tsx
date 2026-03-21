import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const { error } = await signIn(email, password)

    if (error) {
      setError('メールアドレスまたはパスワードが正しくありません')
      setLoading(false)
    } else {
      navigate('/')
    }
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* 左 — ブランドパネル */}
      <div className="hidden lg:flex w-80 bg-ad-dark flex-col justify-between px-10 py-12">
        <div>
          <p className="text-[11px] text-brand tracking-widest uppercase font-semibold mb-1">awareness:design</p>
          <h1 className="text-2xl font-bold text-white leading-tight mt-4">
            Team<br />Survey
          </h1>
          <p className="text-ad-gray text-sm mt-4 leading-relaxed">
            チームの状態を継続的に可視化し、<br />より良いチームへ。
          </p>
        </div>
        <div className="border-t border-white/10 pt-6">
          <p className="text-[11px] text-white/30 leading-relaxed">
            招待メールに記載のアカウントでログインしてください
          </p>
        </div>
      </div>

      {/* 右 — フォーム */}
      <div className="flex-1 flex items-center justify-center px-6">
        <div className="w-full max-w-sm">
          {/* モバイル用ブランド */}
          <div className="lg:hidden mb-8 text-center">
            <p className="text-[11px] text-brand tracking-widest uppercase font-semibold">awareness:design</p>
            <h1 className="text-xl font-bold text-ad-dark mt-1">Team Survey</h1>
          </div>

          <h2 className="text-xl font-semibold text-ad-dark mb-6">ログイン</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-medium text-ad-gray mb-1.5">
                メールアドレス
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-ad-border rounded-lg px-4 py-2.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all placeholder-gray-300"
                placeholder="example@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-[12px] font-medium text-ad-gray mb-1.5">
                パスワード
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-ad-border rounded-lg px-4 py-2.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all placeholder-gray-300"
                placeholder="パスワードを入力"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2.5">
                <p className="text-red-600 text-xs">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand text-ad-dark py-2.5 rounded-lg text-sm font-semibold hover:bg-brand-dark disabled:opacity-50 transition-all mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-ad-dark border-t-transparent rounded-full animate-spin" />
                  ログイン中...
                </span>
              ) : 'ログイン'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
