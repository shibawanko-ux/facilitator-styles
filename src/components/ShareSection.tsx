import { RefObject, useCallback, useState } from 'react';
import { DiagnosisResult } from '../data/types';

interface ShareSectionProps {
  result: DiagnosisResult;
  resultRef: RefObject<HTMLDivElement>;
}

export function ShareSection({ result, resultRef }: ShareSectionProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [shareImageUrl, setShareImageUrl] = useState<string | null>(null);

  // シェア用URL（本番・ローカルどちらでも現在のオリジンを使用）
  const shareUrl = typeof window !== 'undefined' ? window.location.origin : '';

  // シェアテキストを生成（09_sns_share_requirements.md に準拠）
  // 診断結果＋誘導文＋awareness=design 告知＋ハッシュタグ
  const plainCatchcopy = result.type.catchcopy.replace(/\*\*/g, '');
  const shareTextFull = [
    `ファシリスタイル診断の結果、私は「${result.type.name}」スタイルでした！ ${plainCatchcopy}`,
    '',
    `あなたも診断してみて 👉 ${shareUrl}`,
    'ファシリスタイル診断 by awareness=design',
    '#ファシリスタイル #awarenessdesign',
  ].join('\n');

  // X(Twitter)用：URLは intent の url パラメータで渡すため、本文には含めない
  const shareTextForTwitter = [
    `ファシリスタイル診断の結果、私は「${result.type.name}」スタイルでした！ ${plainCatchcopy}`,
    '',
    'あなたも診断してみて 👉',
    '#ファシリスタイル #awarenessdesign',
  ].join('\n');

  // 画像を生成（html2canvas のクローンで背景色が抜けるため onclone でインライン指定）
  const generateImage = useCallback(async () => {
    if (!resultRef.current) return;

    const FORCE_BG = {
      'bg-primary-600': '#0284c7',
      'bg-primary-700': '#0369a1',
      'bg-white': '#ffffff',
      'bg-slate-50': '#f8fafc',
      'bg-slate-100': '#f1f5f9',
      'bg-red-50': '#fef2f2',
      'bg-emerald-50': '#ecfdf5',
      'bg-amber-50': '#fffbeb',
      'bg-sky-50': '#f0f9ff',
    } as const;

    setIsGenerating(true);
    try {
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(resultRef.current, {
        backgroundColor: '#ffffff',
        scale: 3,
        useCORS: true,
        logging: false,
        onclone: (_doc, clone) => {
          const root = clone as HTMLElement;
          root.style.backgroundColor = '#ffffff';
          root.style.opacity = '1';

          (Object.keys(FORCE_BG) as (keyof typeof FORCE_BG)[]).forEach((cls) => {
            clone.querySelectorAll(`[class*="${cls}"]`).forEach((el) => {
              const h = el as HTMLElement;
              h.style.backgroundColor = FORCE_BG[cls];
              h.style.opacity = '1';
            });
          });

          const header = clone.querySelector('[class*="bg-primary-600"]') as HTMLElement | null;
          if (header) {
            header.style.backgroundColor = '#0284c7';
            header.style.opacity = '1';
            header.querySelectorAll('[class*="text-white"]').forEach((el) => {
              (el as HTMLElement).style.color = '#ffffff';
            });
            header.querySelectorAll('[class*="text-primary-200"]').forEach((el) => {
              (el as HTMLElement).style.color = '#bae6fd';
            });
            // 型ピル（4軸タグ）：背景・文字色・角丸を明示して崩れを防ぐ
            header.querySelectorAll('[class*="bg-slate-100"]').forEach((el) => {
              const pill = el as HTMLElement;
              pill.style.backgroundColor = '#f1f5f9';
              pill.style.color = '#334155';
              pill.style.borderRadius = '9999px';
              pill.style.border = '1px solid #e2e8f0';
              pill.style.opacity = '1';
            });
          }

          // カード・説明エリアの背景を確実に
          clone.querySelectorAll('.card, [class*="space-y-4"]').forEach((el) => {
            (el as HTMLElement).style.backgroundColor = '#ffffff';
            (el as HTMLElement).style.opacity = '1';
          });

          // 画像用フッターロゴ（画面上は hidden）：クローン内で表示してキャプチャに含める
          const footerLogo = clone.querySelector('.image-only-footer') as HTMLElement | null;
          if (footerLogo) {
            footerLogo.style.display = 'block';
            footerLogo.style.visibility = 'visible';
            footerLogo.style.backgroundColor = '#ffffff';
          }
        },
      });
      const dataUrl = canvas.toDataURL('image/png');
      setShareImageUrl(dataUrl);
    } catch (error) {
      console.error('Failed to generate image:', error);
      alert('画像の生成に失敗しました');
    } finally {
      setIsGenerating(false);
    }
  }, [resultRef]);

  // 画像をダウンロード
  const downloadImage = useCallback(() => {
    if (!shareImageUrl) return;
    
    const link = document.createElement('a');
    link.href = shareImageUrl;
    link.download = `facilistyle-${result.type.id}.png`;
    link.click();
  }, [shareImageUrl, result.type.id]);

  // X(Twitter)でシェア（URLは別パラメータで渡す）
  const shareOnTwitter = useCallback(() => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareTextForTwitter)}&url=${encodeURIComponent(shareUrl)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [shareTextForTwitter, shareUrl]);

  // Facebookでシェア（全文＋URL）
  const shareOnFacebook = useCallback(() => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(shareTextFull)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [shareTextFull, shareUrl]);

  // LINEでシェア（全文＋URL）
  const shareOnLine = useCallback(() => {
    const url = `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareTextFull)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [shareTextFull, shareUrl]);

  // クリップボードにコピー（告知・URL・ハッシュタグ含む全文）
  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(shareTextFull);
      alert('クリップボードにコピーしました！');
    } catch {
      alert('コピーに失敗しました');
    }
  }, [shareTextFull]);

  return (
    <div>
      {/* SNSシェアボタン */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-slate-700 mb-3">SNSでシェア</h3>
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

          {/* Facebook */}
          <button
            onClick={shareOnFacebook}
            className="flex items-center gap-2 px-4 py-2 bg-[#1877F2] text-white rounded-xl hover:bg-[#166FE5] transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            <span className="text-sm font-medium">Facebook</span>
          </button>

          {/* LINE */}
          <button
            onClick={shareOnLine}
            className="flex items-center gap-2 px-4 py-2 bg-[#00B900] text-white rounded-xl hover:bg-[#00A000] transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63h2.386c.349 0 .63.285.63.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.627-.63.349 0 .631.285.631.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.349 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314" />
            </svg>
            <span className="text-sm font-medium">LINE</span>
          </button>

          {/* コピー */}
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

      {/* 画像保存 */}
      <div>
        <h3 className="text-sm font-medium text-slate-700 mb-3">結果画像を保存</h3>
        
        {!shareImageUrl ? (
          <button
            onClick={generateImage}
            disabled={isGenerating}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-colors ${
              isGenerating
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-primary-100 text-primary-700 hover:bg-primary-200'
            }`}
          >
            {isGenerating ? (
              <>
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-sm font-medium">生成中...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
                <span className="text-sm font-medium">画像を生成</span>
              </>
            )}
          </button>
        ) : (
          <div className="space-y-3">
            <div className="border rounded-xl overflow-hidden">
              <img src={shareImageUrl} alt="診断結果" className="w-full" />
            </div>
            <button
              onClick={downloadImage}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              <span className="text-sm font-medium">ダウンロード</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
