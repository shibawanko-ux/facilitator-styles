/**
 * 結果画面（/room/:roomId/result）
 *
 * データ取得フロー:
 * - API/DB: Supabase。パスコード認証後、rooms (id, name, main_facilitator_type_id, expected_*) と
 *   evaluations (room_id, role, scores, free_comment) を取得。
 * - ローカル: resultAnalysis の getRoleCounts(evaluations)、computeSixAxisAveragesByRole(evaluations)（6軸レーダー用）。
 * - reportAgent（ReportAgentOutput）: 未接続。開発時は roomId が DEV_FIXTURE_ROOM_ID のとき fixture で表示するフォールバックあり。
 */
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import bcrypt from 'bcryptjs'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { getSupabaseClient } from '../lib/supabase'
import { facilitatorTypes } from '../data/facilitatorTypes'
import {
  getRoleCounts,
  computeSixAxisAveragesByRole,
  type SixAxisAveragesByRole,
} from '../lib/resultAnalysis'
import { SIX_AXIS_IDS, SIX_AXIS_LABELS, SIX_AXIS_DESCRIPTIONS, type SixAxisId } from '../data/evaluationItems'
import { generateReport, validateReportComment } from '../lib/reportAgent'
import type { ReportAgentOutput } from '../lib/reportAgent'
import { inputFixtureCase1 } from '../data/reportPreviewFixtures'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

/** 開発用: この roomId のとき fixture（inputFixtureCase1）で reportAgent 出力を表示する */
const DEV_FIXTURE_ROOM_ID = '58c13b5b-02a7-4a7d-aa7a-2b07aecc6c6f'

const RESULT_VERIFIED_KEY = 'facilitator_reflection_result_verified'

function getResultVerifiedRoomIds(): string[] {
  try {
    const s = sessionStorage.getItem(RESULT_VERIFIED_KEY)
    return s ? (JSON.parse(s) as string[]) : []
  } catch {
    return []
  }
}

function setResultVerified(roomId: string): void {
  const ids = getResultVerifiedRoomIds()
  if (ids.includes(roomId)) return
  sessionStorage.setItem(RESULT_VERIFIED_KEY, JSON.stringify([...ids, roomId]))
}

interface RoomRow {
  id: string
  name: string
  main_facilitator_type_id: string | null
  passcode_hash?: string
  expected_sub_count?: number | null
  expected_participant_count?: number | null
}

interface EvaluationRow {
  id: string
  room_id: string
  role: string
  evaluator_label: string | null
  scores: Record<string, number>
  free_comment: string | null
}

const RADAR_COLOR_MAIN = '#0f766e'
const RADAR_COLOR_SUB = '#64748b'
const RADAR_COLOR_PARTICIPANT = '#c2410c'

/** 軸ごとのラベル：観点名を名目位置に、メイン・サブ・参加者は同じxで縦に並べ重ならないように表示（上軸のみ点数を観点名の上に、他は下に配置）。 */
function RadarAxisTick({
  payload,
  hasSub,
  hasParticipant,
  x,
  y,
  textAnchor,
  index,
}: {
  payload: { subject: string; main: number; sub: number; participant: number }
  hasSub: boolean
  hasParticipant: boolean
  x: number
  y: number
  textAnchor: string
  index: number
}) {
  const fmt = (v: number) => (v > 0 ? v.toFixed(1) : '—')
  const lineHeight = 11
  const isTopAxis = index === 0
  const sign = isTopAxis ? -1 : 1
  const topAxisExtraUp = isTopAxis ? -6 : 0
  const dyMain = sign * lineHeight + topAxisExtraUp
  const dySub = sign * (hasSub ? lineHeight * 2 : lineHeight) + topAxisExtraUp
  const dyParticipant = sign * (hasSub ? lineHeight * 3 : lineHeight * 2) + topAxisExtraUp
  return (
    <g>
      <text textAnchor={textAnchor} fill="#1e293b" fontSize={13} fontWeight="bold" x={x} y={y}>
        {payload.subject}
      </text>
      <text
        textAnchor={textAnchor}
        fill={RADAR_COLOR_MAIN}
        fontSize={9}
        x={x}
        y={y + dyMain}
      >
        メイン：{fmt(payload.main)}
      </text>
      {hasSub && (
        <text
          textAnchor={textAnchor}
          fill={RADAR_COLOR_SUB}
          fontSize={9}
          x={x}
          y={y + dySub}
        >
          サブ：{fmt(payload.sub)}
        </text>
      )}
      {hasParticipant && (
        <text
          textAnchor={textAnchor}
          fill={RADAR_COLOR_PARTICIPANT}
          fontSize={9}
          x={x}
          y={y + dyParticipant}
        >
          参加者：{fmt(payload.participant)}
        </text>
      )}
    </g>
  )
}

/** 6軸のレーダーチャート（メイン・サブ・参加者の3系列）。各軸の名目の横に点数を表記。 */
function RadarChartSection({ sectionByRole }: { sectionByRole: SixAxisAveragesByRole }) {
  const data = SIX_AXIS_IDS.map((axisId) => ({
    subject: SIX_AXIS_LABELS[axisId],
    fullMark: 5,
    main: Math.round(sectionByRole.main[axisId] * 10) / 10,
    sub: Math.round(sectionByRole.sub[axisId] * 10) / 10,
    participant: Math.round(sectionByRole.participant[axisId] * 10) / 10,
  }))
  const hasSub = data.some((d) => d.sub > 0)
  const hasParticipant = data.some((d) => d.participant > 0)
  return (
    <section className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h2 className="text-lg font-bold text-slate-800 mb-2">6つの観点</h2>
      <div className="h-80 sm:h-[28rem] min-h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} margin={{ top: 32, right: 32, bottom: 32, left: 32 }}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis
              dataKey="subject"
              tick={(tickProps: { index: number; x: number; y: number; textAnchor: string }) => {
                const row = data[tickProps.index]
                if (!row) return null
                return (
                  <RadarAxisTick
                    payload={row}
                    hasSub={hasSub}
                    hasParticipant={hasParticipant}
                    x={tickProps.x}
                    y={tickProps.y}
                    textAnchor={tickProps.textAnchor}
                    index={tickProps.index}
                  />
                )
              }}
            />
            <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 10 }} />
            <Radar
              name="メイン"
              dataKey="main"
              stroke="#0f766e"
              fill="#0f766e"
              fillOpacity={0.4}
              strokeWidth={1.5}
              dot={{ r: 5, fill: '#0f766e', strokeWidth: 1.5 }}
            />
            {hasSub && (
              <Radar
                name="サブ"
                dataKey="sub"
                stroke="#64748b"
                fill="transparent"
                fillOpacity={0}
                strokeWidth={1.5}
                dot={{ r: 5, fill: '#64748b', stroke: '#64748b' }}
              />
            )}
            {hasParticipant && (
              <Radar
                name="参加者"
                dataKey="participant"
                stroke="#c2410c"
                fill="transparent"
                fillOpacity={0}
                strokeWidth={1.5}
                dot={{ r: 5, fill: '#c2410c', stroke: '#c2410c' }}
              />
            )}
            <Tooltip contentStyle={{ fontSize: 12 }} formatter={(value: number | undefined) => [value != null ? value.toFixed(1) : '—', '']} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-4 gap-y-1 text-sm text-slate-600">
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm shrink-0" style={{ backgroundColor: RADAR_COLOR_MAIN }} aria-hidden />
          メイン
        </span>
        {hasSub && (
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-3 w-3 rounded-sm shrink-0" style={{ backgroundColor: RADAR_COLOR_SUB }} aria-hidden />
            サブ
          </span>
        )}
        {hasParticipant && (
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-3 w-3 rounded-sm shrink-0" style={{ backgroundColor: RADAR_COLOR_PARTICIPANT }} aria-hidden />
            参加者
          </span>
        )}
      </div>
    </section>
  )
}

export function ResultPage() {
  const { roomId } = useParams<{ roomId: string }>()
  const [verified, setVerified] = useState(() => (roomId ? getResultVerifiedRoomIds().includes(roomId) : false))
  const [room, setRoom] = useState<RoomRow | null>(null)
  const [evaluations, setEvaluations] = useState<EvaluationRow[]>([])
  const [loading, setLoading] = useState(verified)
  const [error, setError] = useState<string | null>(null)
  const [passcode, setPasscode] = useState('')
  const [passcodeError, setPasscodeError] = useState<string | null>(null)
  const [verifying, setVerifying] = useState(false)
  const [reportOutput, setReportOutput] = useState<ReportAgentOutput | null>(null)
  const [reportValidation, setReportValidation] = useState<{ ok: boolean; errors: string[] } | null>(null)
  const [sharedLeadershipOpen, setSharedLeadershipOpen] = useState(false)
  const [reflectionOpen, setReflectionOpen] = useState(false)

  useEffect(() => {
    if (!roomId || !verified) return
    const supabase = getSupabaseClient()
    if (!supabase) {
      setError('接続を確認できません。')
      setLoading(false)
      return
    }
    (async () => {
      try {
        const [roomRes, evalsRes] = await Promise.all([
          supabase.from('rooms').select('id, name, main_facilitator_type_id, expected_sub_count, expected_participant_count').eq('id', roomId).single(),
          supabase.from('evaluations').select('id, room_id, role, evaluator_label, scores, free_comment').eq('room_id', roomId),
        ])
        if (roomRes.error) {
          setError(roomRes.error.message || 'ルームを取得できませんでした。')
          setLoading(false)
          return
        }
        setRoom(roomRes.data as RoomRow)
        setEvaluations((evalsRes.data as EvaluationRow[]) || [])
      } catch {
        setError('エラーが発生しました。')
      } finally {
        setLoading(false)
      }
    })()
  }, [roomId, verified])

  useEffect(() => {
    if (roomId !== DEV_FIXTURE_ROOM_ID || !verified) return
    generateReport(inputFixtureCase1, { useAI: false }).then((out) => {
      setReportOutput(out)
      setReportValidation(validateReportComment(out))
    })
  }, [roomId, verified])

  const handleVerifyPasscode = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!roomId) return
    setPasscodeError(null)
    setVerifying(true)
    const supabase = getSupabaseClient()
    if (!supabase) {
      setPasscodeError('接続を確認できません。')
      setVerifying(false)
      return
    }
    try {
      const { data: roomData, error: roomErr } = await supabase
        .from('rooms')
        .select('id, name, main_facilitator_type_id, passcode_hash, expected_sub_count, expected_participant_count')
        .eq('id', roomId)
        .single()
      if (roomErr || !roomData?.passcode_hash) {
        setPasscodeError('ルームが見つかりません。')
        setVerifying(false)
        return
      }
      const match = await bcrypt.compare(passcode.trim(), roomData.passcode_hash)
      if (!match) {
        setPasscodeError('パスコードが違います。')
        setVerifying(false)
        return
      }
      setResultVerified(roomId)
      setRoom({
        id: roomData.id,
        name: roomData.name,
        main_facilitator_type_id: roomData.main_facilitator_type_id,
        expected_sub_count: roomData.expected_sub_count ?? undefined,
        expected_participant_count: roomData.expected_participant_count ?? undefined,
      })
      setVerified(true)
      setLoading(true)
      const { data: evalsData } = await supabase
        .from('evaluations')
        .select('id, room_id, role, evaluator_label, scores, free_comment')
        .eq('room_id', roomId)
      setEvaluations((evalsData as EvaluationRow[]) || [])
    } catch {
      setPasscodeError('エラーが発生しました。')
    } finally {
      setVerifying(false)
      setLoading(false)
    }
  }

  const evaluationsWithRole = evaluations as { role: string; scores?: Record<string, number> | null }[]
  const roleCounts = getRoleCounts(evaluations)
  const mainCount = roleCounts.main
  const subCount = roleCounts.sub
  const participantCount = roleCounts.participant
  const sectionByRole = computeSixAxisAveragesByRole(evaluationsWithRole)

  const typeId = room?.main_facilitator_type_id ?? ''
  const typeName = facilitatorTypes.find((t) => t.id === typeId)?.name ?? (typeId || '未設定')

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

  if (!verified) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">結果を見る</h1>
        <p className="mt-2 text-slate-600 text-center">
          結果を表示するには、主催者から伝えられたパスコードを入力してください。
        </p>
        <form onSubmit={handleVerifyPasscode} className="mt-8 w-full max-w-sm space-y-4">
          {passcodeError && (
            <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">{passcodeError}</div>
          )}
          <div>
            <label htmlFor="result_passcode" className="block text-sm font-medium text-slate-700">
              パスコード
            </label>
            <input
              id="result_passcode"
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
            disabled={verifying}
            className="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition"
          >
            {verifying ? '確認中...' : '結果を表示'}
          </button>
        </form>
        <Link to="/" className="mt-8 text-sm text-slate-500 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <p className="text-slate-600">読み込み中...</p>
      </div>
    )
  }

  if (error || !room) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <p className="text-slate-600">{error || 'ルームが見つかりません。'}</p>
        <Link to="/" className="mt-6 text-primary-600 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  const isDevFixture = roomId === DEV_FIXTURE_ROOM_ID
  if (evaluations.length === 0 && !isDevFixture) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">結果</h1>
        <p className="mt-4 text-slate-600 text-center">まだ評価が送信されていません。</p>
        <p className="mt-2 text-sm text-slate-500">1件以上送信されると集計を表示できます。</p>
        <Link to="/" className="mt-8 text-primary-600 hover:underline">TOP に戻る</Link>
        <AppFooter />
      </div>
    )
  }

  const expectedSub = room.expected_sub_count != null ? Number(room.expected_sub_count) : null
  const expectedPart = room.expected_participant_count != null ? Number(room.expected_participant_count) : null
  const hasExpected = expectedSub != null || expectedPart != null
  const subShortfall = expectedSub != null ? Math.max(0, expectedSub - subCount) : 0
  const partShortfall = expectedPart != null ? Math.max(0, expectedPart - participantCount) : 0
  const hasShortfall = subShortfall > 0 || partShortfall > 0

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <AppBrandHeading />
        <h1 className="text-xl font-bold text-slate-800">結果</h1>
        <p className="mt-1 text-slate-600">{room.name}</p>
        <p className="mt-1 text-sm text-slate-500">メインファシリタイプ: {typeName}</p>
        <p className="mt-2 text-sm text-slate-600">
          {hasExpected ? (
            <>
              送信済み: メイン {mainCount}/1、サブ {subCount}/{expectedSub ?? '—'}、参加者 {participantCount}/{expectedPart ?? '—'}
            </>
          ) : (
            <>送信済み: メイン {mainCount}件、サブ {subCount}件、参加者 {participantCount}件</>
          )}
        </p>
        {hasShortfall && (
          <p className="mt-1 text-sm text-amber-700">
            あと{subShortfall > 0 && ` サブ${subShortfall}人`}{subShortfall > 0 && partShortfall > 0 && '、'}
            {partShortfall > 0 && ` 参加者${partShortfall}人`} の入力待ち
          </p>
        )}
        <Link to="/" className="mt-2 inline-block text-sm text-primary-600 hover:underline">
          TOP に戻る
        </Link>
        {isDevFixture && (
          <p className="mt-2 text-sm text-amber-700">開発用: レポートは fixture（inputFixtureCase1）で表示しています。</p>
        )}

        <div className="mt-8">
          <RadarChartSection sectionByRole={sectionByRole} />
        </div>

        {reportOutput && (
          <section className="mt-8 bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-8">
            <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2">
              レポート
              {isDevFixture && (
                <span className="ml-2 text-sm font-normal text-slate-500">開発用 fixture</span>
              )}
            </h2>
            {reportValidation && (
              <p className={reportValidation.ok ? 'text-green-700 text-sm' : 'text-red-700 text-sm'}>
                検証: {reportValidation.ok ? 'OK' : 'NG'}
                {reportValidation.errors.length > 0 && (
                  <ul className="list-disc pl-5 mt-1">
                    {reportValidation.errors.map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                )}
              </p>
            )}

            {/* セクション1：メインファシリテーター評価（14 表示・見せ方に準拠） */}
            <div className="space-y-5">
              <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-1">
                セクション1：メインファシリテーター評価
              </h3>
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-1">総評</h4>
                <p className="text-sm text-slate-700 break-words max-w-[50ch]">{reportOutput.summary.factSentence}</p>
                {reportOutput.summary.bullets.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {reportOutput.summary.bullets.length >= 2 ? (
                      <>
                        <p className="text-xs font-medium text-slate-500">傾向の要約</p>
                        <p className="text-sm text-slate-700 break-words max-w-[50ch] pl-0">
                          {reportOutput.summary.bullets[0]}
                        </p>
                        <p className="text-xs font-medium text-slate-500 mt-2">次の一手</p>
                        <p className="text-sm text-slate-700 break-words max-w-[50ch] pl-0">
                          {reportOutput.summary.bullets[1]}
                        </p>
                      </>
                    ) : (
                      reportOutput.summary.bullets.map((b, i) => (
                        <p key={i} className="text-sm text-slate-700 break-words max-w-[50ch]">
                          {b}
                        </p>
                      ))
                    )}
                  </div>
                )}
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-1">あなたの強み</h4>
                <p className="text-xs font-medium text-slate-500 mb-0.5">いちばんの強み</p>
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-0.5">
                  {reportOutput.strengths.bullets.map((b, i) => (
                    <li key={i} className="break-words max-w-[50ch]">{b}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-1">あなたの伸びしろ</h4>
                <p className="text-xs font-medium text-slate-500 mb-0.5">伸ばしやすいところ</p>
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-0.5">
                  {reportOutput.improvementHypotheses.bullets.map((b, i) => (
                    <li key={i} className="break-words max-w-[50ch]">{b}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-1">次回アクション</h4>
                <p className="text-sm text-slate-700 break-words max-w-[50ch]">{reportOutput.nextActions.summary}</p>
                <ol className="list-decimal pl-5 mt-1 text-sm text-slate-700 space-y-0.5">
                  {reportOutput.nextActions.bullets.map((b, i) => (
                    <li key={i} className="break-words max-w-[50ch]">{b}</li>
                  ))}
                </ol>
              </div>
            </div>

            {/* セクション2：６つの観点の点数解説 */}
            <div className="space-y-5">
              <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-1">
                セクション2：６つの観点の点数解説
              </h3>
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-2">総合点数</h4>
                <p className="text-sm text-slate-700">
                  メイン{' '}
                  <strong>
                    {(
                      (SIX_AXIS_IDS as readonly SixAxisId[]).reduce((s, id) => s + sectionByRole.main[id], 0) / 6
                    ).toFixed(1)}
                  </strong>
                  {' ／ サブ '}
                  <strong>
                    {(
                      (SIX_AXIS_IDS as readonly SixAxisId[]).reduce((s, id) => s + sectionByRole.sub[id], 0) / 6
                    ).toFixed(1)}
                  </strong>
                  {' ／ 参加者 '}
                  <strong>
                    {(
                      (SIX_AXIS_IDS as readonly SixAxisId[]).reduce(
                        (s, id) => s + sectionByRole.participant[id],
                        0
                      ) / 6
                    ).toFixed(1)}
                  </strong>
                  （6軸の平均。差分で役割間の傾向が分かります）
                </p>
              </div>
              <div className="space-y-4">
                {(SIX_AXIS_IDS as readonly SixAxisId[]).map((axisId: SixAxisId) => {
                  const bullets = reportOutput.sectionComments[axisId].bullets
                  const summaryLine = bullets[0]
                  const restBullets = bullets.slice(1)
                  return (
                    <div key={axisId}>
                      <h4 className="text-sm font-bold text-slate-700 mb-1 flex items-center gap-1">
                        {SIX_AXIS_LABELS[axisId]}
                        <span className="relative inline-flex group cursor-help group-hover:pb-40 group-hover:-mb-40">
                          <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-slate-200 text-slate-600 text-xs">
                            ?
                          </span>
                          <span
                            role="tooltip"
                            className="absolute left-0 top-full mt-1 z-20 w-72 max-w-[calc(100vw-2rem)] rounded-md border border-slate-200 bg-white px-3 py-2 text-left text-xs text-slate-700 shadow-lg opacity-0 transition-opacity duration-75 group-hover:opacity-100"
                          >
                            {SIX_AXIS_DESCRIPTIONS[axisId]}
                          </span>
                        </span>
                      </h4>
                      {summaryLine != null && (
                        <p className="text-sm font-bold text-slate-700 mb-1 break-words max-w-[50ch]">
                          {summaryLine}
                        </p>
                      )}
                      {restBullets.length > 0 && (
                        <ul className="list-disc pl-5 text-sm text-slate-700 space-y-0.5">
                          {restBullets.map((b, i) => (
                            <li key={i} className="break-words max-w-[50ch]">{b}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* セクション3：振り返り用の問い・シェアドリーダーシップ・認知 */}
            <div className="space-y-4">
              <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-1">
                セクション3：振り返りの問い・シェアドリーダーシップ
              </h3>
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <button
                  type="button"
                  onClick={() => setReflectionOpen((o) => !o)}
                  className="w-full px-4 py-3 text-left text-sm font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 flex items-center justify-between"
                >
                  振り返り用の問い
                  <span className="text-slate-500">{reflectionOpen ? '▲' : '▼'}</span>
                </button>
                {reflectionOpen && (
                  <div className="p-4 space-y-2 text-sm text-slate-700 border-t border-slate-200">
                    {reportOutput.reflectionQuestions.map((q, i) => (
                      <div key={i} className="border-l-2 border-slate-200 pl-3">
                        <p className="font-medium">{q.question}</p>
                        <p className="text-slate-600 text-xs">意図: {q.intent}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {subCount > 0 && reportOutput.sharedLeadershipReflectionQuestions?.length ? (
                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setSharedLeadershipOpen((o) => !o)}
                    className="w-full px-4 py-3 text-left text-sm font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 flex items-center justify-between"
                  >
                    シェアドリーダーシップ・認知の振り返り
                    <span className="text-slate-500">{sharedLeadershipOpen ? '▲' : '▼'}</span>
                  </button>
                  {sharedLeadershipOpen && (
                    <div className="p-4 space-y-2 text-sm text-slate-700 border-t border-slate-200">
                      {reportOutput.sharedLeadershipReflectionQuestions.map((q, i) => (
                        <div key={i} className="border-l-2 border-slate-200 pl-3">
                          <p className="font-medium">{q.question}</p>
                          <p className="text-slate-600 text-xs">意図: {q.intent}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </section>
        )}

        <AppFooter className="text-center" />
      </div>
    </div>
  )
}
