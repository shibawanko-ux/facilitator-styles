-- ============================================
-- テストチームA メンバー割り当てSQL
-- Supabase SQL Editor に貼り付けて実行してください
-- leader・member ロールのユーザーをテストチームAに割り当てます
-- ============================================

DO $$
DECLARE
  v_leader_id uuid;
  v_member_id uuid;
BEGIN
  -- leaderロールのユーザーを取得
  SELECT id INTO v_leader_id FROM public.users WHERE role = 'leader' LIMIT 1;
  -- memberロールのユーザーを取得
  SELECT id INTO v_member_id FROM public.users WHERE role = 'member' LIMIT 1;

  -- leaderをテストチームAに割り当て
  IF v_leader_id IS NOT NULL THEN
    DELETE FROM team_members WHERE user_id = v_leader_id;
    INSERT INTO team_members (user_id, team_id, role)
      VALUES (v_leader_id, 'aaaaaaaa-0000-0000-0000-000000000001', 'leader');
    RAISE NOTICE 'leader を割り当て: %', v_leader_id;
  ELSE
    RAISE NOTICE 'leaderユーザーが見つかりません';
  END IF;

  -- memberをテストチームAに割り当て
  IF v_member_id IS NOT NULL THEN
    DELETE FROM team_members WHERE user_id = v_member_id;
    INSERT INTO team_members (user_id, team_id, role)
      VALUES (v_member_id, 'aaaaaaaa-0000-0000-0000-000000000001', 'member');
    RAISE NOTICE 'member を割り当て: %', v_member_id;
  ELSE
    RAISE NOTICE 'memberユーザーが見つかりません';
  END IF;
END $$;

-- 確認クエリ
SELECT
  u.email,
  u.role AS user_role,
  tm.role AS team_role,
  t.name AS team_name
FROM team_members tm
JOIN public.users u ON u.id = tm.user_id
JOIN teams t ON t.id = tm.team_id
ORDER BY t.name, tm.role;
