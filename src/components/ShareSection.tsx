import { useCallback } from 'react';
import { DiagnosisResult } from '../data/types';

interface ShareSectionProps {
  result: DiagnosisResult;
}

export function ShareSection({ result }: ShareSectionProps) {
  // シェア用URL（本番・ローカルどちらでも現在のオリジンを使用）
  const shareUrl = typeof window !== 'undefined' ? window.location.origin : '';

  // シェアテキストを生成（09_sns_share_requirements.md に準拠）
  // 診断結果＋誘導文＋awareness=design 告知＋ハッシュタグ
  const plainCatchcopy = result.type.catchcopy.replace(/\*\*/g, '');
  const shareTextFull = [
    `ファシリテータースタイル診断の結果、私は「${result.type.name}」スタイルでした！ ${plainCatchcopy}`,
    '',
    `あなたも診断してみて 👉 ${shareUrl}`,
    'ファシリテータースタイル診断 by awareness=design',
    '#ファシリテータースタイル #awarenessdesign',
  ].join('\n');

  // X(Twitter)用：URLは intent の url パラメータで渡すため、本文には含めない
  const shareTextForTwitter = [
    `ファシリテータースタイル診断の結果、私は「${result.type.name}」スタイルでした！ ${plainCatchcopy}`,
    '',
    'あなたも診断してみて 👉',
    '#ファシリテータースタイル #awarenessdesign',
  ].join('\n');

  // X(Twitter)でシェア（URLは別パラメータで渡す）
  const shareOnTwitter = useCallback(() => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareTextForTwitter)}&url=${encodeURIComponent(shareUrl)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [shareTextForTwitter, shareUrl]);

  // クリップボードにコピー（告知・URL・ハッシュタグ含む全文）。X/Facebook等に貼り付けてシェア可能
  const copyToClipboard = useCallback(async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareTextFull);
        alert('クリップボードにコピーしました！XやFacebookの投稿欄に貼り付けてシェアできます。');
        return;
      }
      // 非HTTPS等で clipboard API が使えない場合のフォールバック
      const textarea = document.createElement('textarea');
      textarea.value = shareTextFull;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(textarea);
      if (ok) {
        alert('クリップボードにコピーしました！XやFacebookの投稿欄に貼り付けてシェアできます。');
      } else {
        alert('コピーに失敗しました。お手数ですが本文を選択してコピーしてください。');
      }
    } catch {
      alert('コピーに失敗しました');
    }
  }, [shareTextFull]);

  return (
    <div>
      {/* SNSシェアボタン */}
      <div>
        <h3 className="text-sm font-medium text-slate-700 mb-3">SNSでシェア</h3>
        <p className="text-xs text-slate-500 mb-3">コピーしてXやFacebookの投稿欄に貼り付けてシェアできます。</p>
        <div className="flex flex-wrap gap-3">
          {/* X/Twitter */}
          <button
            onClick={shareOnTwitter}
            className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-xl hover:bg-gray-800 transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
            <span className="text-sm font-medium">X</span>
          </button>

          {/* コピー（X/Facebook等に貼り付けてシェア可能・Facebookボタンは投稿文が反映されないため削除） */}
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-2 px-4 py-2 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            <span className="text-sm font-medium">コピー</span>
          </button>
        </div>
      </div>
    </div>
  );
}
