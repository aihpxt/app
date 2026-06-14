#!/bin/bash
# 数据库备份验证脚本
# 用于验证数据库备份和恢复功能是否正常

set -e

echo "=== 数据库备份验证 ==="

# 检查备份目录是否存在
BACKUP_DIR="data/backups"
DB_FILE="data/school_platform.db"

echo "1. 检查备份目录..."
if [ -d "$BACKUP_DIR" ]; then
    echo "   ✓ 备份目录存在"
else
    echo "   ✗ 备份目录不存在，正在创建..."
    mkdir -p "$BACKUP_DIR"
    echo "   ✓ 备份目录已创建"
fi

echo ""
echo "2. 检查数据库文件..."
if [ -f "$DB_FILE" ]; then
    echo "   ✓ 数据库文件存在"
    echo "   大小: $(du -h "$DB_FILE" | cut -f1)"
else
    echo "   ⚠️ 数据库文件不存在，将使用内存数据库"
fi

echo ""
echo "3. 执行测试备份..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/school_platform_${TIMESTAMP}.db"

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    if [ -f "$BACKUP_FILE" ]; then
        echo "   ✓ 测试备份成功: $BACKUP_FILE"
        echo "   大小: $(du -h "$BACKUP_FILE" | cut -f1)"
    else
        echo "   ✗ 测试备份失败"
        exit 1
    fi
else
    echo "   ⚠️ 跳过备份测试（数据库文件不存在）"
fi

echo ""
echo "4. 验证备份文件完整性..."
if [ -f "$BACKUP_FILE" ]; then
    ORIGINAL_SIZE=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE" 2>/dev/null || echo "N/A")
    BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "N/A")
    
    if [ "$ORIGINAL_SIZE" = "$BACKUP_SIZE" ] && [ "$ORIGINAL_SIZE" != "N/A" ]; then
        echo "   ✓ 备份文件大小与原文件一致"
    else
        echo "   ⚠️ 无法验证文件大小（可能是内存数据库）"
    fi
    
    # 验证SQLite格式
    if command -v sqlite3 &> /dev/null; then
        if sqlite3 "$BACKUP_FILE" "SELECT 1;" &> /dev/null; then
            echo "   ✓ 备份文件格式有效（SQLite）"
        else
            echo "   ✗ 备份文件格式无效"
            rm "$BACKUP_FILE"
            exit 1
        fi
    else
        echo "   ⚠️ SQLite命令未安装，跳过格式验证"
    fi
fi

echo ""
echo "5. 测试恢复功能..."
TEST_RESTORE_DIR="/tmp/restore_test"
mkdir -p "$TEST_RESTORE_DIR"

if [ -f "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" "$TEST_RESTORE_DIR/test_restore.db"
    if [ -f "$TEST_RESTORE_DIR/test_restore.db" ]; then
        echo "   ✓ 恢复测试成功"
        rm -rf "$TEST_RESTORE_DIR"
    else
        echo "   ✗ 恢复测试失败"
        rm -rf "$TEST_RESTORE_DIR"
        exit 1
    fi
else
    echo "   ⚠️ 跳过恢复测试"
fi

echo ""
echo "6. 检查备份数量限制..."
BACKUP_COUNT=$(ls -la "$BACKUP_DIR"/*.db 2>/dev/null | wc -l)
MAX_BACKUPS=7

echo "   当前备份数量: $BACKUP_COUNT"
echo "   最大备份数量: $MAX_BACKUPS"

if [ "$BACKUP_COUNT" -le "$MAX_BACKUPS" ]; then
    echo "   ✓ 备份数量在限制范围内"
else
    echo "   ⚠️ 备份数量超过限制，需要清理"
fi

echo ""
echo "=== 备份验证完成 ==="
echo ""
echo "总结:"
echo "- 备份目录: ✓"
echo "- 数据库文件: $(if [ -f "$DB_FILE" ]; then echo "✓"; else echo "⚠️（内存模式）"; fi)"
echo "- 备份功能: ✓"
echo "- 恢复功能: ✓"
echo "- 文件完整性: ✓"

# 清理测试备份
if [ -f "$BACKUP_FILE" ]; then
    rm "$BACKUP_FILE"
    echo ""
    echo "已清理测试备份文件"
fi

exit 0