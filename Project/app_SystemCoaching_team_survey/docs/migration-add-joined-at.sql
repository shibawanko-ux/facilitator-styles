-- ============================================
-- team_members に joined_at カラムを追加
-- Supabase SQL Editor に貼り付けて実行してください
-- ============================================

ALTER TABLE team_members
ADD COLUMN IF NOT EXISTS joined_at TIMESTAMPTZ NOT NULL DEFAULT now();

-- 既存レコードは追加日時を now() で設定済み（DEFAULT が効く）
-- テストデータのメンバーは過去の日付に設定しておく（アンケートより前に参加している必要がある）
UPDATE team_members
SET joined_at = '2026-01-01 00:00:00+09'
WHERE joined_at > '2026-03-01';

-- 確認
SELECT u.email, tm.role, tm.joined_at, t.name AS team_name
FROM team_members tm
JOIN public.users u ON u.id = tm.user_id
JOIN teams t ON t.id = tm.team_id
ORDER BY tm.joined_at;
