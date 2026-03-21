"""
プロジェクト管理モジュール
プロジェクトの作成、取得、一覧取得を管理
"""
import os
import json
import re
from typing import List, Dict, Optional
from datetime import datetime


PROJECTS_FILE = 'projects.json'


def sanitize_folder_name(name: str) -> str:
    """
    プロジェクト名をファイルシステムで安全に使用できるフォルダ名に変換
    
    Args:
        name: プロジェクト名
    
    Returns:
        サニタイズされたフォルダ名
    """
    # Windows/Mac/Linuxで使用できない文字を置換
    # 禁止文字: < > : " / \ | ? *
    # また、先頭・末尾のスペースやドットも削除
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 先頭・末尾のスペースとドットを削除
    sanitized = sanitized.strip(' .')
    # 連続するスペースやアンダースコアを1つに
    sanitized = re.sub(r'[_\s]+', '_', sanitized)
    # 空文字列の場合はデフォルト名を使用
    if not sanitized:
        sanitized = 'project'
    # 長すぎる場合は切り詰め（255文字制限を考慮して200文字に）
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized


def get_projects_file_path(base_dir: str) -> str:
    """プロジェクトファイルのパスを取得"""
    return os.path.join(base_dir, PROJECTS_FILE)


def load_projects(base_dir: str) -> Dict[str, Dict]:
    """プロジェクト一覧を読み込む"""
    projects_file = get_projects_file_path(base_dir)
    if not os.path.exists(projects_file):
        return {}
    
    try:
        with open(projects_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_projects(base_dir: str, projects: Dict[str, Dict]):
    """プロジェクト一覧を保存"""
    projects_file = get_projects_file_path(base_dir)
    with open(projects_file, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def get_project_list(base_dir: str) -> List[Dict[str, str]]:
    """プロジェクト一覧を取得（プルダウン用）"""
    projects = load_projects(base_dir)
    project_list = []
    for project_id, project_data in projects.items():
        project_list.append({
            'id': project_id,
            'name': project_data.get('name', project_id),
            'created_at': project_data.get('created_at', '')
        })
    # 作成日時の新しい順にソート
    project_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return project_list


def get_or_create_project(base_dir: str, project_name: str) -> str:
    """プロジェクトを取得または作成（プロジェクトIDを返す）"""
    projects = load_projects(base_dir)
    
    # 既存のプロジェクトを検索（名前で）
    for project_id, project_data in projects.items():
        if project_data.get('name') == project_name:
            return project_id
    
    # 新規プロジェクトを作成
    project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    projects[project_id] = {
        'name': project_name,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_projects(base_dir, projects)
    
    return project_id


def get_project_name(base_dir: str, project_id: str) -> Optional[str]:
    """プロジェクト名を取得"""
    projects = load_projects(base_dir)
    project = projects.get(project_id)
    if project:
        return project.get('name', project_id)
    return None


def update_project_timestamp(base_dir: str, project_id: str):
    """プロジェクトの更新日時を更新"""
    projects = load_projects(base_dir)
    if project_id in projects:
        projects[project_id]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_projects(base_dir, projects)


def get_project_dir(base_dir: str, project_id: str) -> str:
    """
    プロジェクト専用ディレクトリのパスを取得
    プロジェクト名をフォルダ名として使用する（既存のプロジェクトIDベースのフォルダが存在する場合はそれを使用）
    
    Args:
        base_dir: ベースディレクトリ
        project_id: プロジェクトID
    
    Returns:
        プロジェクトディレクトリのパス
    """
    projects = load_projects(base_dir)
    project_data = projects.get(project_id)
    
    # 既存のプロジェクトIDベースのフォルダが存在するか確認（後方互換性）
    old_project_dir = os.path.join(base_dir, 'projects', project_id)
    if os.path.exists(old_project_dir):
        return old_project_dir
    
    if project_data:
        # プロジェクト名を取得してサニタイズ
        project_name = project_data.get('name', project_id)
        sanitized_name = sanitize_folder_name(project_name)
        project_dir = os.path.join(base_dir, 'projects', sanitized_name)
    else:
        # プロジェクトが見つからない場合はプロジェクトIDを使用
        project_dir = os.path.join(base_dir, 'projects', project_id)
    
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def get_project_upload_dir(base_dir: str, project_id: str) -> str:
    """プロジェクト専用アップロードディレクトリのパスを取得"""
    upload_dir = os.path.join(get_project_dir(base_dir, project_id), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def get_project_report_dir(base_dir: str, project_id: str) -> str:
    """プロジェクト専用レポートディレクトリのパスを取得"""
    report_dir = os.path.join(get_project_dir(base_dir, project_id), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


def get_project_export_dir(base_dir: str, project_id: str) -> str:
    """プロジェクト専用エクスポートディレクトリのパスを取得"""
    export_dir = os.path.join(get_project_dir(base_dir, project_id), 'spreadsheet_export')
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def delete_project(base_dir: str, project_id: str) -> Dict[str, any]:
    """
    プロジェクトを削除（フォルダとファイル、projects.jsonからの削除）
    
    Args:
        base_dir: ベースディレクトリ
        project_id: プロジェクトID
    
    Returns:
        削除結果の辞書（success: bool, message: str, deleted_items: list）
    """
    import shutil
    
    result = {
        'success': False,
        'message': '',
        'deleted_items': []
    }
    
    try:
        # projects.jsonからプロジェクト情報を取得
        projects = load_projects(base_dir)
        if project_id not in projects:
            result['message'] = f'プロジェクト {project_id} が見つかりません。'
            return result
        
        project_data = projects[project_id]
        project_name = project_data.get('name', project_id)
        
        # プロジェクトディレクトリのパスを取得（既存のフォルダを確認）
        # プロジェクトIDベースのフォルダ（後方互換性のため）
        old_project_dir = os.path.join(base_dir, 'projects', project_id)
        # プロジェクト名ベースのフォルダ
        sanitized_name = sanitize_folder_name(project_name)
        new_project_dir = os.path.join(base_dir, 'projects', sanitized_name)
        
        # 存在するディレクトリを削除（両方をチェックして、存在する方を削除）
        if os.path.exists(old_project_dir):
            # ディレクトリ内のすべてのファイルとフォルダを削除
            shutil.rmtree(old_project_dir)
            result['deleted_items'].append(f'ディレクトリ: {old_project_dir}')
        
        if os.path.exists(new_project_dir) and new_project_dir != old_project_dir:
            # ディレクトリ内のすべてのファイルとフォルダを削除
            shutil.rmtree(new_project_dir)
            result['deleted_items'].append(f'ディレクトリ: {new_project_dir}')
        
        # projects.jsonからプロジェクトを削除
        del projects[project_id]
        save_projects(base_dir, projects)
        result['deleted_items'].append(f'プロジェクト情報: {project_name}')
        
        result['success'] = True
        result['message'] = f'プロジェクト "{project_name}" を削除しました。'
        
    except Exception as e:
        result['message'] = f'プロジェクト削除中にエラーが発生しました: {str(e)}'
    
    return result
