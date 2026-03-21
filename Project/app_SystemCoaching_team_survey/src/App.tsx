import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import { supabase } from './lib/supabase'
import LoginPage from './pages/auth/LoginPage'
import SetPasswordPage from './pages/auth/SetPasswordPage'
import Layout from './components/Layout'
import DashboardPage from './pages/admin/DashboardPage'
import TeamsPage from './pages/admin/TeamsPage'
import MembersPage from './pages/admin/MembersPage'
import SurveysPage from './pages/admin/SurveysPage'
import SurveyAnswerPage from './pages/member/SurveyAnswerPage'
import SurveyThanksPage from './pages/member/SurveyThanksPage'
import ResultsPage from './pages/ResultsPage'

function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    const hash = window.location.hash
    const params = new URLSearchParams(hash.replace('#', '?'))
    const type = params.get('type')

    if (type === 'invite' || type === 'recovery') {
      navigate('/set-password', { replace: true })
    } else {
      navigate('/', { replace: true })
    }
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-500">読み込み中...</p>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">読み込み中...</p>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  useEffect(() => {
    supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        window.location.href = '/set-password'
      }
    })
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/set-password" element={<SetPasswordPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teams"
          element={
            <ProtectedRoute>
              <Layout>
                <TeamsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/members"
          element={
            <ProtectedRoute>
              <Layout>
                <MembersPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/surveys"
          element={
            <ProtectedRoute>
              <Layout>
                <SurveysPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/survey"
          element={
            <ProtectedRoute>
              <Layout>
                <SurveyAnswerPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/results"
          element={
            <ProtectedRoute>
              <Layout>
                <ResultsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/survey/thanks"
          element={
            <ProtectedRoute>
              <Layout>
                <SurveyThanksPage />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
