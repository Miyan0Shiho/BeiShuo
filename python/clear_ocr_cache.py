#!/usr/bin/env python3
"""
清除OCR数据库缓存脚本

该脚本用于清除数据库中之前的OCR缓存记录，包括：
1. inscription_assets表中的记录
2. ocr_jobs表中的记录
3. ocr_images表中的记录
4. ocr_text_lines表中的记录

注意：此操作会删除所有OCR缓存数据，请谨慎执行！
"""

import asyncio
import traceback
from app.client.mysql_client import mysql_client


async def clear_ocr_cache():
    """清除OCR数据库缓存"""
    print("开始清除OCR数据库缓存")
    print("=" * 60)
    print("警告：此操作会删除所有OCR缓存数据，请谨慎执行！")
    print("=" * 60)
    
    # 自动确认操作（用于脚本自动执行）
    print("自动确认清除操作")
    
    try:
        # 连接数据库
        print("\n连接数据库...")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 1. 清除ocr_text_lines表
        print("\n1. 清除ocr_text_lines表...")
        query = "DELETE FROM ocr_text_lines"
        affected_rows = await mysql_client.execute_update(query)
        print(f"成功删除 {affected_rows} 条ocr_text_lines记录")
        
        # 2. 清除ocr_images表
        print("\n2. 清除ocr_images表...")
        query = "DELETE FROM ocr_images"
        affected_rows = await mysql_client.execute_update(query)
        print(f"成功删除 {affected_rows} 条ocr_images记录")
        
        # 3. 清除ocr_jobs表
        print("\n3. 清除ocr_jobs表...")
        query = "DELETE FROM ocr_jobs"
        affected_rows = await mysql_client.execute_update(query)
        print(f"成功删除 {affected_rows} 条ocr_jobs记录")
        
        # 4. 清除inscription_assets表中与OCR相关的记录
        print("\n4. 清除inscription_assets表中与OCR相关的记录...")
        query = "DELETE FROM inscription_assets"
        affected_rows = await mysql_client.execute_update(query)
        print(f"成功删除 {affected_rows} 条inscription_assets记录")
        
        print("\nOCR数据库缓存清除完成！")
        print("=" * 60)
        print("已清除的表：")
        print("- ocr_text_lines")
        print("- ocr_images")
        print("- ocr_jobs")
        print("- inscription_assets")
        print("=" * 60)
        print("OCR数据库缓存清除成功！")
        
    except Exception as e:
        print(f"清除OCR缓存失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")


if __name__ == "__main__":
    asyncio.run(clear_ocr_cache())