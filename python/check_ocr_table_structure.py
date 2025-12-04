#!/usr/bin/env python3
"""
检查OCR相关表结构的脚本
"""
import asyncio
import mysql.connector
from app.config import settings

async def check_table_structure():
    """检查OCR相关表结构"""
    print("开始检查OCR相关表结构")
    
    try:
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
        print("\n1. 检查ocr_text_lines表结构:")
        cursor.execute("DESCRIBE ocr_text_lines")
        for column in cursor.fetchall():
            print(f"   {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        # 检查ocr_jobs表结构
        print("\n2. 检查ocr_jobs表结构:")
        cursor.execute("DESCRIBE ocr_jobs")
        for column in cursor.fetchall():
            print(f"   {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        # 检查ocr_images表结构
        print("\n3. 检查ocr_images表结构:")
        cursor.execute("DESCRIBE ocr_images")
        for column in cursor.fetchall():
            print(f"   {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        cursor.close()
        conn.close()
        
        print("\n表结构检查完成")
        
    except Exception as e:
        print(f"检查表结构失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure())