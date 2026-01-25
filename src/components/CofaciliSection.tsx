import { useState } from 'react';
import { CofaciliHint } from '../data/types';

interface CofaciliSectionProps {
  hints: {
    intervention: CofaciliHint;
    perception: CofaciliHint;
    judgment: CofaciliHint;
    engagement: CofaciliHint;
  };
}

type TabType = 'main' | 'sub';

export function CofaciliSection({ hints }: CofaciliSectionProps) {
  const [activeTab, setActiveTab] = useState<TabType>('main');

  const hintsList = [
    { key: 'intervention', name: '介入スタイル', hint: hints.intervention },
    { key: 'perception', name: '知覚対象', hint: hints.perception },
    { key: 'judgment', name: '判断基準', hint: hints.judgment },
    { key: 'engagement', name: '場への関わり', hint: hints.engagement },
  ];

  return (
    <div>
      {/* タブ */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('main')}
          className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'main'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          メインファシリのとき
        </button>
        <button
          onClick={() => setActiveTab('sub')}
          className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'sub'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          サブファシリのとき
        </button>
      </div>

      {/* コンテンツ */}
      <div className="space-y-6">
        {hintsList.map(({ key, name, hint }) => (
          <div key={key} className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs text-gray-500">{name}</span>
              <span className="px-2 py-0.5 bg-white rounded text-xs font-medium text-gray-700">
                {hint.label}
              </span>
            </div>

            {activeTab === 'main' ? (
              <div className="space-y-3">
                <div>
                  <h4 className="text-xs font-medium text-gray-500 mb-1">対極タイプと組むメリット</h4>
                  <p className="text-sm text-gray-700">{hint.asMain.benefit}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-gray-500 mb-1">意識すること</h4>
                  <p className="text-sm text-gray-700">{hint.asMain.focus}</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <h4 className="text-xs font-medium text-gray-500 mb-1">同じタイプのメインと組むとき</h4>
                  <p className="text-sm text-gray-700">{hint.asSub.withSameType}</p>
                </div>
                <div>
                  <h4 className="text-xs font-medium text-gray-500 mb-1">対極タイプのメインと組むとき</h4>
                  <p className="text-sm text-gray-700">{hint.asSub.withOppositeType}</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 補足 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-800 mb-2">コーファシリテーションのポイント</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 事前に役割分担を明確にする</li>
          <li>• 交代のタイミングや合図を決めておく</li>
          <li>• ワークショップ後に振り返りの時間を確保する</li>
        </ul>
      </div>
    </div>
  );
}
