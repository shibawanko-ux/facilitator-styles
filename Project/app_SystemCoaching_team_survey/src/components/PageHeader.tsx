interface Props {
  title: string
  description?: string
  action?: React.ReactNode
}

export default function PageHeader({ title, description, action }: Props) {
  return (
    <div className="flex items-start justify-between mb-8">
      <div className="flex items-stretch gap-4">
        {/* 黄色の左アクセントバー */}
        <div className="w-1 bg-brand rounded-full flex-shrink-0" />
        <div>
          <h1 className="text-xl font-bold text-ad-dark leading-tight">{title}</h1>
          {description && (
            <p className="text-sm text-ad-gray mt-0.5">{description}</p>
          )}
        </div>
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  )
}
