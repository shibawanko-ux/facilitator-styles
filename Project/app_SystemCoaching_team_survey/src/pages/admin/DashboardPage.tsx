import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../../lib/supabase'
import PageHeader from '../../components/PageHeader'
import { useAuth } from '../../hooks/useAuth'

interface TeamSummary {
  id: string
  name: string
  memberCount: number
  latestScore: number | null
  latestStatus: string | null
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [teamCount, setTeamCount] = useState(0)
  const [memberCount, setMemberCount] = useState(0)
  const [closedSurveyCount, setClosedSurveyCount] = useState(0)
  const [teams, setTeams] = useState<TeamSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    const [teamsRes, membersRes, surveysRes] = await Promise.all([
      supabase.from('teams').select('id, name'),
      supabase.from('team_members').select('id, team_id'),
      supabase.from('surveys').select('id').eq('status', 'closed'),
    ])

    const teamsData = teamsRes.data ?? []
    const membersData = membersRes.data ?? []
    const surveysData = surveysRes.data ?? []

    setTeamCount(teamsData.length)
    setMemberCount(membersData.length)
    setClosedSurveyCount(surveysData.length)

    const summaries: TeamSummary[] = teamsData.map((t) => ({
      id: t.id,
      name: t.name,
      memberCount: membersData.filter((m) => m.team_id === t.id).length,
      latestScore: null,
      latestStatus: null,
    }))

    setTeams(summaries)
    setLoading(false)
  }

  // member / leader 向けダッシュボード
  if (user && user.role !== 'admin') {
    const isLeader = user.role === 'leader'
    return (
      <div className="p-8">
        <PageHeader title="ダッシュボード" description="ようこそ" />
        <div className="grid grid-cols-2 gap-4 max-w-lg">
          {!isLeader && (
            <Link
              to="/survey"
              className="bg-white rounded-xl border border-ad-border p-6 hover:border-brand hover:shadow-sm transition-all"
            >
              <div className="w-8 h-8 bg-brand-light rounded-lg flex items-center justify-center mb-3">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="2" y="1.5" width="10" height="13" rx="1.5" stroke="#333" strokeWidth="1.5"/>
                  <path d="M5 5.5h4M5 8h4M5 10.5h2" stroke="#333" strokeWidth="1.3" strokeLinecap="round"/>
                  <path d="M10 11l1.5 1.5 2.5-2.5" stroke="#ffcc00" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <p className="text-sm font-semibold text-ad-dark mb-0.5">アンケート回答</p>
              <p className="text-xs text-ad-gray">回答できるアンケートを開く</p>
            </Link>
          )}
          <Link
            to="/results"
            className="bg-white rounded-xl border border-ad-border p-6 hover:border-brand hover:shadow-sm transition-all"
          >
            <div className="w-8 h-8 bg-brand-light rounded-lg flex items-center justify-center mb-3">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 12L6 7.5L9.5 10L14 4" stroke="#333" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 14h12" stroke="#333" strokeWidth="1.3" strokeLinecap="round"/>
              </svg>
            </div>
            <p className="text-sm font-semibold text-ad-dark mb-0.5">チームの結果</p>
            <p className="text-xs text-ad-gray">最新の分析結果を確認する</p>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <PageHeader title="ダッシュボード" description="全チームの状態一覧" />

      {/* サマリーカード */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'チーム数', value: teamCount },
          { label: 'メンバー数', value: memberCount },
          { label: '実施済みアンケート', value: closedSurveyCount },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white rounded-xl border border-ad-border p-5">
            <p className="text-xs text-ad-gray mb-2">{label}</p>
            {loading ? (
              <div className="w-6 h-6 border-2 border-brand border-t-transparent rounded-full animate-spin" />
            ) : (
              <p className="text-3xl font-bold text-ad-dark">{value}</p>
            )}
          </div>
        ))}
      </div>

      {/* チーム一覧 */}
      <div className="bg-white rounded-xl border border-ad-border">
        <div className="px-5 py-4 border-b border-ad-border flex items-center justify-between">
          <h3 className="font-semibold text-ad-dark text-sm">チーム一覧</h3>
          <Link to="/teams" className="text-xs text-ad-gray hover:text-ad-dark">
            チームを管理 →
          </Link>
        </div>

        {loading ? (
          <div className="p-10 flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-brand border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-ad-gray">読み込み中...</p>
          </div>
        ) : teams.length === 0 ? (
          <div className="p-10 text-center text-ad-gray">
            <p className="text-sm font-medium text-ad-dark mb-1">チームがまだありません</p>
            <p className="text-xs">チーム管理からチームを追加してください</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-ad-bg text-ad-gray text-xs">
              <tr>
                <th className="text-left px-5 py-3 font-medium">チーム名</th>
                <th className="text-left px-5 py-3 font-medium">メンバー数</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ad-border">
              {teams.map((team) => (
                <tr key={team.id} className="hover:bg-ad-bg transition-colors">
                  <td className="px-5 py-3.5 font-medium text-ad-dark">{team.name}</td>
                  <td className="px-5 py-3.5 text-ad-gray">{team.memberCount}人</td>
                  <td className="px-5 py-3.5 text-right">
                    <Link to={`/results?teamId=${team.id}`} className="text-xs text-ad-gray hover:text-ad-dark">
                      結果を見る →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
