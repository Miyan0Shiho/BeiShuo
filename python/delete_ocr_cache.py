#!/usr/bin/env python3
"""
删除数据库中的OCR缓存记录
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.client.database_client import DatabaseClient
from app.utils.logger import logger

async def delete_ocr_cache():
    """
    删除OCR缓存记录
    """
    print("开始删除OCR缓存记录")
    
    # 连接数据库
    db_client = DatabaseClient()
    
    try:
        # 1. 查询inscription_assets表，获取所有资产记录
        print("1. 查询inscription_assets表，获取所有资产记录")
        
        # 查询所有inscription_assets记录，按创建时间倒序
        assets_query = """
        SELECT id, hash_md5, object_path, created_at 
        FROM inscription_assets 
        ORDER BY created_at DESC
        LIMIT 10
        """
        
        assets_results = await db_client.execute_query(assets_query)
        
        if not assets_results:
            print("未找到任何资产记录")
            return
        
        print(f"找到 {len(assets_results)} 条资产记录")
        for asset in assets_results:
            print(f"  asset_id={asset['id']}, hash_md5={asset['hash_md5']}, object_path={asset['object_path']}")
        
        # 2. 选择要删除的asset_id（这里我们删除所有测试记录）
        print("\n2. 删除所有测试相关的OCR记录")
        
        for asset in assets_results:
            asset_id = asset['id']
            hash_md5 = asset['hash_md5']
            
            print(f"\n处理asset_id={asset_id}, hash_md5={hash_md5}")
            
            # 查询关联的ocr_jobs
            jobs_query = "SELECT id FROM ocr_jobs WHERE asset_id = %s"
            jobs_results = await db_client.execute_query(jobs_query, (asset_id,))
            
            if jobs_results:
                for job in jobs_results:
                    job_id = job['id']
                    
                    print(f"  找到关联的ocr_job: job_id={job_id}")
                    
                    # 查询关联的ocr_images
                    images_query = "SELECT id FROM ocr_images WHERE job_id = %s"
                    images_results = await db_client.execute_query(images_query, (job_id,))
                    
                    if images_results:
                        for image in images_results:
                            image_id = image['id']
                            
                            print(f"    找到关联的ocr_image: image_id={image_id}")
                            
                            # 删除ocr_text_lines
                            delete_lines_query = "DELETE FROM ocr_text_lines WHERE image_id = %s"
                            lines_affected = await db_client.execute_update(delete_lines_query, (image_id,))
                            print(f"    删除了 {lines_affected} 条ocr_text_lines记录")
                            
                            # 删除ocr_images
                            delete_image_query = "DELETE FROM ocr_images WHERE id = %s"
                            image_affected = await db_client.execute_update(delete_image_query, (image_id,))
                            print(f"    删除了 {image_affected} 条ocr_images记录")
                    
                    # 删除ocr_jobs
                    delete_job_query = "DELETE FROM ocr_jobs WHERE id = %s"
                    job_affected = await db_client.execute_update(delete_job_query, (job_id,))
                    print(f"  删除了 {job_affected} 条ocr_jobs记录")
            
            # 删除inscription_assets
            delete_asset_query = "DELETE FROM inscription_assets WHERE id = %s"
            asset_affected = await db_client.execute_update(delete_asset_query, (asset_id,))
            print(f"删除了 {asset_affected} 条inscription_assets记录")
        
        print("\nOCR缓存记录删除完成")
    except Exception as e:
        logger.error(f"删除OCR缓存记录失败: {e}", exc_info=True)
        print(f"删除失败: {e}")
    finally:
        await db_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(delete_ocr_cache())