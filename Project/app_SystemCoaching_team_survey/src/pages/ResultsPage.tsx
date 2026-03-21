import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { supabase } from '../lib/supabase'
import { useAuth } from '../hooks/useAuth'

interface AxisScore {
  axis: string
  label: string
  score: number
  fullMark: number
}

interface Snapshot {
  label: string
  date: string
  total: number
  axisScores: AxisScore[]
  respondentCount: number
  teamSizeAtTime: number
  joinAlert: boolean
  hadNewJoiner: boolean
}

const AXIS_LABELS: Record<string, string> = {
  alignment: '目的共有',
  relationship: '信頼',
  conflict: '対立の質',
  system: 'システム意識',
  voice: '声の多様性',
  safety: '心理的安全性',
}

const AXIS_WEIGHTS: Record<string, number> = {
  system: 1.5,
  safety: 1.3,
  voice: 1.2,
  alignment: 1.0,
  relationship: 1.0,
  conflict: 1.0,
}

function calcTotalScore(axisScores: Record<string, number>): number {
  let weightedSum = 0
  let weightTotal = 0
  for (const [axis, score] of Object.entries(axisScores)) {
    const weight = AXIS_WEIGHTS[axis] ?? 1.0
    weightedSum += score * weight
    weightTotal += weight
  }
  return (weightedSum / weightTotal / 6) * 100
}

function getDiagnosis(total: number) {
  if (total >= 80) return { label: '優秀', color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-400', message: 'チームの状態は非常に良好です' }
  if (total >= 60) return { label: '良好', color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', dot: 'bg-blue-400', message: 'チームの状態は概ね良好です' }
  if (total >= 40) return { label: '要注意', color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-400', message: 'いくつかの課題があります' }
  return { label: '危険', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', dot: 'bg-red-400', message: 'チームの状態に深刻な課題があります' }
}

function getStateText(total: number, axisScores: AxisScore[]): string {
  const sorted = [...axisScores].sort((a, b) => b.score - a.score)
  const strongest = sorted[0]
  const weakest = sorted[sorted.length - 1]
  const overall =
    total >= 80 ? '非常に良い状態です' :
    total >= 60 ? '概ね良い状態です' :
    total >= 40 ? 'いくつかの課題がある状態です' :
    '深刻な課題がある状態です'
  return `現在のチームは${overall}。特に「${strongest?.label}」の評価が高くチームの強みになっています。一方、「${weakest?.label}」は改善の余地があります。`
}

function getAxisDiagnosis(score: number) {
  if (score >= 5.0) return { label: '強み', className: 'bg-emerald-50 text-emerald-700 border border-emerald-200', barColor: 'bg-emerald-400' }
  if (score >= 3.5) return { label: '普通', className: 'bg-gray-100 text-gray-500', barColor: 'bg-blue-400' }
  return { label: '要改善', className: 'bg-red-50 text-red-600 border border-red-200', barColor: 'bg-red-400' }
}

export default function ResultsPage() {
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(0)
  const [teamName, setTeamName] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [noData, setNoData] = useState(false)

  useEffect(() => {
    if (user) fetchResults()
  }, [user, searchParams])

  const fetchResults = async () => {
    setLoading(true)
    setNoData(false)

    const { data: teamMember } = await supabase
      .from('team_members')
      .select('team_id')
      .eq('user_id', user!.id)
      .single()

    const urlTeamId = searchParams.get('teamId')
    const teamId = urlTeamId
      ?? (user?.role === 'admin'
        ? (await supabase.from('teams').select('id').limit(1).single()).data?.id
        : teamMember?.team_id)

    if (!teamId) { setNoData(true); setLoading(false); return }

    const { data: team } = await supabase
      .from('teams')
      .select('name')
      .eq('id', teamId)
      .single()
    setTeamName(team?.name ?? '')

    const { data: projects } = await supabase
      .from('projects')
      .select('id, name')
      .eq('team_id', teamId)
      .order('created_at')

    if (!projects || projects.length === 0) { setNoData(true); setLoading(false); return }

    const { data: teamMembersHistory } = await supabase
      .from('team_members')
      .select('user_id, joined_at')
      .eq('team_id', teamId)

    const result: Snapshot[] = []

    for (const project of projects) {
      const { data: surveys } = await supabase
        .from('surveys')
        .select('id, session_number, timing, status, created_at')
        .eq('project_id', project.id)
        .eq('status', 'closed')
        .order('session_number')

      const surveyList = surveys ?? []
      const projectBaselineDate = surveyList.length > 0 ? new Date(surveyList[0].created_at) : null

      for (const survey of surveyList) {
        const { data: responses } = await supabase
          .from('responses')
          .select('user_id, score, question:questions(axis, is_reverse)')
          .eq('survey_id', survey.id)

        if (!responses || responses.length === 0) continue

        const respondentCount = new Set(responses.map((r) => r.user_id)).size
        const surveyDate = new Date(survey.created_at)
        const members = teamMembersHistory ?? []
        const teamSizeAtTime = members.filter(
          (m) => new Date(m.joined_at) <= surveyDate
        ).length

        const prevSize = result.length > 0 ? result[result.length - 1].teamSizeAtTime : teamSizeAtTime
        const hadNewJoiner = teamSizeAtTime > prevSize

        let joinAlert = false
        if (projectBaselineDate) {
          const earlyUserIds = new Set(
            members.filter((m) => new Date(m.joined_at) <= projectBaselineDate).map((m) => m.user_id)
          )
          const lateUserIds = new Set(
            members.filter((m) => new Date(m.joined_at) > projectBaselineDate).map((m) => m.user_id)
          )

          if (earlyUserIds.size > 0 && lateUserIds.size > 0) {
            const calcGroupScore = (userIds: Set<string>) => {
              const groupMap: Record<string, number[]> = {}
              for (const r of responses) {
                if (!userIds.has(r.user_id)) continue
                const q = r.question as unknown as { axis: string; is_reverse: boolean } | null
                if (!q?.axis || r.score == null) continue
                let score = r.score
                if (q.is_reverse) score = 7 - score
                if (!groupMap[q.axis]) groupMap[q.axis] = []
                groupMap[q.axis].push(score)
              }
              const avgMap: Record<string, number> = {}
              for (const [axis, scores] of Object.entries(groupMap)) {
                avgMap[axis] = scores.reduce((a, b) => a + b, 0) / scores.length
              }
              return Object.keys(avgMap).length > 0 ? calcTotalScore(avgMap) : null
            }

            const earlyScore = calcGroupScore(earlyUserIds)
            const lateScore = calcGroupScore(lateUserIds)
            if (earlyScore !== null && lateScore !== null) {
              joinAlert = Math.abs(earlyScore - lateScore) >= 15
            }
          }
        }

        const axisMap: Record<string, number[]> = {}
        for (const r of responses) {
          const q = r.question as unknown as { axis: string; is_reverse: boolean } | null
          if (!q?.axis || r.score == null) continue
          let score = r.score
          if (q.is_reverse) score = 7 - score
          if (!axisMap[q.axis]) axisMap[q.axis] = []
          axisMap[q.axis].push(score)
        }

        const avgMap: Record<string, number> = {}
        for (const [axis, scores] of Object.entries(axisMap)) {
          avgMap[axis] = Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10
        }

        const total = calcTotalScore(avgMap)
        const axisScores: AxisScore[] = Object.entries(avgMap).map(([axis, score]) => ({
          axis,
          label: AXIS_LABELS[axis] ?? axis,
          score,
          fullMark: 6,
        }))

        result.push({
          label: `第${survey.session_number}回${survey.timing === 'pre' ? '事前' : '事後'}`,
          date: new Date(survey.created_at).toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric' }),
          total: Math.round(total * 10) / 10,
          axisScores,
          respondentCount,
          teamSizeAtTime,
          joinAlert,
          hadNewJoiner,
        })
      }
    }

    if (result.length === 0) { setNoData(true); setLoading(false); return }

    setSnapshots(result)
    setSelectedIndex(result.length - 1)
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-400">データを読み込んでいます...</p>
        </div>
      </div>
    )
  }

  if (noData || snapshots.length === 0) {
    return (
      <div className="p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">結果閲覧</h2>
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-16 text-center text-gray-400">
          <div className="text-5xl mb-4">📊</div>
          <p className="text-sm font-medium text-gray-500">まだ集計できるデータがありません</p>
          <p className="text-xs mt-2 text-gray-400">アンケートが回答・終了されると結果が表示されます</p>
        </div>
      </div>
    )
  }

  const selected = snapshots[selectedIndex]
  const diagnosis = getDiagnosis(selected.total)
  const prevSnapshot = selectedIndex > 0 ? snapshots[selectedIndex - 1] : null
  const scoreDiff = prevSnapshot ? Math.round((selected.total - prevSnapshot.total) * 10) / 10 : null
  const newJoinerDates = snapshots.filter((s) => s.hadNewJoiner)

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-4">

      {/* ヘッダー */}
      <div className="mb-2">
        <h2 className="text-xl font-bold text-gray-900">チームの状態レポート</h2>
        <p className="text-sm text-gray-400 mt-0.5">{teamName}　{selected.date}（{selected.label}）</p>
      </div>

      {/* ① 今のチームの状態 */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        {/* 上部: 診断カラーバー */}
        <div className={`h-1 w-full ${diagnosis.dot}`} />

        <div className="p-6">
          <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-5">今のチームの状態</p>

          <div className="flex items-start gap-6">
            {/* スコア */}
            <div className="flex flex-col items-center min-w-[88px]">
              <div className={`w-20 h-20 rounded-2xl ${diagnosis.bg} ${diagnosis.border} border flex flex-col items-center justify-center`}>
                <span className={`text-3xl font-extrabold leading-none ${diagnosis.color}`}>{selected.total}</span>
                <span className="text-[10px] text-gray-400 mt-0.5">/ 100</span>
              </div>
              <span className={`mt-2 text-xs font-bold px-2.5 py-0.5 rounded-full ${diagnosis.bg} ${diagnosis.color}`}>
                {diagnosis.label}
              </span>
            </div>

            {/* テキスト説明 */}
            <div className="flex-1 pt-1">
              <p className="text-sm text-gray-700 leading-relaxed">
                {getStateText(selected.total, selected.axisScores)}
              </p>

              <div className="flex items-center gap-3 mt-4">
                {/* 前回比バッジ */}
                {scoreDiff !== null ? (
                  <span className={`inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full ${
                    scoreDiff > 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                    scoreDiff < 0 ? 'bg-red-50 text-red-600 border border-red-200' :
                    'bg-gray-100 text-gray-500'
                  }`}>
                    {scoreDiff > 0 ? `▲ +${scoreDiff}` : scoreDiff < 0 ? `▼ ${scoreDiff}` : '±0'}
                    <span className="font-normal text-[10px]">前回比</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center text-[11px] text-gray-400 bg-gray-50 border border-gray-200 px-3 py-1 rounded-full">
                    初回測定
                  </span>
                )}

                {/* 回答数 */}
                <span className="inline-flex items-center gap-1 text-xs text-gray-500 bg-gray-50 border border-gray-100 px-3 py-1 rounded-full">
                  <span className="text-gray-400">回答</span>
                  <span className="font-semibold text-gray-700">{selected.respondentCount}</span>
                  <span className="text-gray-400">/ {selected.teamSizeAtTime}人</span>
                </span>
              </div>
            </div>
          </div>

          {/* 加入アラート */}
          {selected.joinAlert && (
            <div className="mt-5 border border-amber-200 bg-amber-50 rounded-xl px-4 py-3 flex items-start gap-2.5">
              <span className="text-amber-400 mt-0.5 text-base">⚠️</span>
              <div>
                <p className="text-xs font-semibold text-amber-800">新しく加わったメンバーと、もともといたメンバーの間で感じ方に差があります</p>
                <p className="text-xs text-amber-600 mt-0.5">チームに慣れるためのサポートや、関係構築の機会を設けることを検討してください。</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ② 変化の流れ */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-1">変化の流れ</p>
        <h3 className="text-sm font-semibold text-gray-800 mb-0.5">スコアの推移</h3>
        <p className="text-xs text-gray-400 mb-5">セッションを重ねるごとにチームがどう変化したかを確認できます</p>

        <ResponsiveContainer width="100%" height={200}>
          <AreaChart
            data={snapshots}
            margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
            onClick={(e) => {
              if (e?.activeTooltipIndex != null) setSelectedIndex(e.activeTooltipIndex)
            }}
          >
            <defs>
              <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="" stroke="#f3f4f6" vertical={false} />
            <XAxis
              dataKey="date"
              tick={({ x, y, payload, index }) => {
                const snap = snapshots[index]
                const isJoin = snap?.hadNewJoiner
                const isSelected = index === selectedIndex
                return (
                  <text
                    x={x} y={y + 12} textAnchor="middle" fontSize={11}
                    fill={isJoin ? '#f59e0b' : isSelected ? '#2563eb' : '#9ca3af'}
                    fontWeight={isJoin || isSelected ? 600 : 400}
                  >
                    {payload.value}
                  </text>
                )
              }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#9ca3af' }} tickLine={false} axisLine={false} width={28} />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0].payload as Snapshot
                return (
                  <div className="bg-white border border-gray-200 rounded-xl px-3 py-2.5 shadow-lg text-sm">
                    <p className="text-gray-400 text-[11px]">{d.date}（{d.label}）</p>
                    <p className="font-bold text-blue-600 text-lg leading-tight">{d.total}<span className="text-xs font-normal text-gray-400 ml-0.5">点</span></p>
                    {d.hadNewJoiner && <p className="text-[11px] text-amber-500 mt-1">👤 メンバーが加入</p>}
                    <p className="text-[10px] text-gray-300 mt-1">クリックで詳細を表示</p>
                  </div>
                )
              }}
            />
            <Area
              type="linear"
              dataKey="total"
              stroke="#3b82f6"
              strokeWidth={2.5}
              fill="url(#scoreGradient)"
              dot={(props) => {
                const { cx, cy, index } = props
                const isSelected = index === selectedIndex
                return (
                  <circle
                    key={index}
                    cx={cx} cy={cy}
                    r={isSelected ? 7 : 4}
                    fill={isSelected ? '#1d4ed8' : '#3b82f6'}
                    stroke="white"
                    strokeWidth={isSelected ? 3 : 2}
                    style={{ cursor: 'pointer' }}
                  />
                )
              }}
              activeDot={{ r: 7, fill: '#1d4ed8', stroke: 'white', strokeWidth: 2, cursor: 'pointer' }}
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="flex items-center justify-between mt-3">
          <p className="text-[11px] text-gray-400">点を選択すると詳細が切り替わります</p>
          {newJoinerDates.length > 0 && (
            <div className="flex items-center gap-1.5 text-[11px] text-amber-600">
              <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
              <span>オレンジ = メンバー加入（{newJoinerDates.map(s => s.date).join('・')}）</span>
            </div>
          )}
        </div>
      </div>

      {/* ③ 詳細分析 */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-1">詳細分析</p>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-sm font-semibold text-gray-800">6つの視点から見たチームの状態</h3>
            <p className="text-xs text-gray-400 mt-0.5">チームの強みと伸びしろを確認しましょう</p>
          </div>
          {snapshots.length > 1 && (
            <div className="flex gap-1 flex-wrap justify-end">
              {snapshots.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedIndex(i)}
                  className={`text-xs px-3 py-1 rounded-full border transition-all ${
                    i === selectedIndex
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                      : 'bg-white text-gray-400 border-gray-200 hover:border-blue-300 hover:text-blue-500'
                  }`}
                >
                  {s.date}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* レーダーチャート */}
          <div>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={selected.axisScores}>
                <PolarGrid stroke="#f0f0f0" />
                <PolarAngleAxis dataKey="label" tick={{ fontSize: 11, fill: '#6b7280' }} />
                <PolarRadiusAxis domain={[0, 6]} tick={{ fontSize: 9, fill: '#c4c4c4' }} tickCount={4} />
                <Radar name="スコア" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* 軸スコアリスト */}
          <div className="flex flex-col justify-center space-y-3.5">
            {selected.axisScores
              .slice()
              .sort((a, b) => b.score - a.score)
              .map((a) => {
                const diag = getAxisDiagnosis(a.score)
                const prevScore = prevSnapshot?.axisScores.find(p => p.axis === a.axis)?.score ?? null
                const diff = prevScore !== null ? Math.round((a.score - prevScore) * 10) / 10 : null
                return (
                  <div key={a.axis}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-medium text-gray-600">
                        {AXIS_LABELS[a.axis] ?? a.axis}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {diff !== null && diff !== 0 && (
                          <span className={`text-[11px] font-semibold ${diff > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                            {diff > 0 ? `▲+${diff}` : `▼${diff}`}
                          </span>
                        )}
                        <span className="text-sm font-bold text-gray-800">{a.score}<span className="text-[11px] font-normal text-gray-400">/6</span></span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${diag.className}`}>
                          {diag.label}
                        </span>
                      </div>
                    </div>
                    <div className="bg-gray-100 rounded-full h-2">
                      <div
                        className={`${diag.barColor} h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${(a.score / 6) * 100}%` }}
                      />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      </div>

    </div>
  )
}
