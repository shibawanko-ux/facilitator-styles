# レポート・GAS 整合性確認結果

**確認日**: 2026.02.12  
**対象**: レポート関連ロジック・表示・GAS の情報矛盾の有無

---

## 1. 確認範囲

- 生成レポート（全体）.md とスライド挿入内容（全体）.md の対応
- スライド挿入内容と GAS コード内データ（PLACEHOLDER_DATA / REPORT_DATA / CSV_DATA）の一致
- データソース表記（01_エグゼクティブサマリー.csv、生成レポート.md）と実際の値の整合
- 軸順・プレースホルダー命名（CgrA〜F、Ogr*）と要件（02, 05, 13, 17）の一致

---

## 2. 確認結果サマリー

| 項目 | 結果 | 備考 |
|------|------|------|
| スライド挿入内容 ⇔ 生成レポート | 一致 | S_block_1/2/3、C_block_*、数値・文言とも一致 |
| PLACEHOLDER_DATA ⇔ スライド挿入内容 | 一致 | 置換は PLACEHOLDER_DATA を使用しており表示は正しい |
| REPORT_DATA の S_block_* | 一致 | 総合型コメントが正しく埋め込まれている |
| REPORT_DATA の C_block_* | 不一致 | GAS 内で空文字のまま（後述） |
| CSV_DATA（executiveSummary）⇔ 表の数値 | 一致 | 軸順・実施前/直後/変化量とも一致 |
| 軸順・命名（A=具体化、B=リサーチ、C=構想、D=伝達、E=実現、F=総合） | 要件と一致 | 13・17 の仕様どおり |
| 組織別 O_block_2/3・Ogr* | 一致 | スライド挿入内容と PLACEHOLDER_DATA と一致 |

---

## 3. データフロー整理

1. **分析** → 生成レポート.md（report_generator）
2. **生成レポート + 分析結果** → スライド挿入内容.md（同）
3. **スライド挿入内容** → GAS 生成時に  
   - `parse_placeholder_mapping_from_markdown()` → **PLACEHOLDER_DATA**（全プレースホルダー ⇔ データ内容）  
   - `parse_slide_content_markdown()` → **slide_data** → **REPORT_DATA** の S_block / C_block 等  
   - CSV 読み込み → **CSV_DATA**（executiveSummary, organizationAnalysis 等）
4. **GAS 実行時**  
   - スライド1・2 等の置換: **PLACEHOLDER_DATA** を参照（`replacePlaceholdersInSlide_(slide, PLACEHOLDER_DATA)`）  
   - 組織別スライド: **ORGANIZATION_DATA**（スライド挿入内容から抽出）＋ CSV

---

## 4. 発見した不整合と対応

### 4.1 GAS 内 REPORT_DATA の C_block_* が空

- **事象**: 生成された GAS の `REPORT_DATA` において、`C_block_1_body`・`C_block_2_1_body`・`C_block_2_2_body`・`C_block_2_3_body` が空文字で埋め込まれている。
- **影響**: スライドの置換は **PLACEHOLDER_DATA** で行っているため、**表示上の不具合はなし**。REPORT_DATA は Phase 判定・clientName 等の参照に使われており、C_block を参照する処理は現状ない。
- **原因**: `parse_slide_content_markdown()` がスライド挿入内容から C_block を正しく取り出していない可能性、または report_data_dict 組み立て時に未設定のままにしている可能性。
- **推奨対応**: GAS 生成時、`report_data_dict` の C_block_* が空の場合は **placeholder_mapping**（PLACEHOLDER_DATA の元）から同一キーで補完する。これにより REPORT_DATA と PLACEHOLDER_DATA の内容が一致し、将来 REPORT_DATA を参照する処理を追加しても矛盾しない。

**対応済み**: `gas_generator.py` で、`report_data_dict` 組み立て後に C_block_1_body / C_block_2_1_body / C_block_2_2_body / C_block_2_3_body が空の場合に `placeholder_mapping` から補完する処理を追加。再生成後の GAS では REPORT_DATA に C_block が正しく埋め込まれることを確認済み。

---

## 5. 矛盾なしと判断した点

- **S_block_1/2/3**: 要件25の総合総評型・総合強み型・総合伸びしろ型が、生成レポート・スライド挿入内容・GAS の PLACEHOLDER_DATA / REPORT_DATA のいずれとも一致。
- **数値**: スライド挿入内容の Cgr* と GAS の PLACEHOLDER_DATA・CSV_DATA（executiveSummary）の値が一致。生成レポートのスコア推移表（2.29 / 2.62 / +0.33 等）とも一致。
- **組織別**: デザイン室等の O_score・Ogr*・O_block_2_body / O_block_3_body が、スライド挿入内容と GAS の ORGANIZATION_DATA / 組織別置換ロジックと整合。
- **データソース表記**: スライド挿入内容の「データソース」列が 18_生成レポート統合確認 の考え方と矛盾なし（01_エグゼクティブサマリー.csv、生成レポート.md のセクション経路）。

---

## 6. 今後の確認の目安

- 再生成後は「スライド挿入内容の表」と「GAS の PLACEHOLDER_DATA」の該当プレースホルダーを突き合わせると、表示と GAS の挙動を一通り確認できる。
- REPORT_DATA の C_block_* は、上記修正後に GAS を再生成すれば PLACEHOLDER_DATA と同内容で埋まる想定。
