# 22 個別スライド_overall_name_プレースホルダー要件

個人別スライドの雛形で「P2の{{overall_name}}」に**所属部署名**を表示するため、新プレースホルダー `{{overall_name}}` を追加する要件を規定する。

## 1. 目的

- 個人別スライド上で、その参加者の所属部署名を表示する。
- スライド雛形（個人スライドマスター）内の「P2の{{overall_name}}」を、実行時に所属部署名に置換する。

## 2. プレースホルダー仕様

| 項目 | 内容 |
|------|------|
| プレースホルダーID | `{{overall_name}}` |
| 表示内容 | その参加者の**所属部署名**（例: デザイン室、業務システム課、DX推進課） |
| データソース | 直後.csvの「あなたの所属部署を選択してください。」列（正規化後: 所属部署）。直後にない場合は実施前.csvの同列。既存の個別レポート「所属」表示（[20_個別レポート_所属部署表示要件.md](20_個別レポート_所属部署表示要件.md)）と同じ出所。 |
| スライド雛形 | P2の個人スライドマスター内で「P2の{{overall_name}}」として配置（スライド側で1箇所または複数箇所に配置可能） |

## 3. スライド雛形（参照）

- 個人のスライドマスター: https://docs.google.com/presentation/d/1TFrOFJwWXGpxzsCn5oOabBWMwIaDegT8i6IcuglI0t0/edit?slide=id.g3b3a0bf6720_0_259

## 4. 関わるファイルと対応

1. **report_generator.py**  
   `generate_individual_slide_content_markdown` で、各参加者の「スライド1」のプレースホルダーテーブルに  
   `| \`{{overall_name}}\` | {所属部署名} | 直後.csv（所属部署列）または実施前.csv、生成レポート（個別）.md（所属） |` を追加する。
2. **スライド挿入内容（個別）_*_Phase*.md**  
   上記により再生成すると、全参加者に `{{overall_name}}` の行が含まれる。
3. **individual_gas_generator.py**  
   既存のパースで `| \`{{XXX}}\` | 値 |` の行はすべて参加者ごとの placeholders に取り込まれるため、変更不要。生成GASは各参加者の placeholders をそのままスライドに置換するため、`{{overall_name}}` も自動で置換される。
4. **GASコード（個別）_*_Phase*.gs**  
   スライド挿入内容（個別）.md を再生成したうえで個別GASを再生成すると、`PARTICIPANTS_DATA` の各 `placeholders` に `{{overall_name}}` が含まれる。GAS側の置換ロジックは既存のまま。

## 5. 確認ポイント

- スライド挿入内容（個別）.md の各参加者ブロックに `{{overall_name}}` の行があること。
- 個別GAS実行後、各個人スライドの「P2の{{overall_name}}」が所属部署名（例: デザイン室）に置き換わっていること。

## 6. 実装済み（更新したファイル）

- **report_generator.py**: `generate_individual_slide_content_markdown` 内で各参加者のスライド1テーブルに `{{overall_name}}` 行を追加。
- **スライド挿入内容（個別）_*_Phase*.md**: 再生成により全参加者に `{{overall_name}}`（所属部署名）を追加済み。
- **GASコード（個別）_*_Phase*.gs**: 再生成により各参加者の `placeholders` に `"{{overall_name}}": "部署名"` を反映済み。スライド雛形で `{{overall_name}}` を置換するため追加のGAS修正は不要。

## 7. 参照

- 所属部署のデータソース・優先順位: [20_個別レポート_所属部署表示要件.md](20_個別レポート_所属部署表示要件.md)
- 個人用スライド・GAS: [06_GAS連携.md](06_GAS連携.md)
