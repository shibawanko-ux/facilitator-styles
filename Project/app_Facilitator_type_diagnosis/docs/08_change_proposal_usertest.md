# ユーザーテスト改善の変更提案

ユーザーテストで判明した「回答が2・3・4に偏る」「結果タイプの振り幅が小さい」を解消するための変更ファイル一覧と修正のポイントです。

---

## 1. 課題の整理

| 課題 | 内容 |
|------|------|
| 回答形式の偏り | 5段階のうち 1・5 が選ばれにくく、2・3・4 に集中しがち |
| 結果の振り幅 | 軸スコアが中央付近に集まり、16タイプの結果が偏る |

---

## 2. 案別の変更ファイル一覧

### 案A: 4段階化（中立をなくす）

- **概要**: 選択肢を4つにし、「どちらとも言えない」を廃止。スコアは 1〜4、軸合計 8〜32、中央 20 で A/B 判定。
- **変更するファイル**:
  - `docs/01_requirements.md` … 2.4 回答形式を4段階に、2.5 スコア範囲を 8〜32・中央20 に更新
  - `docs/02_questions.md` … 回答形式の説明を4段階に変更
  - `src/data/types.ts` … `Answer.score` のコメントを 1–4 に（型は number のまま）
  - `src/components/QuestionPage.tsx` … `scaleLabels` を4段階に、ボタン4個に変更
  - `src/utils/scoring.ts` … 軸スコア範囲 8–32、中央 20 に合わせて `getTendencyType` の閾値（例: score <= 19 で A）、`getTendencyStrength` の `maxDistance`（例: 12）を変更
  - `src/components/ScoreChart.tsx` … スコア 8–32 を 0–100% に変換する式を修正（必要なら `scoring.ts` のユーティリティに合わせる）

### 案B: 5段階のままスコアの再重み付け

- **概要**: UI は 5段階のまま、生スコアを変換して中間（2・4）を極端側に寄せる。例: 1→1, 2→1.5, 3→3, 4→4.5, 5→5。
- **変更するファイル**:
  - `docs/01_requirements.md` … 2.5 に「生スコアを再重み付けして集計する」旨を追記、2.6 で採用案を明記
  - `src/utils/scoring.ts` … `calculateAxisScores` 内で、各 `answer.score` を上記の変換テーブルで重み付けしてから加算。`getTendencyType` / `getTendencyStrength` の閾値は変換後のスコア範囲（例: 8–40 のままだが分布が広がる）に合わせて必要なら微調整
  - （任意）`src/components/ScoreChart.tsx` … 表示用のスコアが変換後になるため、0–100% 変換式がそのまま使えるか確認し、必要なら調整

### 案C: 6段階化（中立をなくす）

- **概要**: 1–3 を A 側、4–6 を B 側とし、中立を廃止。スコア 1〜6、軸合計 8〜48、中央 28 で A/B 判定。
- **変更するファイル**:
  - `docs/01_requirements.md` … 2.4 を6段階に、2.5 を 8〜48・中央28 に更新
  - `docs/02_questions.md` … 回答形式を6段階に変更
  - `src/data/types.ts` … `Answer.score` のコメントを 1–6 に
  - `src/components/QuestionPage.tsx` … `scaleLabels` を6段階に、ボタン6個に変更
  - `src/utils/scoring.ts` … 軸スコア範囲 8–48、中央 28 に合わせて `getTendencyType`（例: score <= 27 で A）、`getTendencyStrength` の `maxDistance`（例: 20）を変更
  - `src/components/ScoreChart.tsx` … 8–48 を 0–100% に変換する式を修正

---

## 3. 案別の修正ポイント（コード）

### 案A: 4段階

- **QuestionPage.tsx**  
  `scaleLabels` を例えば  
  `[ { score: 1, label: 'かなりAに近い' }, { score: 2, label: 'ややAに近い' }, { score: 3, label: 'ややBに近い' }, { score: 4, label: 'かなりBに近い' } ]`  
  にし、ボタンは 4 個に。
- **scoring.ts**  
  - 軸スコアは 8〜32。  
  - `getTendencyType`: 例として `score <= 19` を A、`score >= 20` を B。  
  - `getTendencyStrength`: 中央 20、`maxDistance = 12`（20–8 または 32–20）。

### 案B: 再重み付け

- **scoring.ts**  
  - 変換マップ例: `const weight = { 1: 1, 2: 1.5, 3: 3, 4: 4.5, 5: 5 };`  
  - `calculateAxisScores` で `scores[question.axis] += weight[answer.score as 1|2|3|4|5] ?? answer.score;` のように加算。  
  - 合計範囲は 8〜40 のままだが、2・4 選択が極端側に寄るため分布が広がる。閾値 24 はそのままでも可。必要なら実データを見て 23/25 などを微調整。

### 案C: 6段階

- **QuestionPage.tsx**  
  `scaleLabels` を 1〜6 の6件に（例: 1・2 ややA／かなりA、3 どちらかといえばA、4 どちらかといえばB、5・6 ややB／かなりB など）。ボタン 6 個に。
- **scoring.ts**  
  - 軸スコア 8〜48、中央 28。  
  - `getTendencyType`: 例として `score <= 27` を A、`score >= 28` を B。  
  - `getTendencyStrength`: 中央 28、`maxDistance = 20`（28–8 または 48–28）。

---

## 4. 共通で確認すること

- **useDiagnosis.ts**  
  回答の保存形式（`score` の 1–5 / 1–4 / 1–6）が変わる場合、既存のローカルストレージや状態の互換性を確認する。
- **ScoreChart.tsx**  
  軸スコアの範囲が変わる案では、0–100% 変換が `scoring.ts` の `getTendencyStrength` などと矛盾しないようにする。
- **02_questions.md**  
  各案の回答形式（4段階／5段階のまま／6段階）の説明を、実際のラベルと一致させる。

---

## 5. 推奨

- **まず試すなら案B（再重み付け）**  
  UI 変更が不要で、質問文・選択肢ラベルもそのまま使え、実装が少ない。効果を確認したうえで、必要なら案Aや案Cで段階数そのものを変更するのがよい。
- **振り幅を強くしたいなら案Aまたは案C**  
  中立をなくすことで、無意識の「真ん中寄せ」を防ぎ、タイプのばらつきを増やしやすい。

---

## 6. 採用案

**案C（6段階化）を採用**（2026-01-25 実装済み）

- 回答形式: 1〜6の6段階（中立なし）
- 軸スコア: 8〜48点、中央28でA/B判定
- 変更ファイル: `01_requirements.md`, `02_questions.md`, `types.ts`, `QuestionPage.tsx`, `scoring.ts`, `ScoreChart.tsx`
