import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function SetPasswordPage() {
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { updatePassword } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirm) {
      setError('パスワードが一致しません')
      return
    }

    if (password.length < 8) {
      setError('パスワードは8文字以上で設定してください')
      return
    }

    setLoading(true)
    const { error } = await updatePassword(password)

    if (error) {
      setError('パスワードの設定に失敗しました')
      setLoading(false)
    } else {
      navigate('/')
    }
  }

  const strength = password.length === 0 ? 0 : password.length < 8 ? 1 : password.length < 12 ? 2 : 3
  const strengthLabel = ['', '短すぎます', '普通', '強い']
  const strengthColor = ['', 'bg-red-400', 'bg-amber-400', 'bg-brand']

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
            はじめてのログインです。<br />パスワードを設定してください。
          </p>
        </div>
        <div className="border-t border-white/10 pt-6">
          <p className="text-[11px] text-white/30 leading-relaxed">
            8文字以上のパスワードを設定してください
          </p>
        </div>
      </div>

      {/* 右 — フォーム */}
      <div className="flex-1 flex items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-8 text-center">
            <p className="text-[11px] text-brand tracking-widest uppercase font-semibold">awareness:design</p>
            <h1 className="text-xl font-bold text-ad-dark mt-1">Team Survey</h1>
          </div>

          <h2 className="text-xl font-semibold text-ad-dark mb-2">パスワードの設定</h2>
          <p className="text-sm text-ad-gray mb-6">はじめてのログイン。8文字以上で設定してください。</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-medium text-ad-gray mb-1.5">
                新しいパスワード
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-ad-border rounded-lg px-4 py-2.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all placeholder-gray-300"
                placeholder="8文字以上"
                required
              />
              {password.length > 0 && (
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${strengthColor[strength]}`}
                      style={{ width: `${(strength / 3) * 100}%` }}
                    />
                  </div>
                  <span className={`text-[10px] font-medium ${strength === 1 ? 'text-red-500' : strength === 2 ? 'text-amber-500' : 'text-green-600'}`}>
                    {strengthLabel[strength]}
                  </span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-[12px] font-medium text-ad-gray mb-1.5">
                パスワード（確認）
              </label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full border border-ad-border rounded-lg px-4 py-2.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all placeholder-gray-300"
                placeholder="もう一度入力"
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
                  設定中...
                </span>
              ) : 'パスワードを設定してはじめる'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
