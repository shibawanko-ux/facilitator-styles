-- ============================================
-- テストデータ 挿入SQL
-- Supabase SQL Editor に貼り付けて実行してください
-- 削除するときは test-data-delete.sql を使用
-- ============================================

-- チーム
INSERT INTO teams (id, name, created_at) VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001', 'テストチームA', now())
ON CONFLICT (id) DO NOTHING;

-- プロジェクト
INSERT INTO projects (id, team_id, name, status, created_at) VALUES
  ('bbbbbbbb-0000-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000001', '2026年春', 'active', now())
ON CONFLICT (id) DO NOTHING;

-- アンケート（3回分・日付が異なるので折れ線グラフに反映される）
INSERT INTO surveys (id, project_id, session_number, timing, is_final, status, created_at) VALUES
  ('cccccccc-0000-0000-0000-000000000001', 'bbbbbbbb-0000-0000-0000-000000000001', 1, 'pre',  false, 'closed', '2026-03-01 10:00:00+09'),
  ('cccccccc-0000-0000-0000-000000000002', 'bbbbbbbb-0000-0000-0000-000000000001', 1, 'post', false, 'closed', '2026-03-08 10:00:00+09'),
  ('cccccccc-0000-0000-0000-000000000003', 'bbbbbbbb-0000-0000-0000-000000000001', 2, 'pre',  false, 'closed', '2026-03-15 10:00:00+09')
ON CONFLICT (id) DO NOTHING;

-- 質問（18問）
INSERT INTO questions (id, text, axis, type, survey_type, display_order, is_reverse) VALUES
  ('dddddddd-0000-0000-0000-000000000001', 'チームが向かう方向を、メンバー全員で共有できている',           'alignment',    'scale', 'common',  1, false),
  ('dddddddd-0000-0000-0000-000000000002', 'チームの目標に対して、自分ごととして取り組めている',           'alignment',    'scale', 'common',  2, false),
  ('dddddddd-0000-0000-0000-000000000003', '成果が出ないとき、チーム全員で原因を考えようとする',           'alignment',    'scale', 'common',  3, false),
  ('dddddddd-0000-0000-0000-000000000004', 'チームメンバーに、本音で話せる関係がある',                     'relationship', 'scale', 'common',  4, false),
  ('dddddddd-0000-0000-0000-000000000005', '困ったときに、チームメンバーに頼ることができる',               'relationship', 'scale', 'common',  5, false),
  ('dddddddd-0000-0000-0000-000000000006', 'メンバーそれぞれの強みや役割を、お互いに理解している',         'relationship', 'scale', 'common',  6, false),
  ('dddddddd-0000-0000-0000-000000000007', '仕事の進め方について、率直に意見を言い合える',                 'conflict',     'scale', 'common',  7, false),
  ('dddddddd-0000-0000-0000-000000000008', 'チーム内に、個人間のわだかまりや緊張感がある',                 'conflict',     'scale', 'common',  8, true),
  ('dddddddd-0000-0000-0000-000000000009', '意見の違いが、良い議論やアイデアにつながっている',             'conflict',     'scale', 'common',  9, false),
  ('dddddddd-0000-0000-0000-000000000010', '自分の仕事がチーム全体にどう影響するか、意識して動いている',   'system',       'scale', 'common', 10, false),
  ('dddddddd-0000-0000-0000-000000000011', '「私vsあなた」ではなく「私たちの問題」として考えられている',   'system',       'scale', 'common', 11, false),
  ('dddddddd-0000-0000-0000-000000000012', 'チームの一員であることに、意味ややりがいを感じている',         'system',       'scale', 'common', 12, false),
  ('dddddddd-0000-0000-0000-000000000013', 'チームでは、さまざまなメンバーが発言できている',               'voice',        'scale', 'common', 13, false),
  ('dddddddd-0000-0000-0000-000000000014', '少数派や普段静かなメンバーの意見も、大切にされている',         'voice',        'scale', 'common', 14, false),
  ('dddddddd-0000-0000-0000-000000000015', '自分の意見を、安心してチームで伝えられる',                     'voice',        'scale', 'common', 15, false),
  ('dddddddd-0000-0000-0000-000000000016', 'ミスや失敗を、チームで正直に話せる雰囲気がある',               'safety',       'scale', 'common', 16, false),
  ('dddddddd-0000-0000-0000-000000000017', '新しいアイデアを出しても、否定されない安心感がある',           'safety',       'scale', 'common', 17, false),
  ('dddddddd-0000-0000-0000-000000000018', '「おかしい」と思ったことを、声に上げられる',                   'safety',       'scale', 'common', 18, false)
ON CONFLICT (id) DO NOTHING;

-- 回答データ（ユーザーIDは自動取得）
-- スコアの変化: 第1回事前(低) → 第1回事後(中) → 第2回事前(高) で上昇傾向を表現
DO $$
DECLARE
  v_user_id uuid;
BEGIN
  SELECT id INTO v_user_id FROM auth.users LIMIT 1;

  -- 第1回事前（スコア低め: 3〜4）
  INSERT INTO responses (survey_id, user_id, question_id, score) VALUES
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000001', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000002', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000003', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000004', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000005', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000006', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000007', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000008', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000009', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000010', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000011', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000012', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000013', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000014', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000015', 4),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000016', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000017', 3),
    ('cccccccc-0000-0000-0000-000000000001', v_user_id, 'dddddddd-0000-0000-0000-000000000018', 4)
  ON CONFLICT DO NOTHING;

  -- 第1回事後（スコア中程度: 4〜5）
  INSERT INTO responses (survey_id, user_id, question_id, score) VALUES
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000001', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000002', 5),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000003', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000004', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000005', 5),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000006', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000007', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000008', 3),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000009', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000010', 5),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000011', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000012', 5),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000013', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000014', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000015', 5),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000016', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000017', 4),
    ('cccccccc-0000-0000-0000-000000000002', v_user_id, 'dddddddd-0000-0000-0000-000000000018', 5)
  ON CONFLICT DO NOTHING;

  -- 第2回事前（スコア高め: 5〜6）
  INSERT INTO responses (survey_id, user_id, question_id, score) VALUES
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000001', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000002', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000003', 6),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000004', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000005', 6),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000006', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000007', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000008', 2),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000009', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000010', 6),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000011', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000012', 6),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000013', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000014', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000015', 6),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000016', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000017', 5),
    ('cccccccc-0000-0000-0000-000000000003', v_user_id, 'dddddddd-0000-0000-0000-000000000018', 6)
  ON CONFLICT DO NOTHING;
END $$;
