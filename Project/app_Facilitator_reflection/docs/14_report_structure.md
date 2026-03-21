# 結果画面の構成（レポート表示構造）

結果画面で表示する**レポートの内容と表示構造**を定義する。読み手（主にメインファシリテーター）が**上から順に読みやすく**、**振り返りと次の一手**に自然につながる構成とする。[01_requirements.md](01_requirements.md) 2.4.1 および [02_requirements_analysis_result.md](02_requirements_analysis_result.md) の表示構成を具体化する。

**デザインの方向性**は [15_design_direction.md](15_design_direction.md) に従い、ファシリテータースタイル診断と同一ブランド（丸み・余白・sky/slate）で統一する。

---

## 1. 結果画面の全体構成（読み手の流れ）

結果画面は**上から下**に、次のブロックで構成する。番号は表示順である。

| 順 | ブロック名（画面での見出し案） | 内容 | 読み手の目的 |
|----|------------------------------|------|----------------|
| 0 | **6つの観点（レーダーチャート）** | 六角形レーダー1枚。6軸×役割（メイン・サブ・参加者）の比較。凡例はチャート下段。 | 全体の傾向を一目で把握する |
| 1 | **あなたへの評価** | 総評・あなたの強み・あなたの伸びしろ（テキスト中心。点数は羅列しない） | 自分へのフィードバックを理解する |
| 2 | **6つの観点の解説** | 総合点数（メイン vs サブ・参加者）＋ 各観点の分析文。観点名に「？」でツールチップ。 | 軸ごとの解釈と次に手を入れるポイントを知る |
| 3 | **振り返りの問い・シェアドリーダーシップ** | 振り返り用の問い（アコーディオン）、シェアドリーダーシップ・認知（アコーディオン） | 対話のきっかけと次のアクションを得る |

- **0** は結果画面の最上部に独立したカードで表示する。
- **1〜3** は「レポート」として1つのカード（またはセクション群）にまとめ、見出しで区切る。
- 実装上のセクション番号（セクション1〜3）は、上記のブロック1＝セクション1、ブロック2＝セクション2、ブロック3＝セクション3 に対応する。

---

## 2. 文言・モチベーション方針

レポートの文言は、読み手（メインファシリテーター）の**モチベーション**を意識する。

- **対象者**: 主な読み手はメインファシリテーター。文言は**モチベーションが高まる**ようにしつつ、**批判・課題も必要な範囲で含める**。
- **強み**: 肯定を前面に。「〜と読める」に加え、「〇〇の観点では高く評価されています」「届いていたと感じられています」など、**強みとして伝わる一文**を各ブロックの先頭に置く。
- **伸びしろ**: 未来志向の表現。「低め」だけでなく「これから伸ばしやすい領域」「次に手を入れやすい」とし、最後に「次に試すとよいこと」のヒントを添える。事実に基づく批判は「〜の可能性」「〜と解釈できる」で残す。
- **総評**: 傾向の要約（点数羅列なし）＋役割間の傾向＋「次にやるとよいこと」の一言。2〜3文に分けて読みやすくする。

---

## 3. ブロック別の詳細

### 3.1 ブロック0：6つの観点（レーダーチャート）

- **表示**: 1枚の六角形レーダー。6軸（説明・設計、見える化・編集、場の観察、場のホールド・安心感、問いかけ・リフレーミング、流れ・即興）。メイン・サブ・参加者の3系列（または存在する役割のみ）を重ねて表示。
- **軸ラベル**: 各軸の名目位置に観点名を表示。その外向きにメイン・サブ・参加者の点数をオフセットして配置し、図や他ラベルと重ならないようにする。点数の文字色はチャートの系列色と同一。
- **凡例**: チャート外（下段）に配置し、文字と重ならないようにする。
- **詳細要件**: [02_requirements_analysis_result.md](02_requirements_analysis_result.md) の「0. 表示の構成」「2. レーダーチャート」を参照。

---

### 3.2 ブロック1：あなたへの評価（セクション1）

メインファシリテーター向けの**総合的な評価フィードバック**。各項目は**点数を羅列せず、テキストで表現**する。

| 項目 | 内容 | 分量・表現 |
|------|------|------------|
| **総評** | 全体の傾向・役割間の傾向・次にやるとよいこと | 約300字。factSentence は1〜2文（60〜80字）。bullets は2本目安（傾向の要約／次の一手）。数値羅列はしない。 |
| **あなたの強み** | メインの強みをあぶり出す | 約200字。箇条書き2〜3本。1本目を「いちばんの強み」の1文（40字前後）、2本目以降で理由・観点を補足。肯定を前面に。 |
| **あなたの伸びしろ** | 弱み・課題と次に試すとよいこと | 約200字。1本目を「いちばん伸ばしやすいところ」の1文、2本目で解釈、3本目で「次に試すとよいこと」のヒント。未来志向。 |

---

### 3.3 ブロック2：6つの観点の解説（セクション2）

| 項目 | 内容 | 分量・表現 |
|------|------|------------|
| **総合点数** | メイン・サブ・参加者の総合点と差分が分かる表示 | 6軸の平均を役割別に表示。差分で傾向が分かる旨を短く補足してよい。 |
| **各観点の分析** | 6観点それぞれの分析（メイン・サブ・参加者の点数から解釈） | 1観点あたり「1文要約＋1文補足」目安（計80〜120字）。1文目で結論、2文目で理由。点数は羅列しない。 |
| **観点の説明（ツールチップ）** | 各観点名称の横に「？」アイコン。ホバーで説明表示 | 05_evaluation_items.md の6軸定義に合わせて説明文を保持する。 |

---

### 3.4 ブロック3：振り返りの問い・シェアドリーダーシップ（セクション3）

| 項目 | 内容 | 表示形式 |
|------|------|----------|
| **振り返り用の問い** | 弱み軸・強み軸に紐づく問い。3問程度。意図の併記は任意。 | アコーディオン（開閉可能） |
| **シェアドリーダーシップ・認知** | メイン・サブのシェアドリーダーシップの振り返り | アコーディオン（開閉可能）。箇条書き。サブがいる場合のみ表示。 |

- 詳細: [03_requirements_reflection_shared_leadership_cognition.md](03_requirements_reflection_shared_leadership_cognition.md) を参照。

---

## 4. 表示・見せ方（UIの細則）

- **ブロック1**
  - 強み・伸びしろの先頭 bullet に対応するラベル（例: 「いちばんの強み」「伸ばしやすいところ」）を見出しまたは箇条書き直前に表示してよい。
  - 総評の bullets を「傾向の要約」「次の一手」などに分けて表示してよい。
  - 1行が長い場合は 40〜50 字程度で改行してよい。
- **ブロック2**
  - 各観点ブロックの先頭に、要約1行（太字など）を表示してよい。その下に bullets を表示する。
- **次回アクション**
  - bullets を番号付き（1. 2. 3.）で表示してよい。

---

## 5. 他ドキュメントとの対応

- **レーダーチャート**: 02 の「0. 表示の構成」に従い、結果画面の最上部に表示する。
- **reportAgent 出力**: [11_report_agent.md](11_report_agent.md) の JSON 構造（summary, strengths, improvementHypotheses, sectionComments, reflectionQuestions, actionProposal, sharedLeadershipReflectionQuestions 等）は、本ドキュメントのブロック1〜3に**マッピング**して表示する。
- **文字数制約**: 11・13・validateReportComment 等のブロック別文字数制約は、本ドキュメントの分量目安（300字・200字等）と整合させる。

---

## 6. 関連ファイル一覧

### 要件・設計ドキュメント

| ファイル | 役割 |
|----------|------|
| [01_requirements.md](01_requirements.md) | 2.4.1 結果の表示で本構成を参照 |
| [02_requirements_analysis_result.md](02_requirements_analysis_result.md) | 表示構成・レーダー・分析文・振り返り問いの要件 |
| [03_requirements_reflection_shared_leadership_cognition.md](03_requirements_reflection_shared_leadership_cognition.md) | ブロック3「シェアドリーダーシップ・認知」の要件元 |
| [05_evaluation_items.md](05_evaluation_items.md) | 6軸の定義・軸名称・ツールチップ説明文の参照元 |
| [11_report_agent.md](11_report_agent.md) | レポート出力 JSON 仕様。ブロック1〜3へのマッピング |
| [12_report_module_design.md](12_report_module_design.md) | reportAgent モジュール設計 |
| [15_design_direction.md](15_design_direction.md) | 結果画面のデザイン方針（ファシリテータースタイル同一ブランド） |

### フロントエンド（表示）

| ファイル | 役割 |
|----------|------|
| [src/pages/ResultPage.tsx](../src/pages/ResultPage.tsx) | 結果画面。ブロック0（レーダー）→ ブロック1〜3（レポート）の順で表示 |
| [src/data/evaluationItems.ts](../src/data/evaluationItems.ts) | 6軸 ID・ラベル・観点説明文（ツールチップ用） |

### レポート生成・型・バリデーション

| ファイル | 役割 |
|----------|------|
| [src/lib/reportAgent/types.ts](../src/lib/reportAgent/types.ts) | ReportAgentOutput 等の型。ブロック1〜3対応キーの確認・拡張 |
| [src/lib/reportAgent/renderTemplateComment.ts](../src/lib/reportAgent/renderTemplateComment.ts) | 総評・sectionComments 等のテンプレ組み立て |
| [src/lib/reportAgent/validateReportComment.ts](../src/lib/reportAgent/validateReportComment.ts) | 出力検証。本構造の分量・必須ブロックとの整合 |
| [src/lib/reportAgent/sectionCommentTemplates.ts](../src/lib/reportAgent/sectionCommentTemplates.ts) | 6軸ごとの分析コメントテンプレ |
| [src/lib/reportAgent/truncateReportOutput.ts](../src/lib/reportAgent/truncateReportOutput.ts) | ブロック別文字数 truncate |
| [src/lib/resultAnalysis.ts](../src/lib/resultAnalysis.ts) | 役割別・6軸総合点。総合点数表示に利用 |

### 振り返りの問い・シェアドリーダーシップ

| ファイル | 役割 |
|----------|------|
| [src/lib/reportAgent/reflectionQuestionsFixed.ts](../src/lib/reportAgent/reflectionQuestionsFixed.ts) | 固定の振り返りの問い。弱み軸・強み軸の出し分け |
| [src/lib/reportAgent/polishAiPrompt.ts](../src/lib/reportAgent/polishAiPrompt.ts) | AI 整形プロンプト。出力キーとブロック構造の一致確認 |
| [src/lib/reportAgent/classifyWorkshopState.ts](../src/lib/reportAgent/classifyWorkshopState.ts) | 状態タイプ分類。問いの出し分けに利用する場合に参照 |

### テスト・プレビュー

| ファイル | 役割 |
|----------|------|
| [src/lib/reportAgent/__tests__/validateReportComment.test.ts](../src/lib/reportAgent/__tests__/validateReportComment.test.ts) | 検証ルールのテスト |
| [src/lib/reportAgent/__tests__/reportPipeline.test.ts](../src/lib/reportAgent/__tests__/reportPipeline.test.ts) | パイプライン全体のテスト |
| [src/pages/ReportPreviewPage.tsx](../src/pages/ReportPreviewPage.tsx) | レポートプレビュー画面。本構成に合わせた見出し・並び |

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| （初版） | レポートを3セクションで定義。総評・強み・伸びしろ、総合点数、観点ツールチップ、アコーディオン仕様を明記。 |
| （追記） | 文言・モチベーション方針、表示・見せ方の要件を追加。 |
| （構成整理） | 結果画面の全体構成を「読み手の流れ」で再構成。ブロック0〜3・見出し案・読み手の目的を表で整理。15_design_direction への参照を追加。 |
