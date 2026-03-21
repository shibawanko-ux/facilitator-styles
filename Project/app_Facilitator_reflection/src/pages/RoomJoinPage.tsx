import { useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import bcrypt from 'bcryptjs'
import { getSupabaseClient } from '../lib/supabase'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

const ROOM_SESSION_KEY = 'facilitator_reflection_room'

export type JoinRole = 'main' | 'sub' | 'participant'

export interface RoomSession {
  roomId: string
  roomName: string
  role: JoinRole
}

export function saveRoomSession(session: RoomSession): void {
  sessionStorage.setItem(ROOM_SESSION_KEY, JSON.stringify(session))
}

export function getRoomSession(): RoomSession | null {
  try {
    const s = sessionStorage.getItem(ROOM_SESSION_KEY)
    return s ? (JSON.parse(s) as RoomSession) : null
  } catch {
    return null
  }
}

const ROLE_OPTIONS: { value: JoinRole; label: string }[] = [
  { value: 'main', label: 'メインで行ったファシリテーター（自己評価）' },
  { value: 'sub', label: 'サブファシリテーター' },
  { value: 'participant', label: '参加者' },
]

export function RoomJoinPage() {
  const { roomId } = useParams<{ roomId: string }>()
  const navigate = useNavigate()
  const [passcode, setPasscode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'passcode' | 'role'>('passcode')
  const [roomName, setRoomName] = useState<string>('')

  const handleVerifyPasscode = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!roomId) return
    setError(null)
    setLoading(true)
    const supabase = getSupabaseClient()
    if (!supabase) {
      setError('接続を確認できません。')
      setLoading(false)
      return
    }
    try {
      const { data, error: fetchError } = await supabase
        .from('rooms')
        .select('id, name, passcode_hash')
        .eq('id', roomId)
        .single()

      if (fetchError || !data) {
        setError('ルームが見つかりません。URLを確認するか、主催者に問い合わせてください。')
        setLoading(false)
        return
      }

      const match = await bcrypt.compare(passcode.trim(), data.passcode_hash)
      if (!match) {
        setError('パスコードが違います。')
        setLoading(false)
        return
      }
      setRoomName(data.name)
      setStep('role')
    } catch {
      setError('エラーが発生しました。')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectRole = (role: JoinRole) => {
    if (!roomId || !roomName) return
    saveRoomSession({ roomId, roomName, role })
    navigate(`/room/${roomId}/evaluate`, { state: { role } })
  }

  if (!roomId) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <p className="text-slate-600">無効なURLです。</p>
        <Link to="/" className="mt-6 text-primary-600 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  if (step === 'role') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">役割を選んでください</h1>
        <p className="mt-2 text-slate-600">{roomName}</p>
        <div className="mt-8 flex flex-col gap-3 w-full max-w-sm">
          {ROLE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => handleSelectRole(opt.value)}
              className="px-4 py-3 bg-white border border-slate-200 rounded-xl text-left font-medium text-slate-800 hover:border-primary-400 hover:bg-primary-50 transition"
            >
              {opt.label}
            </button>
          ))}
        </div>
        <Link to="/" className="mt-8 text-sm text-slate-500 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
      <AppBrandHeading />
      <h1 className="text-xl font-bold text-slate-800">このルームに参加する</h1>
      <p className="mt-2 text-slate-600 text-center">
        主催者から伝えられたパスコードを入力してください。
      </p>
      <form onSubmit={handleVerifyPasscode} className="mt-8 w-full max-w-sm space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        )}
        <div>
          <label htmlFor="passcode" className="block text-sm font-medium text-slate-700">
            パスコード
          </label>
          <input
            id="passcode"
            type="password"
            value={passcode}
            onChange={(e) => setPasscode(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
            placeholder="パスコードを入力"
            autoComplete="off"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition"
        >
          {loading ? '確認中...' : '参加する'}
        </button>
      </form>
      <Link to="/" className="mt-8 text-sm text-slate-500 hover:underline">TOP に戻る</Link>
      <AppFooter />
    </div>
  )
}
