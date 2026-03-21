"""
個人用GASコード生成モジュール（再実装版）
個人別スライド用のGoogleスライドGASコードを生成
全体用GASコード生成のロジックを参考に、シンプルで確実な実装
"""
import os
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime

# 安全なprint関数（BrokenPipeErrorを無視）
def safe_print(*args, **kwargs):
    """安全なprint関数（BrokenPipeErrorを無視）"""
    try:
        print(*args, **kwargs, file=sys.stderr)
    except (BrokenPipeError, OSError):
        pass


def parse_individual_slide_content_markdown(slide_content_path: str) -> Tuple[List[Dict[str, Dict[str, str]]], Dict[str, str]]:
    """
    個人用スライド挿入内容Markdownから、各参加者ごとのプレースホルダーとデータ内容のマッピングを抽出
    表紙セクションのデータも抽出する
    
    Returns:
        tuple: (参加者データのリスト, 表紙プレースホルダーの辞書)
    """
    participants_data = []
    cover_placeholders = {}
    
    if not os.path.exists(slide_content_path):
        return participants_data, cover_placeholders
    
    try:
        with open(slide_content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        import re
        current_participant = None
        current_placeholders = {}
        in_participant_section = False
        in_cover_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # 表紙セクションの開始を検出
            if line_stripped.startswith('## スライド0: 表紙') or (line_stripped.startswith('##') and '表紙' in line_stripped):
                in_cover_section = True
                in_participant_section = False
                safe_print("  表紙セクションを検出")
                continue
            
            # 表紙セクション内でテーブル行を検出
            if in_cover_section and '`{{' in line and '}}`' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    placeholder_cell = parts[1].strip()
                    data_value = parts[2].strip()
                    
                    match = re.search(r'`\{\{([^}]+)\}\}`', placeholder_cell)
                    if match:
                        placeholder_id = '{{' + match.group(1) + '}}'
                        if data_value and data_value != 'データ内容' and data_value != '-':
                            cover_placeholders[placeholder_id] = data_value
                continue
            
            # 参加者セクションの開始を検出
            if line_stripped.startswith('## 参加者'):
                in_cover_section = False
                
                # 前の参加者のデータを保存
                if current_participant and current_placeholders:
                    # nameプレースホルダーが未設定なら参加者名で補完（{{name}}または{{name_P}}の両方に対応）
                    if '{{name}}' not in current_placeholders and '{{name_P}}' not in current_placeholders:
                        # テンプレートに{{name}}がある場合は{{name}}を使用、なければ{{name_P}}を使用
                        current_placeholders['{{name}}'] = current_participant
                    participant_placeholders = current_placeholders.copy()
                    participant_placeholders.update(cover_placeholders)
                    participants_data.append({
                        'name': current_participant,
                        'placeholders': participant_placeholders
                    })
                
                # 新しい参加者の開始
                match = re.search(r'## 参加者\d+:\s*(.+)', line_stripped)
                if match:
                    current_participant = match.group(1).strip()
                    current_placeholders = {}
                    in_participant_section = True
                    safe_print(f"  参加者を検出: {current_participant}")
                continue
            
            # 参加者セクション内でのみテーブル行を検出
            if in_participant_section and '`{{' in line and '}}`' in line and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    placeholder_cell = parts[1].strip()
                    data_value = parts[2].strip()
                    
                    match = re.search(r'`\{\{([^}]+)\}\}`', placeholder_cell)
                    if match:
                        placeholder_id = '{{' + match.group(1) + '}}'
                        # データ内容列ヘッダー以外は追加（空・'-'も追加。17 CgrF_*_P）
                        if data_value != 'データ内容':
                            current_placeholders[placeholder_id] = data_value if data_value else ''
        
        # 最後の参加者のデータを保存
        if current_participant and current_placeholders:
            # nameプレースホルダーが未設定なら参加者名で補完
            if '{{name}}' not in current_placeholders and '{{name_P}}' not in current_placeholders:
                current_placeholders['{{name}}'] = current_participant
            participant_placeholders = current_placeholders.copy()
            participant_placeholders.update(cover_placeholders)
            participants_data.append({
                'name': current_participant,
                'placeholders': participant_placeholders
            })
        
        safe_print(f"個人用スライド挿入内容Markdownから{len(participants_data)}名の参加者データを抽出しました")
        safe_print(f"表紙プレースホルダー: {len(cover_placeholders)}個")
    
    except Exception as e:
        safe_print(f"個人用スライド挿入内容Markdown解析エラー: {e}")
        import traceback
        try:
            traceback.print_exc(file=sys.stderr)
        except (BrokenPipeError, OSError):
            pass
    
    return participants_data, cover_placeholders


def generate_individual_gas_code(project_id: str, project_name: str, phase: int,
                                 individual_slide_content_path: str) -> str:
    """
    個人用GASコードを生成（再実装版）
    
    Args:
        project_id: プロジェクトID
        project_name: プロジェクト名
        phase: フェーズ（2, 3）
        individual_slide_content_path: 個人用スライド挿入内容Markdownファイルのパス
    
    Returns:
        生成されたGASコード（文字列）
    """
    if phase not in [2, 3]:
        raise ValueError(f"個人用GASコードはPhase 2またはPhase 3のみ対応しています。指定されたPhase: {phase}")
    
    # テンプレートスライドID（個人用）
    if phase == 2:
        template_slide_id = '1hNVB6KZe9-VeYzSO_FY2RggGkM6XPiKXkqgzEdTLblI'
    else:  # phase == 3
        template_slide_id = '1wb0qGlykvzqGXfQ7DpRktfm-LU76n8AeUQVYfdiKMlc'
    
    # 個人用スライド挿入内容Markdownを解析
    participants_data, cover_placeholders = parse_individual_slide_content_markdown(individual_slide_content_path)
    
    if not participants_data:
        raise ValueError("個人用スライド挿入内容Markdownから参加者データを抽出できませんでした")
    
    # 参加者データをJSON形式でシリアライズ
    participants_data_js = json.dumps(participants_data, ensure_ascii=False, indent=2)
    
    date_str = datetime.now().strftime('%Y.%m.%d')
    
    # 個人用レイアウト（表紙 + 個人ページ1枚）
    layouts = ['cover', 'radar_chart_P']
    layouts_js = json.dumps(layouts, ensure_ascii=False)
    
    # GASコードを生成（シンプルな構造で実装）
    gas_code = f'''/**
 * 実践スキル定着度レポート 個人別スライド自動生成
 * プロジェクト: {project_name}
 * フェーズ: Phase {phase}
 * 生成日: {date_str}
 * 
 * 使用方法:
 * 1. マスターテンプレートのスライドを開く
 *    - Phase 2用: https://docs.google.com/presentation/d/1hNVB6KZe9-VeYzSO_FY2RggGkM6XPiKXkqgzEdTLblI/edit
 *    - Phase 3用: https://docs.google.com/presentation/d/1wb0qGlykvzqGXfQ7DpRktfm-LU76n8AeUQVYfdiKMlc/edit
 * 2. 拡張機能 > Apps Script を開く
 * 3. このコードを貼り付けて保存
 * 4. 実行 > generateIndividualSlides を実行（各参加者ごとにスライドが生成されます）
 * 5. レーダーチャート画像は手動でスライドに挿入してください
 * 
 * データ要件（分析アプリで検証済み）:
 * - 実施前.csvと直後.csvでは、同一参加者が同じメールアドレスを使用すること
 * - メールアドレスの重複や不一致があると分析は実行されない
 * 
 * 注意: 
 * - レーダーチャート画像は手動で挿入してください（自動挿入は行いません）
 * - 各参加者ごとに1枚（radar_chart_P）が生成されます（表紙は1回のみ）
 * - レイアウト順: cover → radar_chart_P
 */

// ============================================
// 設定
// ============================================
const TEMPLATE_SLIDE_ID = '{template_slide_id}';
const LAYOUTS = {layouts_js};

// ============================================
// 参加者データ（埋め込み）
// ============================================
const PARTICIPANTS_DATA = {participants_data_js};

// ============================================
// ヘルパー関数: スピーカーノートからスライドを取得
// ============================================
function getSlideFromTemplateSlideByNotes(templateSlideId, targetLayoutId) {{
  try {{
    const templatePresentation = SlidesApp.openById(templateSlideId);
    const slides = templatePresentation.getSlides();
    
    for (let i = 0; i < slides.length; i++) {{
      const slide = slides[i];
      try {{
        const notes = slide.getNotesPage();
        const notesText = notes.getSpeakerNotesShape().getText().asString();
        
        const escapedLayoutId = targetLayoutId.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
        const layoutPattern = new RegExp('LAYOUT:\\\\s*' + escapedLayoutId, 'i');
        if (layoutPattern.test(notesText)) {{
          Logger.log('スライド "' + targetLayoutId + '" をスピーカーノートから見つけました: スライド ' + (i + 1));
          return slide;
        }}
      }} catch (e) {{
        continue;
      }}
    }}
    
    Logger.log('警告: スライド "' + targetLayoutId + '" をスピーカーノートから見つけられませんでした');
    return null;
  }} catch (e) {{
    Logger.log('エラー: テンプレートスライドからスライドを取得できませんでした: ' + e.toString());
    return null;
  }}
}}

// ============================================
// プレースホルダー置換関数（全体用GASコードと同じロジック）
// ============================================
function replacePlaceholdersInSlide_(slide, dict) {{
  let replacedCount = 0;
  
  for (const key in dict) {{
    const value = dict[key];
    if (value !== null && value !== undefined && value !== '') {{
      try {{
        slide.replaceAllText(key, value);
        replacedCount++;
      }} catch (e) {{
        Logger.log('replaceAllText()エラー: ' + key + ' - ' + e.message);
        // フォールバック: 個別のShape/Tableを処理
        try {{
          const shapes = slide.getShapes();
          for (let i = 0; i < shapes.length; i++) {{
            const shape = shapes[i];
            const shapeType = shape.getShapeType();
            
            if (shapeType === SlidesApp.ShapeType.TABLE) {{
              try {{
                const table = shape.asTable();
                const numRows = table.getNumRows();
                const numCols = table.getNumColumns();
                
                for (let row = 0; row < numRows; row++) {{
                  for (let col = 0; col < numCols; col++) {{
                    try {{
                      const cell = table.getCell(row, col);
                      const textRange = cell.getText();
                      if (textRange) {{
                        textRange.replaceAllText(key, value);
                      }}
                    }} catch (e) {{
                      // セル取得エラーは無視
                    }}
                  }}
                }}
              }} catch (e) {{
                Logger.log('テーブル処理エラー: ' + e.message);
              }}
            }} else {{
              try {{
                const textRange = shape.getText();
                if (textRange) {{
                  textRange.replaceAllText(key, value);
                }}
              }} catch (e) {{
                // テキストがないShapeは無視
              }}
            }}
          }}
          
          // テーブルを直接取得して処理
          try {{
            const tables = slide.getTables();
            if (tables && tables.length > 0) {{
              for (let t = 0; t < tables.length; t++) {{
                const table = tables[t];
                const numRows = table.getNumRows();
                const numCols = table.getNumColumns();
                
                for (let row = 0; row < numRows; row++) {{
                  for (let col = 0; col < numCols; col++) {{
                    try {{
                      const cell = table.getCell(row, col);
                      const textRange = cell.getText();
                      if (textRange) {{
                        textRange.replaceAllText(key, value);
                      }}
                    }} catch (e) {{
                      // セル取得エラーは無視
                    }}
                  }}
                }}
              }}
            }}
          }} catch (e) {{
            Logger.log('getTables()エラー: ' + e.message);
          }}
        }} catch (e2) {{
          Logger.log('フォールバック処理エラー: ' + e2.message);
        }}
      }}
    }}
  }}
  
  if (replacedCount > 0) {{
    Logger.log('置換完了: ' + replacedCount + '種類のプレースホルダー');
  }}
}}

// ============================================
// ヘルパー関数: スピーカーノートからスライドを検出（現在のプレゼンテーション内）
// ============================================
function findSlideByLayout(slides, targetLayoutId) {{
  if (!slides || typeof slides.length === 'undefined') {{
    Logger.log('エラー: findSlideByLayout に無効なスライド一覧が渡されました。スライドを開いた状態で実行してください。');
    return null;
  }}
  for (let i = 0; i < slides.length; i++) {{
    const slide = slides[i];
    try {{
      const notes = slide.getNotesPage();
      const notesText = notes.getSpeakerNotesShape().getText().asString();
      
      const escapedLayoutId = targetLayoutId.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
      const layoutPattern = new RegExp('LAYOUT:\\\\s*' + escapedLayoutId, 'i');
      if (layoutPattern.test(notesText)) {{
        Logger.log('スライド "' + targetLayoutId + '" を検出: インデックス ' + i);
        return slide;
      }}
    }} catch (e) {{
      continue;
    }}
  }}
  Logger.log('警告: スライド "' + targetLayoutId + '" が見つかりませんでした');
  return null;
}}

// ============================================
// データ入力関数: 既存のスライドをループしてreplacePlaceholdersInSlide_()を呼び出す
// ============================================
function applyDataToSlides_(slides, participantsData) {{
  Logger.log('=== データ入力処理開始 ===');
  Logger.log('スライド数: ' + slides.length + '枚');
  Logger.log('参加者数: ' + participantsData.length + '名');
  
  for (let i = 0; i < slides.length && i < participantsData.length; i++) {{
    const slide = slides[i];
    const participant = participantsData[i];
    const participantName = participant.name;
    
    try {{
      Logger.log('');
      Logger.log('参加者 ' + (i + 1) + '/' + participantsData.length + ': ' + participantName + ' のスライドにデータを入力中...');
      replacePlaceholdersInSlide_(slide, participant.placeholders);
      Logger.log('✓ ' + participantName + ' のスライドにデータを挿入しました');
    }} catch (e) {{
      Logger.log('❌ エラー: ' + participantName + ' のスライド処理に失敗しました');
      Logger.log('   エラー詳細: ' + e.toString());
      Logger.log('   スタックトレース: ' + (e.stack || 'なし'));
    }}
  }}
  
  Logger.log('=== データ入力処理完了 ===');
}}

// ============================================
// メイン関数: 個人別スライドを生成（全体用GASコード生成のロジックを模倣）
// ============================================
function generateIndividualSlides() {{
  const presentation = SlidesApp.getActivePresentation();
  if (!presentation) {{
    Logger.log('エラー: プレゼンテーションが取得できません。Googleスライドを開いた状態で、拡張機能 > Apps Script からこの関数を実行してください。');
    return;
  }}
  const slides = presentation.getSlides();
  if (!slides || typeof slides.length === 'undefined') {{
    Logger.log('エラー: スライド一覧を取得できません。プレゼンテーションにスライドが存在するか確認してください。');
    return;
  }}
  
  Logger.log('=== 個人別スライド生成開始 ===');
  Logger.log('総スライド数: ' + slides.length);
  Logger.log('参加者数: ' + PARTICIPANTS_DATA.length + '名');
  
  // 1. 既存のcoverスライドを検出して編集（全体用GASコード生成と同じロジック）
  const coverSlide = findSlideByLayout(slides, 'cover');
  if (coverSlide) {{
    try {{
      const firstParticipant = PARTICIPANTS_DATA[0];
      if (firstParticipant) {{
        Logger.log('=== 表紙スライドを処理中 ===');
        replacePlaceholdersInSlide_(coverSlide, firstParticipant.placeholders);
        Logger.log('✓ 表紙スライドにデータを挿入しました');
      }}
    }} catch (e) {{
      Logger.log('表紙スライド編集エラー: ' + e.toString());
    }}
  }} else {{
    Logger.log('警告: 表紙スライドが見つかりませんでした');
  }}
  
  // 2. 既存のradar_chart_Pスライドを検出
  const radarTemplateSlide = findSlideByLayout(slides, 'radar_chart_P');
  if (!radarTemplateSlide) {{
    Logger.log('警告: radar_chart_P スライドが見つかりませんでした');
    Logger.log('=== 個人別スライド生成完了 ===');
    return;
  }}
  
  // 【ステップ1: スライドの準備（複製）】
  Logger.log('');
  Logger.log('=== ステップ1: スライドの準備（複製） ===');
  Logger.log('radar_chart_Pスライドを ' + (PARTICIPANTS_DATA.length - 1) + '回複製します（2人目以降用）');
  
  const radarSlides = [radarTemplateSlide]; // 元のスライドを含む配列（1人目用）
  
  try {{
    for (let i = 1; i < PARTICIPANTS_DATA.length; i++) {{
      const duplicatedSlide = radarTemplateSlide.duplicate();
      radarSlides.push(duplicatedSlide);
      Logger.log('複製 ' + i + '/' + (PARTICIPANTS_DATA.length - 1) + ': スライドを複製しました');
    }}
    Logger.log('✓ スライドの準備が完了しました（合計 ' + radarSlides.length + '枚）');
  }} catch (e) {{
    Logger.log('❌ エラー: スライドの複製に失敗しました');
    Logger.log('   エラー詳細: ' + e.toString());
    Logger.log('   スタックトレース: ' + (e.stack || 'なし'));
    Logger.log('=== 個人別スライド生成完了 ===');
    return;
  }}
  
  // 【ステップ2: データの入力（ループ処理）】
  Logger.log('');
  Logger.log('=== ステップ2: データの入力（ループ処理） ===');
  Logger.log('applyDataToSlides_()関数で既存のスライドをループしてデータを入力します');
  
  applyDataToSlides_(radarSlides, PARTICIPANTS_DATA);
  
  Logger.log('');
  Logger.log('=== 個人別スライド生成完了 ===');
  Logger.log('注意: レーダーチャート画像は手動でスライドに挿入してください。');
}}
'''
    
    return gas_code
