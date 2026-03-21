#!/bin/bash
# 危険なBashコマンドを検知して日本語で警告するHook

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except:
    print('')
" 2>/dev/null)

# 危険パターンを検知
DANGEROUS=false
REASON=""

if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])\s*rm\s+(-[rRfF]*\s|.*-[rRfF])'; then
    DANGEROUS=true
    REASON="ファイル・フォルダの削除（rm）"
fi

if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])\s*git\s+push(\s|$)'; then
    DANGEROUS=true
    REASON="リモートへのプッシュ（git push）"
fi

if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])\s*git\s+reset\s+--hard'; then
    DANGEROUS=true
    REASON="変更の強制リセット（git reset --hard）"
fi

if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])\s*git\s+clean\s+-[fd]'; then
    DANGEROUS=true
    REASON="未追跡ファイルの削除（git clean）"
fi

if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])\s*drop\s+(table|database)' -i; then
    DANGEROUS=true
    REASON="データベースの削除（DROP TABLE/DATABASE）"
fi

if [ "$DANGEROUS" = true ]; then
    echo "🚨 危険な操作を検知しました"
    echo ""
    echo "種別: $REASON"
    echo ""
    echo "実行しようとしているコマンド:"
    echo "  $COMMAND"
    echo ""
    echo "この操作は取り消せない可能性があります。"
    echo "続行するには、明示的に許可してください。"
    exit 2
fi

exit 0
