import type { ReactNode } from 'react';

/**
 * 段落（\n\n）と太字（**...**）を解釈して表示するコンポーネント
 * 読みやすさのため、リード文などで使用
 */

interface FormattedTextProps {
  text: string;
  className?: string;
  as?: 'div' | 'p' | 'span';
}

/** **で囲んだ部分を太字、\n\nで段落に分割して表示 */
export function FormattedText({ text, className = '', as: Wrapper = 'div' }: FormattedTextProps) {
  const paragraphs = text.split(/\n\n+/).filter((p) => p.trim());
  if (paragraphs.length === 0) return <Wrapper className={className} />;
  if (paragraphs.length === 1) {
    return <Wrapper className={className}>{parseBold(paragraphs[0])}</Wrapper>;
  }
  return (
    <Wrapper className={className}>
      {paragraphs.map((para, i) => (
        <p key={i} className={i > 0 ? 'mt-4' : ''}>
          {parseBold(para)}
        </p>
      ))}
    </Wrapper>
  );
}

/** 文字列中の **text** を <strong> に変換（React node の配列を返す） */
function parseBold(str: string): ReactNode[] {
  const parts = str.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    const match = part.match(/^\*\*(.+)\*\*$/);
    if (match) return <strong key={i} className="font-semibold text-gray-800">{match[1]}</strong>;
    return part;
  });
}
