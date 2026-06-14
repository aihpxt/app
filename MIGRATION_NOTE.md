
数据库迁移说明
==============

由于系统权限限制，数据库文件无法自动迁移。请手动执行以下步骤：

1. 复制数据库文件：
   源文件: ai-service/data/unified_school_data.db
   目标文件: ai-service/sqlite/data/unified_school_data.db

2. 删除原文件（可选）：
   删除: ai-service/data/unified_school_data.db

3. 验证迁移成功：
   运行: python check_db_standards.py

完成后，系统将使用规范的数据库位置：ai-service/sqlite/data/
