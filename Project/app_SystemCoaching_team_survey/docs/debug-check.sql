-- ============================================
-- 診断SQL：データ表示されない原因を調べる
-- Supabase SQL Editor で実行して結果を確認
-- ============================================

-- 1. ユーザー確認（roleがadminになっているか）
SELECT id, email, role FROM users;

-- 2. テストデータ確認
SELECT 'teams' AS table_name, count(*) FROM teams
UNION ALL
SELECT 'projects', count(*) FROM projects
UNION ALL
SELECT 'surveys', count(*) FROM surveys
UNION ALL
SELECT 'questions', count(*) FROM questions
UNION ALL
SELECT 'responses', count(*) FROM responses;

-- 3. RLSポリシー確認（読み取りをブロックしていないか）
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
