# ファシリテーターリフレクション 実装計画

## 1. MVP の範囲

### 含める機能
- ルーム作成（ルーム名・パスコード・メインファシリタイプ・イベント日付・名前）
- 参加（参加用URL ＋ パスコード ＋ 役割選択：メイン／サブ／参加者）
- 評価入力（18項目のスコア ＋ 自由記述。05_evaluation_items.md の E1～F4）
- 全員入力完了の判定と結果表示（集計をメイン、振り返りの問い・アクションは折りたたみ）
- 16タイプのマスタ（診断アプリと同様の id・name を本アプリ内に保持）

### 当面含めない／簡略化
- 振り返りの問い・アクションのテンプレートは、タイプ別の固定文言から開始（傾向別は後拡張）
- ユーザー個別ログイン（メール認証等）は行わない（パスコードのみ）
- ルームの有効期限・削除は後回し

## 2. 技術スタック（想定）

- **フロント**: React + Vite + TypeScript（診断アプリと同様）、Tailwind CSS
- **バックエンド・DB**: Supabase（PostgreSQL、認証はパスコード検証を自前 or Edge Function）
- **ホスティング**: Vercel（フロント）、Supabase（DB・API）

## 3. 実装タスクの順序

### Phase 1: 基盤
- [ ] Supabase プロジェクト作成（無料枠）
- [ ] テーブル作成: rooms, evaluations（04_data_design.md に準拠）
- [ ] RLS ポリシー作成（ルーム単位のアクセス制御）
- [ ] パスコード照合用の Edge Function または API 設計（パスコード入力 → トークン or セッション許可）
- [ ] フロント用 Vite + React + TypeScript プロジェクト初期化（app_Facilitator_reflection 直下に src 等）

### Phase 2: ルーム作成・参加
- [ ] TOP 画面（ルーム作成入口・参加用URL入力入口）
- [ ] ルーム作成画面（ルーム名・パスコード・メインファシリタイプ選択・イベント日付・名前）→ Supabase に保存
- [ ] 参加用URL の生成と共有表示（例: /room/{roomId}/join）
- [ ] 参加画面: パスコード入力 → 照合 → 役割選択（main / sub / participant）→ 評価入力へ

### Phase 3: 評価入力
- [ ] 評価入力画面: 18項目（E1～F4）のスコア（5段階等）＋ 自由記述
- [ ] evaluations への挿入（room_id, role, scores, free_comment）
- [ ] メインの自己評価が 1 件あることを「全員揃った」の条件に含める（必要なら「期待人数」は後拡張）

### Phase 4: 結果表示
- [ ] 結果表示のトリガー: 同一 room_id の evaluations を取得し、メイン 1 件以上で「結果を見る」を許可（または簡易ルールで「全員揃い」を判定）
- [x] 結果画面: 6軸の集計・レーダーチャート、reportAgent レポート（3セクション）を表示
- [ ] 振り返りの問い・アクション提案を折りたたみで表示（まずはタイプ別固定文言でよい）
- [ ] 入力待ち状態の表示（まだ揃っていないとき）

### Phase 5: 仕上げ
- [ ] 16タイプのマスタデータをフロントに配置（診断アプリの facilitatorTypes から id・name を利用）
- [ ] ブランド・ロゴ表示（01 の 1.9 に準拠: テキストロゴ、powered by awareness=design）
- [ ] 環境変数・.env.example の整備（Supabase URL, anon key）
- [ ] 動作確認・軽微な UI 調整

## 4. 参照ドキュメント

- 要件・機能: [01_requirements.md](01_requirements.md)
- データ設計: [04_data_design.md](04_data_design.md)
- 評価項目: [05_evaluation_items.md](05_evaluation_items.md)
- セキュリティ: [06_security.md](06_security.md)

## 5. 更新履歴

| 日付 | 内容 |
|------|------|
| （初版） | MVP 範囲・技術スタック・Phase1～5 のタスク順を記載 |
