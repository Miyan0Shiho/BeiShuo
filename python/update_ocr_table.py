#!/usr/bin/env python3
"""
更新OCR表结构，添加保存字符位置信息的字段
"""
import mysql.connector
from app.config import settings

# 连接数据库
print("连接数据库...")
conn = mysql.connector.connect(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_name
)

cursor = conn.cursor()

# 更新ocr_text_lines表，添加words_json字段
print("更新ocr_text_lines表结构...")
try:
    cursor.execute("ALTER TABLE ocr_text_lines ADD COLUMN words_json JSON NULL")
    print("ocr_text_lines表结构更新成功")
except mysql.connector.Error as err:
    if err.errno == 1060:  # 字段已存在
        print("字段words_json已存在")
    else:
        print(f"更新表结构失败: {err}")

# 关闭连接
cursor.close()
conn.close()
print("数据库连接已关闭")
