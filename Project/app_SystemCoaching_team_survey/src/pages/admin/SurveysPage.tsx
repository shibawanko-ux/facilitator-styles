import { useState, useEffect } from 'react'
import { supabase } from '../../lib/supabase'
import PageHeader from '../../components/PageHeader'

interface Team {
  id: string
  name: string
  projectCount?: number
  activeSurveyCount?: number
}

interface Project {
  id: string
  team_id: string
  name: string
  status: string
  created_at: string
}

interface Survey {
  id: string
  project_id: string
  session_number: number
  timing: 'pre' | 'post'
  is_final: boolean
  status: 'draft' | 'active' | 'closed'
  created_at: string
}

interface ResponseStatus {
  user_id: string
  email: string
  answered: boolean
}

export default function SurveysPage() {
  const [teams, setTeams] = useState<Team[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [surveys, setSurveys] = useState<Survey[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [selectedSurveyId, setSelectedSurveyId] = useState<string | null>(null)
  const [responseStatuses, setResponseStatuses] = useState<ResponseStatus[]>([])
  const [loadingStatus, setLoadingStatus] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // プロジェクト作成フォーム
  const [newProjectName, setNewProjectName] = useState('')
  const [addingProject, setAddingProject] = useState(false)
  const [showProjectForm, setShowProjectForm] = useState(false)

  // プロジェクト名編集
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null)
  const [editingProjectName, setEditingProjectName] = useState('')

  // アンケート作成フォーム
  const [newSessionNumber, setNewSessionNumber] = useState(1)
  const [newTiming, setNewTiming] = useState<'pre' | 'post'>('pre')
  const [newIsFinal, setNewIsFinal] = useState(false)
  const [addingSurvey, setAddingSurvey] = useState(false)

  useEffect(() => { fetchData() }, [])
  useEffect(() => { if (selectedProjectId) fetchSurveys(selectedProjectId) }, [selectedProjectId])

  const fetchData = async () => {
    const [teamsRes, projectsRes, surveysRes] = await Promise.all([
      supabase.from('teams').select('*').order('created_at'),
      supabase.from('projects').select('*').order('created_at'),
      supabase.from('surveys').select('*'),
    ])
    const teamsData = teamsRes.data ?? []
    const projectsData = projectsRes.data ?? []
    const surveysData = surveysRes.data ?? []

    const enrichedTeams: Team[] = teamsData.map((t) => {
      const tp = projectsData.filter((p) => p.team_id === t.id)
      const activeSurveys = surveysData.filter(
        (s) => s.status === 'active' && tp.some((p) => p.id === s.project_id)
      )
      return { ...t, projectCount: tp.length, activeSurveyCount: activeSurveys.length }
    })

    setTeams(enrichedTeams)
    setProjects(projectsData)
    setLoading(false)
  }

  const fetchSurveys = async (projectId: string) => {
    const { data } = await supabase
      .from('surveys').select('*')
      .eq('project_id', projectId)
      .order('session_number').order('timing')
    setSurveys(data ?? [])
  }

  const fetchResponseStatus = async (survey: Survey) => {
    if (selectedSurveyId === survey.id) { setSelectedSurveyId(null); setResponseStatuses([]); return }
    setSelectedSurveyId(survey.id)
    setLoadingStatus(true)
    const { data: project } = await supabase.from('projects').select('team_id').eq('id', survey.project_id).single()
    if (!project) { setLoadingStatus(false); return }
    const [teamMembersRes, responsesRes] = await Promise.all([
      supabase.from('team_members').select('user_id, user:users(email)').eq('team_id', project.team_id),
      supabase.from('responses').select('user_id').eq('survey_id', survey.id),
    ])
    const answeredUserIds = new Set((responsesRes.data ?? []).map((r) => r.user_id))
    setResponseStatuses((teamMembersRes.data ?? []).map((tm) => ({
      user_id: tm.user_id,
      email: (tm.user as unknown as { email: string } | null)?.email ?? '',
      answered: answeredUserIds.has(tm.user_id),
    })))
    setLoadingStatus(false)
  }

  const handleSelectTeam = (team: Team) => {
    setSelectedTeam(team)
    setSelectedProjectId(null)
    setSurveys([])
    setShowProjectForm(false)
  }

  const handleAddProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProjectName.trim() || !selectedTeam) return
    setAddingProject(true)
    setError('')
    const { data, error } = await supabase
      .from('projects')
      .insert({ name: newProjectName.trim(), team_id: selectedTeam.id, status: 'active' })
      .select().single()
    if (error) {
      setError('プロジェクトの作成に失敗しました')
    } else {
      setProjects((prev) => [...prev, data])
      setSelectedProjectId(data.id)
      setNewProjectName('')
      setShowProjectForm(false)
      await fetchData()
    }
    setAddingProject(false)
  }

  const handleAddSurvey = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedProjectId) return
    setAddingSurvey(true)
    setError('')
    const { error } = await supabase.from('surveys').insert({
      project_id: selectedProjectId,
      session_number: newSessionNumber,
      timing: newTiming,
      is_final: newIsFinal,
      status: 'draft',
    })
    if (error) { setError('アンケートの作成に失敗しました') }
    else { await fetchSurveys(selectedProjectId) }
    setAddingSurvey(false)
  }

  const handleUpdateStatus = async (surveyId: string, status: 'draft' | 'active' | 'closed') => {
    const { error } = await supabase.from('surveys').update({ status }).eq('id', surveyId)
    if (error) { setError('ステータスの更新に失敗しました') }
    else if (selectedProjectId) { await fetchSurveys(selectedProjectId); await fetchData() }
  }

  const handleUpdateProjectName = async (projectId: string) => {
    if (!editingProjectName.trim()) return
    const { error } = await supabase
      .from('projects')
      .update({ name: editingProjectName.trim() })
      .eq('id', projectId)
    if (error) {
      setError('プロジェクト名の更新に失敗しました')
    } else {
      setProjects((prev) => prev.map((p) => p.id === projectId ? { ...p, name: editingProjectName.trim() } : p))
      setEditingProjectId(null)
    }
  }

  const handleDeleteSurvey = async (surveyId: string) => {
    if (!confirm('このアンケートを削除しますか？')) return
    const { error } = await supabase.from('surveys').delete().eq('id', surveyId)
    if (error) { setError('削除に失敗しました') }
    else if (selectedProjectId) { await fetchSurveys(selectedProjectId) }
  }

  const teamProjects = selectedTeam ? projects.filter((p) => p.team_id === selectedTeam.id) : []
  const selectedProject = projects.find((p) => p.id === selectedProjectId)

  const statusLabel = (status: string) => {
    if (status === 'active') return { label: '配信中', className: 'bg-green-50 text-green-700 border border-green-200' }
    if (status === 'closed') return { label: '終了', className: 'bg-ad-bg text-ad-gray border border-ad-border' }
    return { label: '下書き', className: 'bg-brand-light text-ad-dark border border-brand/30' }
  }

  // Step 1: チーム選択画面
  if (!selectedTeam) {
    return (
      <div className="p-8">
        <PageHeader title="アンケート管理" description="チームを選択してください" />
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
        {loading ? (
          <div className="flex flex-col items-center gap-3 py-12">
            <div className="w-8 h-8 border-2 border-brand border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-ad-gray">読み込み中...</p>
          </div>
        ) : teams.length === 0 ? (
          <div className="bg-white rounded-xl border border-ad-border p-12 text-center text-ad-gray">
            <p className="text-sm">チームがありません。先にチームを作成してください。</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {teams.map((team) => (
              <button
                key={team.id}
                onClick={() => handleSelectTeam(team)}
                className="bg-white rounded-xl border border-ad-border p-6 text-left hover:border-brand hover:shadow-sm transition-all"
              >
                <p className="text-base font-bold text-ad-dark mb-3">{team.name}</p>
                <div className="space-y-1.5">
                  <p className="text-xs text-ad-gray">
                    プロジェクト：<span className="font-semibold text-ad-dark">{team.projectCount}件</span>
                  </p>
                  {(team.activeSurveyCount ?? 0) > 0 && (
                    <span className="inline-block bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded border border-green-200 font-medium">
                      配信中 {team.activeSurveyCount}件
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    )
  }

  // Step 2: チーム内のプロジェクト・アンケート管理
  return (
    <div className="p-8">
      <div className="mb-6 flex items-center gap-2">
        <button
          onClick={() => { setSelectedTeam(null); setSelectedProjectId(null); setSurveys([]) }}
          className="text-sm text-ad-gray hover:text-ad-dark transition-colors"
        >
          ← チーム一覧
        </button>
        <span className="text-ad-border">/</span>
        <h2 className="text-base font-bold text-ad-dark">{selectedTeam.name}</h2>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {/* 左カラム：プロジェクト一覧 */}
        <div className="col-span-1">
          <div className="bg-white rounded-xl border border-ad-border mb-3">
            <div className="px-4 py-3 border-b border-ad-border flex items-center justify-between">
              <h3 className="font-semibold text-ad-dark text-xs uppercase tracking-wide">プロジェクト</h3>
              <button
                onClick={() => setShowProjectForm((v) => !v)}
                className="text-xs text-ad-gray hover:text-ad-dark"
              >
                {showProjectForm ? 'キャンセル' : '+ 追加'}
              </button>
            </div>

            {showProjectForm && (
              <form onSubmit={handleAddProject} className="p-3 border-b border-ad-border space-y-2">
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="例：2026年春"
                  className="w-full border border-ad-border rounded-lg px-3 py-2 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand placeholder-gray-300"
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={addingProject || !newProjectName.trim()}
                  className="w-full bg-brand text-ad-dark py-1.5 rounded-lg text-sm font-semibold hover:bg-brand-dark disabled:opacity-40"
                >
                  {addingProject ? '作成中...' : '作成'}
                </button>
              </form>
            )}

            {teamProjects.length === 0 ? (
              <div className="p-4 text-center text-ad-gray text-sm">プロジェクトがありません</div>
            ) : (
              <ul className="divide-y divide-ad-border">
                {teamProjects.map((p) => (
                  <li key={p.id} className={`group ${selectedProjectId === p.id ? 'bg-brand-light' : ''}`}>
                    {editingProjectId === p.id ? (
                      <div className="flex items-center gap-1 px-3 py-2">
                        <input
                          type="text"
                          value={editingProjectName}
                          onChange={(e) => setEditingProjectName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleUpdateProjectName(p.id)
                            if (e.key === 'Escape') setEditingProjectId(null)
                          }}
                          className="flex-1 text-sm border border-brand rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand text-ad-dark"
                          autoFocus
                        />
                        <button
                          onClick={() => handleUpdateProjectName(p.id)}
                          className="text-xs text-ad-dark font-semibold bg-brand px-2 py-1 rounded hover:bg-brand-dark"
                        >保存</button>
                        <button
                          onClick={() => setEditingProjectId(null)}
                          className="text-xs text-ad-gray hover:text-ad-dark"
                        >×</button>
                      </div>
                    ) : (
                      <div className="flex items-center">
                        <button
                          onClick={() => setSelectedProjectId(p.id)}
                          className={`flex-1 text-left px-4 py-3 text-sm transition-colors ${
                            selectedProjectId === p.id
                              ? 'text-ad-dark font-semibold'
                              : 'text-ad-gray hover:text-ad-dark hover:bg-ad-bg'
                          }`}
                        >
                          {p.name}
                        </button>
                        <button
                          onClick={() => { setEditingProjectId(p.id); setEditingProjectName(p.name) }}
                          className="opacity-0 group-hover:opacity-100 px-2 py-3 text-xs text-ad-gray hover:text-ad-dark transition-opacity"
                        >編集</button>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* 右カラム：アンケート一覧 */}
        <div className="col-span-2">
          {selectedProject ? (
            <>
              <div className="bg-white rounded-xl border border-ad-border mb-4">
                <div className="px-5 py-4 border-b border-ad-border">
                  <h3 className="font-semibold text-ad-dark text-sm">{selectedProject.name}</h3>
                </div>

                {surveys.length === 0 ? (
                  <div className="p-8 text-center text-ad-gray">
                    <p className="text-sm">アンケートがありません</p>
                  </div>
                ) : (
                  <table className="w-full text-sm">
                    <thead className="bg-ad-bg text-ad-gray text-xs">
                      <tr>
                        <th className="text-left px-5 py-3 font-medium">セッション</th>
                        <th className="text-left px-5 py-3 font-medium">タイミング</th>
                        <th className="text-left px-5 py-3 font-medium">最終回</th>
                        <th className="text-left px-5 py-3 font-medium">ステータス</th>
                        <th className="px-5 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-ad-border">
                      {surveys.map((s) => {
                        const { label, className } = statusLabel(s.status)
                        const isSelected = selectedSurveyId === s.id
                        return (
                          <>
                            <tr key={s.id} className="hover:bg-ad-bg transition-colors">
                              <td className="px-5 py-3 text-ad-dark font-medium">第{s.session_number}回</td>
                              <td className="px-5 py-3">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                  s.timing === 'pre'
                                    ? 'bg-ad-bg text-ad-dark border border-ad-border'
                                    : 'bg-brand-light text-ad-dark border border-brand/30'
                                }`}>
                                  {s.timing === 'pre' ? '事前' : '事後'}
                                </span>
                              </td>
                              <td className="px-5 py-3 text-ad-gray text-xs">{s.is_final ? '✓ 最終回' : '—'}</td>
                              <td className="px-5 py-3">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${className}`}>
                                  {label}
                                </span>
                              </td>
                              <td className="px-5 py-3 text-right space-x-2">
                                <button onClick={() => fetchResponseStatus(s)} className="text-xs text-ad-gray hover:text-ad-dark">
                                  {isSelected ? '▲ 閉じる' : '▼ 回答状況'}
                                </button>
                                {s.status === 'draft' && (
                                  <button onClick={() => handleUpdateStatus(s.id, 'active')} className="text-xs font-semibold text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded hover:bg-green-100">配信開始</button>
                                )}
                                {s.status === 'active' && (
                                  <button onClick={() => handleUpdateStatus(s.id, 'closed')} className="text-xs text-ad-gray hover:text-ad-dark px-2 py-0.5 rounded hover:bg-ad-bg border border-ad-border">終了</button>
                                )}
                                {s.status === 'draft' && (
                                  <button onClick={() => handleDeleteSurvey(s.id)} className="text-xs text-red-400 hover:text-red-600">削除</button>
                                )}
                              </td>
                            </tr>
                            {isSelected && (
                              <tr key={`${s.id}-status`}>
                                <td colSpan={5} className="px-5 py-3 bg-ad-bg">
                                  {loadingStatus ? (
                                    <div className="flex items-center gap-2">
                                      <div className="w-4 h-4 border-2 border-brand border-t-transparent rounded-full animate-spin" />
                                      <p className="text-xs text-ad-gray">読み込み中...</p>
                                    </div>
                                  ) : (
                                    <div>
                                      <p className="text-xs font-semibold text-ad-dark mb-2">
                                        回答状況：{responseStatuses.filter((r) => r.answered).length} / {responseStatuses.length} 人回答済み
                                      </p>
                                      <div className="flex flex-wrap gap-2">
                                        {responseStatuses.map((r) => (
                                          <span key={r.user_id} className={`text-xs px-2 py-1 rounded border ${
                                            r.answered
                                              ? 'bg-green-50 text-green-700 border-green-200'
                                              : 'bg-white text-ad-gray border-ad-border'
                                          }`}>
                                            {r.answered ? '✓' : '○'} {r.email}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </td>
                              </tr>
                            )}
                          </>
                        )
                      })}
                    </tbody>
                  </table>
                )}
              </div>

              {/* アンケート追加フォーム */}
              <div className="bg-white rounded-xl border border-ad-border p-5">
                <h3 className="font-semibold text-ad-dark mb-3 text-sm">アンケートを追加</h3>
                <form onSubmit={handleAddSurvey} className="flex flex-wrap gap-3 items-end">
                  <div>
                    <label className="block text-xs text-ad-gray mb-1">セッション番号</label>
                    <input type="number" min={1} value={newSessionNumber}
                      onChange={(e) => setNewSessionNumber(Number(e.target.value))}
                      className="w-24 border border-ad-border rounded-lg px-3 py-2 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-ad-gray mb-1">タイミング</label>
                    <select value={newTiming} onChange={(e) => setNewTiming(e.target.value as 'pre' | 'post')}
                      className="border border-ad-border rounded-lg px-3 py-2 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
                    >
                      <option value="pre">事前</option>
                      <option value="post">事後</option>
                    </select>
                  </div>
                  <div className="flex items-center gap-2 pb-2">
                    <input type="checkbox" id="isFinal" checked={newIsFinal}
                      onChange={(e) => setNewIsFinal(e.target.checked)} className="rounded accent-brand"
                    />
                    <label htmlFor="isFinal" className="text-sm text-ad-dark">最終回</label>
                  </div>
                  <button type="submit" disabled={addingSurvey}
                    className="bg-brand text-ad-dark px-5 py-2 rounded-lg text-sm font-semibold hover:bg-brand-dark disabled:opacity-40 transition-all"
                  >
                    {addingSurvey ? '追加中...' : '追加'}
                  </button>
                </form>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-xl border border-ad-border p-8 text-center text-ad-gray">
              <p className="text-sm">左からプロジェクトを選択してください</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
