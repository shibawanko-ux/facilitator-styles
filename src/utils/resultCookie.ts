/**
 * 診断結果スタイルIDのクッキー保存・読み取り
 * 要件: 01_requirements.md 3.2 診断結果の保持とTOPでの✓表示
 */
const COOKIE_NAME = 'fs_result';
const MAX_AGE_DAYS = 365;
const PATH = '/';

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/[^a-z0-9_-]/gi, (c) => '\\' + c) + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

function setCookie(name: string, value: string, maxAgeDays: number, path: string): void {
  if (typeof document === 'undefined') return;
  const maxAge = maxAgeDays * 24 * 60 * 60;
  document.cookie = `${name}=${encodeURIComponent(value)}; max-age=${maxAge}; path=${path}; SameSite=Lax`;
}

/** 保存された診断結果のスタイルIDを取得。未設定なら null */
export function getResultTypeId(): string | null {
  return getCookie(COOKIE_NAME);
}

/** 診断結果のスタイルIDをクッキーに保存（上書き） */
export function setResultTypeId(typeId: string): void {
  setCookie(COOKIE_NAME, typeId, MAX_AGE_DAYS, PATH);
}
