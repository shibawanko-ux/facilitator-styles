import { Link } from 'react-router-dom'
import { AppBrandHeading } from '../components/AppBrandHeading'
import { AppFooter } from '../components/AppFooter'

/** Step 9 では参加入口のプレースホルダー。Step 10 以降でパスコード入力・役割選択を実装 */
export function JoinPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-slate-50">
      <AppBrandHeading />
      <h1 className="text-xl font-bold text-slate-800">参加用URLで参加</h1>
      <p className="mt-4 text-slate-600 text-center">
        参加用URLを共有された方は、そのURLをブラウザで開いてください。
      </p>
      <p className="mt-2 text-sm text-slate-500">
        （パスコード入力・役割選択は次のステップで実装します）
      </p>
      <Link to="/" className="mt-8 text-primary-600 hover:underline">
        TOP に戻る
      </Link>
      <AppFooter />
    </div>
  )
}
