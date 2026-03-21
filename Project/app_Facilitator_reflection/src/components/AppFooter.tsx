/** 全画面で統一するフッター表記 */
export function AppFooter({ className = '' }: { className?: string }) {
  return (
    <p className={`mt-8 text-sm text-slate-400 ${className}`.trim()}>powered by awareness=design</p>
  )
}
