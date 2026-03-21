import { useState } from 'react';
import type { TypeCofaciliSummary } from '../data/typeCofaciliSummary';
import { FormattedText } from './FormattedText';

interface CofaciliSectionProps {
  typeId: string;
  summary: TypeCofaciliSummary | undefined;
}

type TabType = 'main' | 'sub';

const COFACILI_POINTS = [
  '事前に役割分担を明確にする',
  '交代のタイミングや合図を決めておく',
  'ワークショップ後に振り返りの時間を確保する',
];

export function CofaciliSection({ summary }: CofaciliSectionProps) {
  const [activeTab, setActiveTab] = useState<TabType>('main');

  return (
    <div>
      {/* タブ（4-A：メイン／サブで1本の文章） */}
      <div className="flex border-b border-slate-200 mb-6">
        <button
          onClick={() => setActiveTab('main')}
          className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'main'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          メインファシリのとき
        </button>
        <button
          onClick={() => setActiveTab('sub')}
          className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'sub'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          サブファシリのとき
        </button>
      </div>

      {/* タブごとの内容：1本の文章＋コーファシリテーションのポイント */}
      {summary && (
        <div>
          <div className="p-5 bg-slate-50 rounded-xl border border-slate-100 mb-6">
            <FormattedText
              text={activeTab === 'main' ? summary.asMain : summary.asSub}
              className="text-slate-700 leading-relaxed"
            />
          </div>
          {/* コーファシリテーションのポイント（メイン／サブそれぞれの文脈内に表示） */}
          <div className="p-4 bg-sky-50 rounded-xl border border-sky-100">
            <h4 className="text-sm font-semibold text-sky-800 mb-2">コーファシリテーションのポイント</h4>
            <ul className="text-sm text-sky-700 space-y-1">
              {COFACILI_POINTS.map((point, index) => (
                <li key={index}>• {point}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
