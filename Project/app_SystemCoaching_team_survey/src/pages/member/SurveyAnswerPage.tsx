import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../hooks/useAuth'

interface Question {
  id: string
  text: string
  axis: string
  type: 'scale' | 'free_text'
  survey_type: 'common' | 'pre_only' | 'post_only'
  order: number
}

interface Survey {
  id: string
  session_number: number
  timing: 'pre' | 'post'
  is_final: boolean
  project_id: string
}

const SCALE_LABELS = [
  '',
  '全くあてはまらない',
  'あてはまらない',
  'どちらかといえばあてはまらない',
  'どちらかといえばあてはまる',
  'あてはまる',
  '非常にあてはまる',
]

export default function SurveyAnswerPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [survey, setSurvey] = useState<Survey | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<string, number | string>>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [alreadyAnswered, setAlreadyAnswered] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user) fetchActiveSurvey()
  }, [user])

  const fetchActiveSurvey = async () => {
    const { data: teamMember } = await supabase
      .from('team_members')
      .select('team_id')
      .eq('user_id', user!.id)
      .single()

    if (!teamMember) { setLoading(false); return }

    const { data: project } = await supabase
      .from('projects')
      .select('id')
      .eq('team_id', teamMember.team_id)
      .eq('status', 'active')
      .single()

    if (!project) { setLoading(false); return }

    const { data: surveyData } = await supabase
      .from('surveys')
      .select('*')
      .eq('project_id', project.id)
      .eq('status', 'active')
      .order('session_number')
      .limit(1)
      .single()

    if (!surveyData) { setLoading(false); return }

    setSurvey(surveyData)

    const { data: existing } = await supabase
      .from('responses')
      .select('id')
      .eq('survey_id', surveyData.id)
      .eq('user_id', user!.id)
      .limit(1)

    if (existing && existing.length > 0) {
      setAlreadyAnswered(true)
      setLoading(false)
      return
    }

    const surveyTypes = ['common', surveyData.timing === 'pre' ? 'pre_only' : 'post_only']
    const { data: questionsData } = await supabase
      .from('questions')
      .select('*')
      .in('survey_type', surveyTypes)
      .order('display_order')

    const filtered = (questionsData ?? []).filter((q) => {
      if (q.survey_type === 'post_only' && !surveyData.is_final) return false
      return true
    })

    setQuestions(filtered)
    setLoading(false)
  }

  const handleScaleChange = (questionId: string, value: number) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
    setError('')
  }

  const handleTextChange = (questionId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async () => {
    if (!survey || !user) return

    const unanswered = questions.filter((q) => {
      if (q.type === 'scale') return !answers[q.id]
      return false
    })
    if (unanswered.length > 0) {
      setError(`まだ${unanswered.length}問の評価が未回答です`)
      return
    }

    setSubmitting(true)
    setError('')

    const records = questions.map((q) => ({
      survey_id: survey.id,
      user_id: user.id,
      question_id: q.id,
      score: q.type === 'scale' ? (answers[q.id] as number) : null,
      free_text: q.type === 'free_text' ? (answers[q.id] as string) || null : null,
    }))

    const { error } = await supabase.from('responses').insert(records)

    if (error) {
      setError('回答の送信に失敗しました。もう一度お試しください。')
      setSubmitting(false)
    } else {
      navigate('/survey/thanks')
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3">
        <div className="w-8 h-8 border-2 border-brand border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-ad-gray">読み込み中...</p>
      </div>
    )
  }

  if (!survey) {
    return (
      <div className="flex items-center justify-center py-20 px-4">
        <div className="bg-white rounded-xl border border-ad-border p-10 text-center max-w-sm w-full">
          <div className="w-12 h-12 bg-ad-bg rounded-full flex items-center justify-center mx-auto mb-4">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="2" y="2" width="16" height="16" rx="2" stroke="#666" strokeWidth="1.5"/>
              <path d="M6 7h8M6 10h8M6 13h4" stroke="#666" strokeWidth="1.3" strokeLinecap="round"/>
            </svg>
          </div>
          <h2 className="text-sm font-semibold text-ad-dark mb-2">現在回答できるアンケートはありません</h2>
          <p className="text-ad-gray text-xs">アンケートが配信されたらこちらに表示されます</p>
        </div>
      </div>
    )
  }

  if (alreadyAnswered) {
    return (
      <div className="flex items-center justify-center py-20 px-4">
        <div className="bg-white rounded-xl border border-ad-border p-10 text-center max-w-sm w-full">
          <div className="w-12 h-12 bg-brand-light rounded-full flex items-center justify-center mx-auto mb-4">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10l5 5 7-7" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2 className="text-sm font-semibold text-ad-dark mb-2">回答済みです</h2>
          <p className="text-ad-gray text-xs">このアンケートはすでに回答が完了しています</p>
        </div>
      </div>
    )
  }

  const scaleQuestions = questions.filter((q) => q.type === 'scale')
  const freeTextQuestions = questions.filter((q) => q.type === 'free_text')
  const answeredCount = scaleQuestions.filter((q) => answers[q.id]).length
  const progress = scaleQuestions.length > 0 ? (answeredCount / scaleQuestions.length) * 100 : 0

  return (
    <div className="py-8 px-4">
      <div className="max-w-xl mx-auto">

        {/* ヘッダー */}
        <div className="mb-6">
          <p className="text-[10px] font-semibold text-ad-gray tracking-widest uppercase mb-1">awareness:design</p>
          <h1 className="text-lg font-bold text-ad-dark">チーム状態アンケート</h1>
          <p className="text-sm text-ad-gray mt-0.5">
            第{survey.session_number}回 — {survey.timing === 'pre' ? '事前' : '事後'}
          </p>
        </div>

        {/* 進捗バー */}
        <div className="bg-white rounded-xl border border-ad-border px-5 py-4 mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-ad-gray">回答の進捗</span>
            <span className="text-xs font-semibold text-ad-dark">{answeredCount} / {scaleQuestions.length} 問</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 説明 */}
        <div className="bg-brand-light border border-brand/30 rounded-xl px-5 py-4 mb-5">
          <p className="text-sm text-ad-dark leading-relaxed">
            「参加チーム」とは、今回のシステムコーチングに参加しているチームを指します。<br />
            各項目について、現在のチームの状態にどれくらいあてはまるかを6段階で選んでください。
          </p>
        </div>

        {/* 評価質問 */}
        <div className="space-y-4 mb-5">
          {scaleQuestions.map((q, index) => {
            const isAnswered = !!answers[q.id]
            return (
              <div
                key={q.id}
                className={`bg-white rounded-xl border transition-all ${
                  isAnswered ? 'border-brand/40' : 'border-ad-border'
                }`}
              >
                <div className="flex items-start gap-3 p-5 pb-3">
                  <span className={`flex-shrink-0 w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center mt-0.5 ${
                    isAnswered ? 'bg-brand text-ad-dark' : 'bg-gray-100 text-ad-gray'
                  }`}>
                    {isAnswered ? '✓' : index + 1}
                  </span>
                  <p className="text-sm text-ad-dark leading-relaxed">{q.text}</p>
                </div>

                <div className="space-y-1 px-5 pb-4 pl-14">
                  {[1, 2, 3, 4, 5, 6].map((val) => (
                    <button
                      key={val}
                      onClick={() => handleScaleChange(q.id, val)}
                      className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg border text-left transition-all ${
                        answers[q.id] === val
                          ? 'border-brand bg-brand-light'
                          : 'border-ad-border hover:border-gray-300 hover:bg-ad-bg'
                      }`}
                    >
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                        answers[q.id] === val ? 'bg-brand text-ad-dark' : 'bg-gray-100 text-ad-gray'
                      }`}>
                        {val}
                      </span>
                      <span className={`text-sm ${answers[q.id] === val ? 'text-ad-dark font-medium' : 'text-ad-gray'}`}>
                        {SCALE_LABELS[val]}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        {/* 自由記述 */}
        {freeTextQuestions.length > 0 && (
          <div className="space-y-4 mb-5">
            <h2 className="text-xs font-semibold text-ad-gray px-1 uppercase tracking-wide">自由記述（任意）</h2>
            {freeTextQuestions.map((q, index) => (
              <div key={q.id} className="bg-white rounded-xl border border-ad-border p-5">
                <p className="text-sm text-ad-dark mb-3">
                  <span className="text-ad-gray mr-2 text-xs">Q{scaleQuestions.length + index + 1}</span>
                  {q.text}
                </p>
                <textarea
                  value={(answers[q.id] as string) || ''}
                  onChange={(e) => handleTextChange(q.id, e.target.value)}
                  placeholder="自由に記述してください"
                  rows={4}
                  className="w-full border border-ad-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent resize-none transition-all text-ad-dark placeholder-gray-300"
                />
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={submitting}
          className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
            progress === 100
              ? 'bg-brand text-ad-dark hover:bg-brand-dark'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          } disabled:opacity-50`}
        >
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-ad-dark border-t-transparent rounded-full animate-spin" />
              送信中...
            </span>
          ) : progress === 100 ? '回答を送信する' : `あと ${scaleQuestions.length - answeredCount} 問回答してください`}
        </button>

        <p className="text-center text-xs text-ad-gray mt-4">回答は一度送信すると変更できません</p>
      </div>
    </div>
  )
}
