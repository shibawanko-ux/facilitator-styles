import { useState, useEffect } from 'react'
import { supabase } from '../../lib/supabase'
import PageHeader from '../../components/PageHeader'

interface Team {
  id: string
  name: string
  created_at: string
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [newTeamName, setNewTeamName] = useState('')
  const [adding, setAdding] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTeams()
  }, [])

  const fetchTeams = async () => {
    const { data } = await supabase
      .from('teams')
      .select('*')
      .order('created_at', { ascending: false })
    setTeams(data ?? [])
    setLoading(false)
  }

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTeamName.trim()) return
    setAdding(true)
    setError('')

    const { error } = await supabase
      .from('teams')
      .insert({ name: newTeamName.trim() })

    if (error) {
      setError('チームの追加に失敗しました')
    } else {
      setNewTeamName('')
      await fetchTeams()
    }
    setAdding(false)
  }

  const handleEdit = async (id: string) => {
    if (!editingName.trim()) return
    setError('')

    const { error } = await supabase
      .from('teams')
      .update({ name: editingName.trim() })
      .eq('id', id)

    if (error) {
      setError('チーム名の更新に失敗しました')
    } else {
      setEditingId(null)
      await fetchTeams()
    }
  }

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`「${name}」を削除しますか？`)) return
    setError('')

    const { error } = await supabase
      .from('teams')
      .delete()
      .eq('id', id)

    if (error) {
      setError('チームの削除に失敗しました')
    } else {
      await fetchTeams()
    }
  }

  return (
    <div className="p-8">
      <PageHeader title="チーム管理" description="チームの追加・編集・削除" />

      {/* チーム追加フォーム */}
      <div className="bg-white rounded-xl border border-ad-border p-5 mb-6">
        <h3 className="font-semibold text-ad-dark mb-3 text-sm">新しいチームを追加</h3>
        <form onSubmit={handleAdd} className="flex gap-3">
          <input
            type="text"
            value={newTeamName}
            onChange={(e) => setNewTeamName(e.target.value)}
            placeholder="チーム名を入力"
            className="flex-1 border border-ad-border rounded-lg px-4 py-2.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all placeholder-gray-300"
          />
          <button
            type="submit"
            disabled={adding || !newTeamName.trim()}
            className="bg-brand text-ad-dark px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-brand-dark disabled:opacity-40 transition-all"
          >
            {adding ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-ad-dark border-t-transparent rounded-full animate-spin" />
                追加中...
              </span>
            ) : '追加'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* チーム一覧 */}
      <div className="bg-white rounded-xl border border-ad-border">
        <div className="px-5 py-4 border-b border-ad-border">
          <h3 className="font-semibold text-ad-dark text-sm">チーム一覧（{teams.length}件）</h3>
        </div>

        {loading ? (
          <div className="p-10 flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-brand border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-ad-gray">読み込み中...</p>
          </div>
        ) : teams.length === 0 ? (
          <div className="p-10 text-center text-ad-gray">
            <p className="text-sm">まだチームが登録されていません</p>
          </div>
        ) : (
          <ul className="divide-y divide-ad-border">
            {teams.map((team) => (
              <li key={team.id} className="px-5 py-3.5 flex items-center gap-3">
                {editingId === team.id ? (
                  <>
                    <input
                      type="text"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      className="flex-1 border border-ad-border rounded-lg px-3 py-1.5 text-sm text-ad-dark focus:outline-none focus:ring-2 focus:ring-brand"
                      autoFocus
                    />
                    <button
                      onClick={() => handleEdit(team.id)}
                      className="text-xs font-semibold text-ad-dark bg-brand px-3 py-1.5 rounded-lg hover:bg-brand-dark"
                    >
                      保存
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-xs text-ad-gray hover:text-ad-dark px-2"
                    >
                      キャンセル
                    </button>
                  </>
                ) : (
                  <>
                    <span className="flex-1 text-sm font-medium text-ad-dark">{team.name}</span>
                    <span className="text-xs text-ad-gray">
                      {new Date(team.created_at).toLocaleDateString('ja-JP')}
                    </span>
                    <button
                      onClick={() => { setEditingId(team.id); setEditingName(team.name) }}
                      className="text-xs text-ad-gray hover:text-ad-dark px-2 py-1 rounded hover:bg-ad-bg transition-colors"
                    >
                      編集
                    </button>
                    <button
                      onClick={() => handleDelete(team.id, team.name)}
                      className="text-xs text-ad-gray hover:text-red-500 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                    >
                      削除
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
