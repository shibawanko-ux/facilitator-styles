import { useState, useEffect } from 'react'
import { supabase } from '../../lib/supabase'
import PageHeader from '../../components/PageHeader'

interface Team {
  id: string
  name: string
}

interface Member {
  id: string
  email: string
  role: string
  team_member_id: string | null
  team_id: string | null
  team_role: string | null
}

export default function MembersPage() {
  const [teams, setTeams] = useState<Team[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [openTeamId, setOpenTeamId] = useState<string | null>(null)

  // 招待フォーム
  const [emailTags, setEmailTags] = useState<string[]>([])
  const [emailInput, setEmailInput] = useState('')
  const [inviteTeamId, setInviteTeamId] = useState('')
  const [inviteRole, setInviteRole] = useState<'leader' | 'member'>('member')
  const [inviteResults, setInviteResults] = useState<{ email: string; status: 'ok' | 'exists' | 'error' }[]>([])
  const [inviting, setInviting] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    const [usersRes, teamsRes, teamMembersRes] = await Promise.all([
      supabase.from('users').select('*').neq('role', 'admin'),
      supabase.from('teams').select('*').order('created_at'),
      supabase.from('team_members').select('*'),
    ])

    const users = usersRes.data ?? []
    const teamsData = teamsRes.data ?? []
    const teamMembers = teamMembersRes.data ?? []

    const merged: Member[] = users.map((u) => {
      const tm = teamMembers.find((tm) => tm.user_id === u.id)
      return {
        id: u.id,
        email: u.email,
        role: u.role,
        team_member_id: tm?.id ?? null,
        team_id: tm?.team_id ?? null,
        team_role: tm?.role ?? null,
      }
    })

    setTeams(teamsData)
    setMembers(merged)
    setLoading(false)
  }

  const handleEmailKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',' || e.key === ' ') {
      e.preventDefault()
      addEmailTag()
    } else if (e.key === 'Backspace' && emailInput === '' && emailTags.length > 0) {
      setEmailTags((prev) => prev.slice(0, -1))
    }
  }

  const addEmailTag = () => {
    const email = emailInput.trim().toLowerCase()
    if (email && email.includes('@') && !emailTags.includes(email)) {
      setEmailTags((prev) => [...prev, email])
    }
    setEmailInput('')
  }

  const removeEmailTag = (email: string) => {
    setEmailTags((prev) => prev.filter((e) => e !== email))
  }

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    const currentInput = emailInput.trim().toLowerCase()
    const emailList = currentInput && currentInput.includes('@')
      ? [...emailTags, currentInput]
      : [...emailTags]

    if (emailList.length === 0 || !inviteTeamId) return
    setInviting(true)
    setInviteResults([])
    setError('')

    const results: { email: string; status: 'ok' | 'exists' | 'error' }[] = []

    for (const email of emailList) {
      const { data: existing } = await supabase
        .from('users')
        .select('id')
        .eq('email', email)
        .single()

      if (existing) {
        await supabase.from('team_members').delete().eq('user_id', existing.id)
        const { error } = await supabase
          .from('team_members')
          .insert({ user_id: existing.id, team_id: inviteTeamId, role: inviteRole })
        results.push({ email, status: error ? 'error' : 'ok' })
      } else {
        results.push({ email, status: 'exists' })
      }
    }

    setInviteResults(results)
    setEmailTags([])
    setEmailInput('')
    setInviting(false)
    await fetchData()
  }

  const handleAssignTeam = async (userId: string, teamId: string, teamRole: 'leader' | 'member') => {
    setError('')
    await supabase.from('team_members').delete().eq('user_id', userId)
    const { error } = await supabase
      .from('team_members')
      .insert({ user_id: userId, team_id: teamId, role: teamRole })

    if (error) {
      setError('チームへの割り当てに失敗しました')
    } else {
      await fetchData()
    }
  }

  const handleRemoveFromTeam = async (teamMemberId: string) => {
    if (!confirm('チームから削除しますか？')) return
    setError('')
    const { error } = await supabase.from('team_members').delete().eq('id', teamMemberId)
    if (error) {
      setError('削除に失敗しました')
    } else {
      await fetchData()
    }
  }

  const unassignedMembers = members.filter((m) => !m.team_id)

  return (
    <div className="p-8">
      <PageHeader title="メンバー管理" description="チームごとのメンバー管理" />

      {/* 招待フォーム */}
      <div className="bg-white rounded-xl border border-ad-border p-5 mb-6">
        <h3 className="font-semibold text-ad-dark mb-1 text-sm">メンバーを一括登録</h3>
        <p className="text-xs text-ad-gray mb-3">
          メールアドレスを入力してEnterで追加。チームと役割を選んで登録してください。<br />
          ※ まだアカウントがない場合は、管理画面でユーザーを先に作成してください
        </p>
        <form onSubmit={handleInvite} className="space-y-3">
          <div
            className="min-h-[80px] w-full border border-ad-border rounded-lg px-3 py-2 flex flex-wrap gap-2 cursor-text focus-within:ring-2 focus-within:ring-brand focus-within:border-transparent transition-all"
            onClick={() => document.getElementById('email-tag-input')?.focus()}
          >
            {emailTags.map((email) => (
              <span
                key={email}
                className="flex items-center gap-1 bg-brand-light border border-brand/30 text-ad-dark text-xs px-2 py-1 rounded-md"
              >
                {email}
                <button
                  type="button"
                  onClick={() => removeEmailTag(email)}
                  className="text-ad-gray hover:text-ad-dark ml-1 leading-none"
                >
                  ×
                </button>
              </span>
            ))}
            <input
              id="email-tag-input"
              type="text"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              onKeyDown={handleEmailKeyDown}
              onBlur={addEmailTag}
              placeholder={emailTags.length === 0 ? 'メールアドレスを入力してEnter' : ''}
              className="flex-1 min-w-40 text-sm outline-none bg-transparent text-ad-dark placeholder-gray-300"
            />
          </div>
          <p className="text-xs text-ad-gray">Enterキーまたはスペースで確定。×で削除。</p>
          <div className="flex gap-3">
            <select
              value={inviteTeamId}
              onChange={(e) => setInviteTeamId(e.target.value)}
              className="border border-ad-border rounded-lg px-3 py-2 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="">チームを選択</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as 'leader' | 'member')}
              className="border border-ad-border rounded-lg px-3 py-2 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
            >
              <option value="member">メンバー</option>
              <option value="leader">リーダー</option>
            </select>
            <button
              type="submit"
              disabled={inviting || (emailTags.length === 0 && !emailInput.trim()) || !inviteTeamId}
              className="bg-brand text-ad-dark px-5 py-2 rounded-lg text-sm font-semibold hover:bg-brand-dark disabled:opacity-40 transition-all"
            >
              {inviting ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-ad-dark border-t-transparent rounded-full animate-spin" />
                  登録中...
                </span>
              ) : '一括登録'}
            </button>
          </div>
        </form>

        {inviteResults.length > 0 && (
          <div className="mt-4 space-y-1">
            <p className="text-xs font-medium text-ad-gray mb-2">登録結果：</p>
            {inviteResults.map((r) => (
              <div key={r.email} className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg ${
                r.status === 'ok' ? 'bg-green-50 text-green-700' :
                r.status === 'exists' ? 'bg-brand-light text-ad-dark' :
                'bg-red-50 text-red-600'
              }`}>
                <span>{r.status === 'ok' ? '✓' : r.status === 'exists' ? '△' : '✗'}</span>
                <span>{r.email}</span>
                <span className="ml-auto">
                  {r.status === 'ok' ? 'チームに登録しました' :
                   r.status === 'exists' ? '先にユーザーアカウントの作成が必要です' :
                   '登録に失敗しました'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

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
      ) : (
        <div className="space-y-3">
          {teams.map((team) => {
            const teamMembers = members.filter((m) => m.team_id === team.id)
            const isOpen = openTeamId === team.id

            return (
              <div key={team.id} className="bg-white rounded-xl border border-ad-border overflow-hidden">
                <button
                  onClick={() => setOpenTeamId(isOpen ? null : team.id)}
                  className="w-full flex items-center justify-between px-5 py-4 hover:bg-ad-bg transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-ad-dark text-sm">{team.name}</span>
                    <span className="text-xs bg-ad-bg text-ad-gray px-2 py-0.5 rounded-md">
                      {teamMembers.length}人
                    </span>
                  </div>
                  <span className="text-ad-gray text-xs">{isOpen ? '▲' : '▼'}</span>
                </button>

                {isOpen && (
                  <div className="border-t border-ad-border">
                    {teamMembers.length === 0 ? (
                      <div className="px-5 py-6 text-center text-ad-gray text-sm">
                        メンバーがいません
                      </div>
                    ) : (
                      <table className="w-full text-sm">
                        <thead className="bg-ad-bg text-ad-gray text-xs">
                          <tr>
                            <th className="text-left px-5 py-3 font-medium">メールアドレス</th>
                            <th className="text-left px-5 py-3 font-medium">役割</th>
                            <th className="px-5 py-3"></th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-ad-border">
                          {teamMembers.map((m) => (
                            <tr key={m.id} className="hover:bg-ad-bg transition-colors">
                              <td className="px-5 py-3 text-ad-dark">{m.email}</td>
                              <td className="px-5 py-3">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                  m.team_role === 'leader'
                                    ? 'bg-ad-dark text-white'
                                    : 'bg-ad-bg text-ad-gray'
                                }`}>
                                  {m.team_role === 'leader' ? 'Leader' : 'Member'}
                                </span>
                              </td>
                              <td className="px-5 py-3 text-right">
                                {m.team_member_id && (
                                  <button
                                    onClick={() => handleRemoveFromTeam(m.team_member_id!)}
                                    className="text-xs text-ad-gray hover:text-red-500 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                                  >
                                    削除
                                  </button>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </div>
            )
          })}

          {unassignedMembers.length > 0 && (
            <div className="bg-white rounded-xl border border-brand/40 overflow-hidden">
              <button
                onClick={() => setOpenTeamId(openTeamId === 'unassigned' ? null : 'unassigned')}
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-brand-light transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-ad-dark text-sm">未割り当て</span>
                  <span className="text-xs bg-brand text-ad-dark px-2 py-0.5 rounded-md font-medium">
                    {unassignedMembers.length}人
                  </span>
                </div>
                <span className="text-ad-gray text-xs">
                  {openTeamId === 'unassigned' ? '▲' : '▼'}
                </span>
              </button>

              {openTeamId === 'unassigned' && (
                <div className="border-t border-brand/20">
                  <table className="w-full text-sm">
                    <thead className="bg-brand-light text-ad-gray text-xs">
                      <tr>
                        <th className="text-left px-5 py-3 font-medium">メールアドレス</th>
                        <th className="text-left px-5 py-3 font-medium">チームを割り当て</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-ad-border">
                      {unassignedMembers.map((m) => (
                        <tr key={m.id} className="hover:bg-ad-bg transition-colors">
                          <td className="px-5 py-3 text-ad-dark">{m.email}</td>
                          <td className="px-5 py-3">
                            <select
                              defaultValue=""
                              onChange={(e) => {
                                if (e.target.value) handleAssignTeam(m.id, e.target.value, 'member')
                              }}
                              className="border border-ad-border rounded-lg px-2 py-1.5 text-xs text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
                            >
                              <option value="">チームを選択</option>
                              {teams.map((t) => (
                                <option key={t.id} value={t.id}>{t.name}</option>
                              ))}
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
