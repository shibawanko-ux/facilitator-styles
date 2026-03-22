# 18. イラスト要件定義

作成日：2026-03-22

---

## 概要

ファシリテータータイプ診断アプリに使用するイラストの要件定義。
Pencil AIで生成したフラット×マンガ風イラストスタイルを正式採用。

---

## 基本スタイル

| 項目 | 仕様 |
|------|------|
| スタイル | フラットイラスト × 日本マンガ風（Japanese manga style） |
| 場面 | ファシリテーションをしている場面（ワークショップ・対話・グループ活動） |
| 構図 | tight composition（人物同士が近い、引き締まった構図） |
| 背景 | クリーンな室内背景（clean indoor background） |
| テキスト | NG（no text） |
| 吹き出し | NG（no speech bubbles / no thought bubbles） |

---

## プロンプト共通フォーマット

```
flat illustration [タイプ説明] tight composition Japanese manga style [色系] tones clean background no text no speech bubbles
```

---

## ヒーローイラスト（TOP画面）

- **用途**：TOPページのヒーローセクション（全面配置・囲み枠なし）
- **内容**：多様な人物が自然に配置された場面（リードする人・聴く人・考える人）
- **プロンプト**：
  ```
  flat illustration diverse group of people with different personalities and communication styles, some leading some listening some thinking, Japanese manga style, colorful characters, blue and white tones, clean minimal background, no text
  ```
- **配置**：フレーム全面に広げる（インパクト重視、囲み枠なし）

---

## 16タイプ キャラクターイラスト

各タイプのカード（イラスト高さ260px）に使用。

| # | タイプ名 | カラートーン | 場面・構図 |
|---|---------|------------|----------|
| 1 | 場の指揮者 | blue white | ホワイトボード前でグループをリード |
| 2 | 共感のスパーク | warm pink | 円座で参加者の声を引き出している |
| 3 | 静かな舵取り | green cool | 参加者のそばでノートを取りながら見守る |
| 4 | ムードメーカー | yellow bright | 全員が笑顔で活発なワークショップ |
| 5 | 推進のエンジン | red warm | データチャートを指しながらチームを前進させる |
| 6 | 戦略のナビゲーター | orange warm | ロードマップをボードで提示しながらグループに説明 |
| 7 | 直感の開拓者 | yellow amber | ホワイトボードに新しいアイデアを描く、グループが驚き興奮 |
| 8 | 場の調律師 | pink coral | テーブルを挟んで2人の間に座り場を調和させる |
| 9 | 場の演出家 | purple violet | グループを巻き込む演出でみんなが熱中 |
| 10 | 柔軟な記録者 | green teal | 議論しながら付箋を整理・記録 |
| 11 | 静かな戦略家 | blue navy | 一人で戦略ノートを確認・次の手を考える |
| 12 | 流れを読む羅針盤 | cyan teal | 横からそっとジェスチャーで議論の流れを導く |
| 13 | 信頼の土台 | indigo blue | 安心できる場を作り全員が前のめりに |
| 14 | 寄り添う聴き手 | pink soft | 1対1の深い傾聴・共感の場面 |
| 15 | 場の守り人 | green soft | 対立する2人の間で穏やかに調整 |
| 16 | 静かな共鳴者 | purple lavender | グループと静かに共に在る、全員が理解されている感覚 |

---

## 構図のコツ（生成時の注意事項）

- `tight composition` を入れると人物間の距離が縮まりまとまった印象になる
- `full bodies visible` `wide angle zoomed out` は雰囲気が損なわれることがある → 原則使わない
- ファシリテーションの「場面」を具体的に指定する（ホワイトボード前・円座・テーブル囲み等）
- 吹き出しが出やすい構図（会話・対話場面）は `no speech bubbles no thought bubbles` を必ず追加

---

## カードレイアウト仕様

| 項目 | 値 |
|------|---|
| カード幅 | fill_container（2列グリッド） |
| イラスト高さ | 260px |
| cornerRadius（イラスト上部） | [12, 12, 0, 0] |
| cornerRadius（カード全体） | 12px |
| カードshadow | outer / blur:8 / offset(0,2) / #00000012 |
| テキストエリアpadding | [12, 14] |
| タイトルフォント | 14px / bold / #1e293b |
| サブタイトルフォント | 11px / regular / #64748b |
| カード間gap | 12px |
| 背景色 | #f8fafc |
