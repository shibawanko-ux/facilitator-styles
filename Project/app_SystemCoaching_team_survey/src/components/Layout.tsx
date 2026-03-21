import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

// SVG Icons
const IconDashboard = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
  </svg>
)

const IconTeam = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <circle cx="8" cy="5" r="2.5" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M3 13c0-2.761 2.239-5 5-5s5 2.239 5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <circle cx="13" cy="5" r="1.5" stroke="currentColor" strokeWidth="1.3"/>
    <path d="M14.5 12c0-1.657-1.119-3-2.5-3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
)

const IconMember = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <circle cx="8" cy="5.5" r="3" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M2 14c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
)

const IconSurvey = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <rect x="2" y="1.5" width="12" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M5 5.5h6M5 8h6M5 10.5h4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
)

const IconChart = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <path d="M2 12L6 7.5L9.5 10L14 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M2 14h12" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
)

const IconAnswer = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
    <rect x="2" y="1.5" width="10" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M5 5.5h4M5 8h4M5 10.5h2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
    <path d="M10 11l1.5 1.5 2.5-2.5" stroke="#ffcc00" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const adminNavItems = [
  { to: '/', label: 'ダッシュボード', icon: <IconDashboard /> },
  { to: '/teams', label: 'チーム管理', icon: <IconTeam /> },
  { to: '/members', label: 'メンバー管理', icon: <IconMember /> },
  { to: '/surveys', label: 'アンケート管理', icon: <IconSurvey /> },
]

const leaderNavItems = [
  { to: '/', label: 'ダッシュボード', icon: <IconDashboard /> },
  { to: '/results', label: 'チームの結果', icon: <IconChart /> },
]

const memberNavItems = [
  { to: '/', label: 'ダッシュボード', icon: <IconDashboard /> },
  { to: '/survey', label: 'アンケート回答', icon: <IconAnswer /> },
  { to: '/results', label: 'チームの結果', icon: <IconChart /> },
]

const roleBadge = (role: string | undefined) => {
  if (role === 'admin') return { label: 'Admin', cls: 'bg-brand text-ad-dark' }
  if (role === 'leader') return { label: 'Leader', cls: 'bg-white/20 text-white' }
  return { label: 'Member', cls: 'bg-white/10 text-white/60' }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const navItems =
    user?.role === 'admin' ? adminNavItems
    : user?.role === 'leader' ? leaderNavItems
    : memberNavItems

  const badge = roleBadge(user?.role)

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex">
      {/* サイドバー — ダーク */}
      <aside className="w-56 bg-ad-dark flex flex-col flex-shrink-0">

        {/* ブランドロゴ */}
        <div className="px-5 pt-6 pb-5 border-b border-white/10">
          <div className="flex items-baseline gap-0 leading-none">
            <span className="text-[15px] font-bold text-white tracking-tight">awareness</span>
            <span className="text-[15px] font-bold text-brand">:</span>
            <span className="text-[15px] font-bold text-white tracking-tight">design</span>
          </div>
          <p className="text-[11px] text-white/30 mt-1.5 tracking-wide">Team Survey</p>
        </div>

        {/* ナビゲーション */}
        <nav className="flex-1 px-2 py-4 space-y-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13px] transition-all ${
                  isActive
                    ? 'bg-brand text-ad-dark font-semibold'
                    : 'text-white/50 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <span className="flex-shrink-0">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* ユーザー情報 */}
        <div className="px-3 py-3 border-t border-white/10">
          <div className="px-3 py-2.5 mb-1">
            <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded mb-1.5 ${badge.cls}`}>
              {badge.label}
            </span>
            <p className="text-[11px] text-white/30 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleSignOut}
            className="w-full text-left px-3 py-2 text-[12px] text-white/30 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            ログアウト
          </button>
        </div>
      </aside>

      {/* メインコンテンツ */}
      <main className="flex-1 overflow-auto bg-[#f7f7f5]">
        {children}
      </main>
    </div>
  )
}
