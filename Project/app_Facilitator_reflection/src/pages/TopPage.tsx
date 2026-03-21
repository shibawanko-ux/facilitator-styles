import { Link } from 'react-router-dom'
import { AppFooter } from '../components/AppFooter'

export function TopPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
      <h1 className="text-2xl font-bold text-slate-800">
        ファシリテーターリフレクション
      </h1>
      <p className="mt-2 text-slate-600 text-center">
        ルームを作って振り返りを始めるか、参加用URLで参加できます。
      </p>
      <nav className="mt-8 flex flex-col sm:flex-row gap-4">
        <Link
          to="/create"
          className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition shadow-sm"
        >
          ルームを作る
        </Link>
        <Link
          to="/join"
          className="px-6 py-3 bg-slate-200 text-slate-800 rounded-xl font-medium hover:bg-slate-300 transition"
        >
          参加用URLで参加
        </Link>
      </nav>
      <AppFooter />
    </div>
  )
}
