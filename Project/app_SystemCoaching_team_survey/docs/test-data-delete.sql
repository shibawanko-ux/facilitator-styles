-- ============================================
-- テストデータ 削除SQL
-- Supabase SQL Editor に貼り付けて実行してください
-- ============================================

DELETE FROM responses WHERE survey_id IN (
  'cccccccc-0000-0000-0000-000000000001',
  'cccccccc-0000-0000-0000-000000000002',
  'cccccccc-0000-0000-0000-000000000003'
);

DELETE FROM surveys WHERE project_id = 'bbbbbbbb-0000-0000-0000-000000000001';

DELETE FROM questions WHERE id LIKE 'dddddddd-0000-0000-0000-%';

DELETE FROM projects WHERE id = 'bbbbbbbb-0000-0000-0000-000000000001';

DELETE FROM team_members WHERE team_id = 'aaaaaaaa-0000-0000-0000-000000000001';
-- ※ 上記でteam_membersからも削除されます

DELETE FROM teams WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001';
