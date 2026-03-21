"""
CSVアップロード時の参加者照合バリデーション
直前フェーズのCSVとメールアドレス・氏名を照合し、不一致を検出する
"""
import re
import unicodedata
from typing import Dict, List, Optional


def _normalize_name(name: str) -> str:
    """氏名の正規化: 全角半角統一・空白除去"""
    if not name:
        return ''
    name = unicodedata.normalize('NFKC', name)
    name = re.sub(r'[\s\u3000]+', '', name)
    return name.strip()


def _email_local(email: str) -> str:
    """メールアドレスの@より前を返す"""
    if not email or '@' not in email:
        return email or ''
    return email.split('@')[0]


def validate_participants(
    upload_data: List[Dict],
    reference_data: List[Dict],
    email_col: str = 'メールアドレス',
    name_col: str = '氏名',
) -> Dict:
    """
    アップロードCSVと直前フェーズCSVの参加者照合バリデーション

    Args:
        upload_data:    今回アップロードしたCSVのデータ
        reference_data: 照合対象（直前フェーズ）のCSVのデータ
        email_col:      メールアドレス列名
        name_col:       氏名列名

    Returns:
        {
            'matched':           完全一致した参加者リスト
            'domain_mismatch':   ドメイン違い（@前一致）の参加者リスト
            'not_in_reference':  直前CSVに存在しない参加者リスト
            'missing_in_upload': 今回CSVに存在しない参加者リスト（未回答）
            'name_mismatch':     氏名不一致の参加者リスト
            'has_issues':        True if 警告・エラーが1件でもある
        }
    """
    matched = []
    domain_mismatch = []
    not_in_reference = []
    missing_in_upload = []
    name_mismatch = []

    # 直前CSVをメール完全一致・ローカル部分でインデックス化
    ref_by_email = {}
    ref_by_local = {}
    for row in reference_data:
        email = (row.get(email_col) or '').strip()
        if not email:
            continue
        ref_by_email[email] = row
        local = _email_local(email)
        if local not in ref_by_local:
            ref_by_local[local] = row

    matched_ref_locals = set()

    for row in upload_data:
        email = (row.get(email_col) or '').strip()
        name = _normalize_name(row.get(name_col) or '')
        if not email:
            continue

        local = _email_local(email)

        if email in ref_by_email:
            # 完全一致
            ref_row = ref_by_email[email]
            ref_name = _normalize_name(ref_row.get(name_col) or '')
            entry = {'email': email, 'name': name}
            if ref_name and name and ref_name != name:
                entry['ref_name'] = ref_name
                name_mismatch.append(entry)
            else:
                matched.append(entry)
            matched_ref_locals.add(local)

        elif local in ref_by_local:
            # ドメイン違い（@前一致）
            ref_row = ref_by_local[local]
            ref_email = (ref_row.get(email_col) or '').strip()
            ref_name = _normalize_name(ref_row.get(name_col) or '')
            domain_mismatch.append({
                'email': email,
                'ref_email': ref_email,
                'name': name,
                'ref_name': ref_name,
                'local': local,
            })
            matched_ref_locals.add(local)

        else:
            # 直前CSVに存在しない
            not_in_reference.append({'email': email, 'name': name})

    # 直前CSVにいるが今回CSVにいない（未回答者）
    for ref_email, ref_row in ref_by_email.items():
        local = _email_local(ref_email)
        if local not in matched_ref_locals:
            missing_in_upload.append({
                'email': ref_email,
                'name': ref_row.get(name_col) or '',
            })

    has_issues = bool(
        domain_mismatch or not_in_reference or missing_in_upload or name_mismatch
    )

    return {
        'matched': matched,
        'domain_mismatch': domain_mismatch,
        'not_in_reference': not_in_reference,
        'missing_in_upload': missing_in_upload,
        'name_mismatch': name_mismatch,
        'has_issues': has_issues,
    }
