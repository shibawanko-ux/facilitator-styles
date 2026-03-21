import { useState } from 'react'
import { Link } from 'react-router-dom'
import bcrypt from 'bcryptjs'
import { getSupabaseClient } from '../lib/supabase'
import { facilitatorTypes } from '../data/facilitatorTypes'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

const SALT_ROUNDS = 10

export function CreateRoomPage() {
  const [name, setName] = useState('')
  const [passcode, setPasscode] = useState('')
  const [mainFacilitatorTypeId, setMainFacilitatorTypeId] = useState('')
  const [eventDate, setEventDate] = useState('')
  const [eventName, setEventName] = useState('')
  const [expectedSubCount, setExpectedSubCount] = useState<string>('')
  const [expectedParticipantCount, setExpectedParticipantCount] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [createdRoomId, setCreatedRoomId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!name.trim()) {
      setError('ルーム名を入力してください。')
      return
    }
    if (!passcode.trim()) {
      setError('パスコードを入力してください。')
      return
    }
    if (!mainFacilitatorTypeId) {
      setError('メインファシリテーターのタイプを選んでください。')
      return
    }

    const supabase = getSupabaseClient()
    if (!supabase) {
      setError('Supabase に接続できません。.env を確認してください。')
      return
    }

    setIsSubmitting(true)
    try {
      const passcodeHash = await bcrypt.hash(passcode.trim(), SALT_ROUNDS)
      const row: {
        name: string
        passcode_hash: string
        main_facilitator_type_id: string
        event_date?: string
        event_name?: string
        expected_sub_count?: number
        expected_participant_count?: number
      } = {
        name: name.trim(),
        passcode_hash: passcodeHash,
        main_facilitator_type_id: mainFacilitatorTypeId,
      }
      if (eventDate.trim()) row.event_date = eventDate.trim()
      if (eventName.trim()) row.event_name = eventName.trim()
      const subN = parseInt(expectedSubCount, 10)
      const partN = parseInt(expectedParticipantCount, 10)
      if (!Number.isNaN(subN) && subN >= 0) row.expected_sub_count = subN
      if (!Number.isNaN(partN) && partN >= 0) row.expected_participant_count = partN

      const { data, error: insertError } = await supabase
        .from('rooms')
        .insert(row)
        .select('id')
        .single()

      if (insertError) {
        setError(insertError.message || 'ルームの作成に失敗しました。')
        return
      }
      if (data?.id) setCreatedRoomId(data.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました。')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (createdRoomId) {
    const joinUrl = `${window.location.origin}/room/${createdRoomId}/join`
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">ルームを作成しました</h1>
        <p className="mt-4 text-slate-600">参加者に次のURLとパスコードを共有してください。</p>
        <div className="mt-6 w-full max-w-md space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600">参加用URL</label>
            <div className="mt-1 flex gap-2">
              <input
                type="text"
                readOnly
                value={joinUrl}
                className="flex-1 px-3 py-2 border border-slate-200 rounded-lg bg-white text-sm"
              />
              <button
                type="button"
                onClick={() => navigator.clipboard.writeText(joinUrl)}
                className="px-4 py-2 bg-slate-200 text-slate-800 rounded-lg text-sm font-medium hover:bg-slate-300"
              >
                コピー
              </button>
            </div>
          </div>
          <p className="text-sm text-slate-600">
            <span className="font-medium">パスコード:</span> {passcode}
          </p>
        </div>
        <Link to="/" className="mt-8 text-primary-600 hover:underline">
          TOP に戻る
        </Link>
        <AppFooter />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-8 bg-slate-50">
      <AppBrandHeading />
      <h1 className="text-xl font-bold text-slate-800">ルームを作る</h1>
      <Link to="/" className="mt-2 text-sm text-primary-600 hover:underline">
        ← TOP に戻る
      </Link>

      <form onSubmit={handleSubmit} className="mt-8 w-full max-w-md space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">
            {error}
          </div>
        )}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-slate-700">
            ルーム名 <span className="text-red-500">*</span>
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
            placeholder="例: 〇月〇日 振り返り"
          />
        </div>
        <div>
          <label htmlFor="passcode" className="block text-sm font-medium text-slate-700">
            パスコード <span className="text-red-500">*</span>
          </label>
          <input
            id="passcode"
            type="password"
            value={passcode}
            onChange={(e) => setPasscode(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
            placeholder="参加者に共有する合言葉"
          />
        </div>
        <div>
          <label htmlFor="type" className="block text-sm font-medium text-slate-700">
            メインファシリテーターのタイプ <span className="text-red-500">*</span>
          </label>
          <select
            id="type"
            value={mainFacilitatorTypeId}
            onChange={(e) => setMainFacilitatorTypeId(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
          >
            <option value="">選択してください</option>
            {facilitatorTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="event_date" className="block text-sm font-medium text-slate-700">
            WS・会議の日付（任意）
          </label>
          <input
            id="event_date"
            type="date"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
          />
        </div>
        <div>
          <label htmlFor="event_name" className="block text-sm font-medium text-slate-700">
            WS・会議の名前（任意）
          </label>
          <input
            id="event_name"
            type="text"
            value={eventName}
            onChange={(e) => setEventName(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
            placeholder="例: キックオフWS"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="expected_sub" className="block text-sm font-medium text-slate-700">
              サブの人数（任意）
            </label>
            <input
              id="expected_sub"
              type="number"
              min={0}
              value={expectedSubCount}
              onChange={(e) => setExpectedSubCount(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
              placeholder="0"
            />
          </div>
          <div>
            <label htmlFor="expected_participant" className="block text-sm font-medium text-slate-700">
              参加者の人数（任意）
            </label>
            <input
              id="expected_participant"
              type="number"
              min={0}
              value={expectedParticipantCount}
              onChange={(e) => setExpectedParticipantCount(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg"
              placeholder="0"
            />
          </div>
        </div>
        <p className="text-xs text-slate-500">入力すると結果画面で「あと○人分の入力待ち」と表示できます。</p>
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition"
        >
          {isSubmitting ? '作成中...' : 'ルームを作成'}
        </button>
      </form>
      <AppFooter />
    </div>
  )
}
