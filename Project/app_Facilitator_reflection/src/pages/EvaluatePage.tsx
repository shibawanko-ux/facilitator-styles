import { useState, useMemo, useRef, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import { getSupabaseClient } from '../lib/supabase'
import { getRoomSession } from './RoomJoinPage'
import {
  itemsBySixAxis,
  allItemIds,
  type EvaluationItem,
} from '../data/evaluationItems'
import { validateAndBuildScores, SCORE_MIN, SCORE_MAX } from '../lib/evaluationInput'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

const SENT_SESSION_KEY_PREFIX = 'facilitator_reflection_sent_'
function getSentSessionKey(roomId: string, role: string): string {
  return `${SENT_SESSION_KEY_PREFIX}${roomId}_${role}`
}
function markSentForRoomRole(roomId: string, role: string): void {
  sessionStorage.setItem(getSentSessionKey(roomId, role), '1')
}
function hasSentForRoomRole(roomId: string, role: string): boolean {
  return sessionStorage.getItem(getSentSessionKey(roomId, role)) === '1'
}

function ScoreRow({ item, value, onChange }: { item: EvaluationItem; value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-2 py-3 border-b border-slate-100 last:border-0">
      <label className="sm:w-2/3 text-sm text-slate-700 flex-shrink-0">
        {item.id}: {item.label}
      </label>
      <div className="flex gap-2 flex-wrap">
        {Array.from({ length: SCORE_MAX - SCORE_MIN + 1 }, (_, i) => i + SCORE_MIN).map((n) => (
          <label key={n} className="flex items-center gap-1 cursor-pointer">
            <input
              type="radio"
              name={`score-${item.id}`}
              value={n}
              checked={value === n}
              onChange={() => onChange(n)}
              className="rounded border-slate-300"
            />
            <span className="text-sm">{n}</span>
          </label>
        ))}
      </div>
    </div>
  )
}

/** 評価入力画面：18項目のスコア（5段階）＋自由記述 → evaluations に保存 */
export function EvaluatePage() {
  const { roomId } = useParams<{ roomId: string }>()
  const location = useLocation()
  const stateRole = (location.state as { role?: string } | null)?.role
  const session = getRoomSession()
  const role = (stateRole || session?.role) as 'main' | 'sub' | 'participant' | undefined
  const roomName = session?.roomName

  const initialScores = useMemo(() => {
    const o: Record<string, number> = {}
    allItemIds.forEach((id) => { o[id] = 0 })
    return o
  }, [])

  const [evaluatorLabel, setEvaluatorLabel] = useState('')
  const [scores, setScores] = useState<Record<string, number>>(initialScores)
  const [freeComment, setFreeComment] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [alreadySent, setAlreadySent] = useState<boolean | null>(null)
  const [alreadySentMessage, setAlreadySentMessage] = useState<string>('')
  const errorRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (error) errorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [error])

  useEffect(() => {
    if (!roomId || !role) return
    if (hasSentForRoomRole(roomId, role)) {
      setAlreadySent(true)
      setAlreadySentMessage('この役割ではすでに送信済みです。')
      return
    }
    if (role === 'main') {
      const supabase = getSupabaseClient()
      if (supabase) {
        void (async () => {
          const { count, error: fetchError } = await supabase
            .from('evaluations')
            .select('id', { count: 'exact', head: true })
            .eq('room_id', roomId)
            .eq('role', 'main')
          if (fetchError) {
            setAlreadySent(false)
            return
          }
          if (count != null && count >= 1) {
            setAlreadySent(true)
            setAlreadySentMessage('メインの自己評価はすでに送信済みです。')
          } else {
            setAlreadySent(false)
          }
        })()
      } else {
        setAlreadySent(false)
      }
      return
    }
    if (role === 'sub') {
      const supabase = getSupabaseClient()
      if (supabase) {
        void (async () => {
          const [roomRes, countRes] = await Promise.all([
            supabase.from('rooms').select('expected_sub_count').eq('id', roomId).single(),
            supabase.from('evaluations').select('id', { count: 'exact', head: true }).eq('room_id', roomId).eq('role', 'sub'),
          ])
          const expected = roomRes.data?.expected_sub_count
          if (roomRes.error || expected == null || typeof expected !== 'number' || expected < 1) {
            setAlreadySent(false)
            return
          }
          if (countRes.error) {
            setAlreadySent(false)
            return
          }
          const count = countRes.count ?? 0
          if (count >= expected) {
            setAlreadySent(true)
            setAlreadySentMessage('サブの人数が既に上限に達しています。')
          } else {
            setAlreadySent(false)
          }
        })()
      } else {
        setAlreadySent(false)
      }
      return
    }
    if (role === 'participant') {
      const supabase = getSupabaseClient()
      if (supabase) {
        void (async () => {
          const [roomRes, countRes] = await Promise.all([
            supabase.from('rooms').select('expected_participant_count').eq('id', roomId).single(),
            supabase.from('evaluations').select('id', { count: 'exact', head: true }).eq('room_id', roomId).eq('role', 'participant'),
          ])
          const expected = roomRes.data?.expected_participant_count
          if (roomRes.error || expected == null || typeof expected !== 'number' || expected < 1) {
            setAlreadySent(false)
            return
          }
          if (countRes.error) {
            setAlreadySent(false)
            return
          }
          const count = countRes.count ?? 0
          if (count >= expected) {
            setAlreadySent(true)
            setAlreadySentMessage('参加者の人数が既に上限に達しています。')
          } else {
            setAlreadySent(false)
          }
        })()
      } else {
        setAlreadySent(false)
      }
      return
    }
    setAlreadySent(false)
  }, [roomId, role])

  const setScore = (id: string, value: number) => {
    setScores((prev) => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!roomId || !role) {
      setError('ルーム情報がありません。参加画面からやり直してください。')
      return
    }
    const validated = validateAndBuildScores(scores)
    if (!validated.ok) {
      setError(validated.error)
      return
    }
    const scoresForDb = validated.scoresForDb

    setError(null)
    setLoading(true)
    const supabase = getSupabaseClient()
    if (!supabase) {
      setError('接続を確認できません。')
      setLoading(false)
      return
    }
    try {
      const { error: insertError } = await supabase.from('evaluations')        .insert({
        room_id: roomId,
        role,
        evaluator_label: evaluatorLabel.trim() || null,
        scores: scoresForDb,
        free_comment: freeComment.trim() || null,
      })
      if (insertError) {
        const msg = insertError.message || '送信に失敗しました。'
        const isRls =
          /policy|permission|row level|違反|RLS/i.test(msg) ||
          msg.includes('new row violates')
        setError(
          isRls
            ? `${msg} — Supabase の evaluations テーブルで、anon が INSERT できる RLS ポリシーを追加してください。`
            : msg
        )
        setLoading(false)
        return
      }
      markSentForRoomRole(roomId, role)
      setSubmitted(true)
    } catch {
      setError('エラーが発生しました。')
    } finally {
      setLoading(false)
    }
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

  if (!role) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <p className="text-slate-600">参加情報がありません。参加画面からやり直してください。</p>
        <Link to={`/room/${roomId}/join`} className="mt-6 text-primary-600 hover:underline">参加画面へ</Link>
        <AppFooter />
      </div>
    )
  }

  if (alreadySent) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">送信済みです</h1>
        <p className="mt-4 text-slate-600">{alreadySentMessage}</p>
        <Link
          to={`/room/${roomId}/result`}
          className="mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          結果を見る
        </Link>
        <Link to="/" className="mt-4 text-sm text-primary-600 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">送信しました</h1>
        <p className="mt-4 text-slate-600">ご協力ありがとうございます。</p>
        <Link
          to={`/room/${roomId}/result`}
          className="mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          結果を見る
        </Link>
        <Link to="/" className="mt-4 text-sm text-primary-600 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  const roleLabel =
    role === 'main' ? 'メインで行ったファシリテーター（自己評価）' : role === 'sub' ? 'サブファシリテーター' : '参加者'

  if (alreadySent === null && (role === 'main' || role === 'sub' || role === 'participant')) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <p className="text-slate-600">確認中...</p>
        <AppFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">評価を入力する</h1>
        {roomName && <p className="mt-1 text-slate-600">{roomName}</p>}
        <p className="mt-1 text-sm text-slate-500">{roleLabel}</p>
        <Link to={`/room/${roomId}/join`} className="mt-2 inline-block text-sm text-primary-600 hover:underline">
          ← 参加画面に戻る
        </Link>

        <div className="mt-6 p-4 rounded-lg bg-slate-100 border border-slate-200 text-sm text-slate-700">
          <p className="font-medium text-slate-800 mb-1">評価の観点（6つのコアスキル）</p>
          <p className="mb-2">話し合いの「場」は、共有→発散→収束→決定の流れで進みます。次の6つの観点で、その場のファシリテーションを振り返ってください。</p>
          <ul className="list-disc list-inside space-y-0.5 text-slate-600">
            {itemsBySixAxis.map(({ label }) => (
              <li key={label}><strong>{label}</strong></li>
            ))}
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-8">
          {error && (
            <div ref={errorRef} className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
              <p className="font-medium">送信できませんでした</p>
              <p className="mt-1 whitespace-pre-wrap">{error}</p>
            </div>
          )}

          <div>
            <label htmlFor="evaluator_label" className="block text-sm font-medium text-slate-700">
              表示名（任意）
            </label>
            <input
              id="evaluator_label"
              type="text"
              value={evaluatorLabel}
              onChange={(e) => setEvaluatorLabel(e.target.value)}
              className="mt-1 w-full max-w-xs px-3 py-2 border border-slate-300 rounded-lg"
              placeholder="匿名の場合は空欄でOK"
            />
          </div>

          {itemsBySixAxis.map(({ axisId, label, items }) => (
            <section key={axisId} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-800 mb-4">{label}</h2>
              <p className="text-sm text-slate-500 mb-4">1〜5 でお選びください。</p>
              <div className="space-y-0">
                {items.map((item) => (
                  <ScoreRow
                    key={item.id}
                    item={item}
                    value={scores[item.id] ?? 0}
                    onChange={(v) => setScore(item.id, v)}
                  />
                ))}
              </div>
            </section>
          ))}

          <section className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <label htmlFor="free_comment" className="block text-sm font-medium text-slate-700">
              自由記述（任意）
            </label>
            <textarea
              id="free_comment"
              value={freeComment}
              onChange={(e) => setFreeComment(e.target.value)}
              rows={4}
              className="mt-2 w-full px-3 py-2 border border-slate-300 rounded-lg"
              placeholder="気づきやコメントがあればどうぞ"
            />
          </section>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition"
          >
            {loading ? '送信中...' : '送信する'}
          </button>
        </form>

        <AppFooter className="text-center" />
      </div>
    </div>
  )
}
