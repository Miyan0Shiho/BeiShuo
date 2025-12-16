#!/usr/bin/env python3
"""
检查ocr_text_lines表结构的脚本
"""
import mysql.connector
from app.config import settings

# 连接数据库
conn = mysql.connector.connect(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_name
)

cursor = conn.cursor()

# 检查ocr_text_lines表结构
print("ocr_text_lines表结构:")
cursor.execute("DESCRIBE ocr_text_lines")
for column in cursor.fetchall():
    print(f"{column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")

# 检查ocr_text_lines表中的数据
print("\nocr_text_lines表中的数据:")
cursor.execute("SELECT id, image_id, line_index, text, position_polygon FROM ocr_text_lines LIMIT 5")
for row in cursor.fetchall():
    print(f"id: {row[0]}, image_id: {row[1]}, line_index: {row[2]}, text: {row[3][:20]}..., position_polygon: {row[4]}")

cursor.close()
conn.close()
