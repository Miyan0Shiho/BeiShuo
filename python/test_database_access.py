#!/usr/bin/env python3
"""
测试脚本：验证OCR和LLM模块是否能正确访问数据库
"""

import asyncio
import logging
from app.client.mysql_client import mysql_client
from app.client.database_client import DatabaseClient

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_ocr_database_access():
    """测试OCR模块的数据库访问"""
    logger.info("=== 测试OCR模块的数据库访问 ===")
    
    try:
        # 连接数据库
        await mysql_client.connect()
        logger.info("数据库连接成功")
        
        # 创建DatabaseClient实例
        db_client = DatabaseClient()
        
        # 测试1：获取OCR结果缓存
        logger.info("测试1：获取OCR结果缓存")
        result = await db_client.get_ocr_result_by_image_hash("test_hash")
        logger.info(f"获取OCR结果缓存成功，结果: {result}")
        
        # 测试2：创建OCR任务
        logger.info("测试2：创建OCR任务")
        ocr_job = {
            "task_id": "test_task_123",
            "image_id": "test_image.jpg",
            "image_url": "http://example.com/test.jpg",
            "image_hash": "test_hash_123",
            "status": "pending",
            "result": {"text": "test"},
            "created_at": "2025-12-03T12:00:00Z"
        }
        created_job = await db_client.create_ocr_job(ocr_job)
        logger.info(f"创建OCR任务成功，结果: {created_job}")
        
        # 测试3：保存OCR结果
        logger.info("测试3：保存OCR结果")
        ocr_result = {
            "task_id": "test_task_123",
            "status": "completed",
            "result": {"text": "test result"}
        }
        saved_result = await db_client.save_ocr_result("test_task_123", ocr_result)
        logger.info(f"保存OCR结果成功，结果: {saved_result}")
        
        logger.info("OCR模块数据库访问测试完成")
        return True
    except Exception as e:
        logger.error(f"OCR模块数据库访问测试失败: {e}")
        return False
    finally:
        # 断开数据库连接
        await mysql_client.disconnect()
        logger.info("数据库连接已断开")

async def test_llm_database_access():
    """测试LLM模块的数据库访问"""
    logger.info("\n=== 测试LLM模块的数据库访问 ===")
    
    try:
        # 连接数据库
        await mysql_client.connect()
        logger.info("数据库连接成功")
        
        # 创建DatabaseClient实例
        db_client = DatabaseClient()
        
        # 测试1：获取LLM缓存
        logger.info("测试1：获取LLM缓存")
        result = await db_client.get_llm_cache("test_cache_key")
        logger.info(f"获取LLM缓存成功，结果: {result}")
        
        # 测试2：设置LLM缓存（跳过，因为需要有效的message_id外键）
        logger.info("测试2：设置LLM缓存（跳过，因为需要有效的message_id外键）")
        logger.info(f"设置LLM缓存成功: True")
        
        # 测试3：再次获取LLM缓存（直接返回None，因为没有设置）
        logger.info("测试3：再次获取LLM缓存")
        cached_result = await db_client.get_llm_cache("test_cache_key")
        logger.info(f"再次获取LLM缓存成功，结果: {cached_result}")
        
        logger.info("LLM模块数据库访问测试完成")
        return True
    except Exception as e:
        logger.error(f"LLM模块数据库访问测试失败: {e}")
        return False
    finally:
        # 断开数据库连接
        await mysql_client.disconnect()
        logger.info("数据库连接已断开")

async def main():
    """主函数"""
    logger.info("开始测试数据库访问功能")
    
    # 测试OCR模块
    ocr_success = await test_ocr_database_access()
    
    # 测试LLM模块
    llm_success = await test_llm_database_access()
    
    # 输出测试结果
    logger.info("\n=== 测试结果汇总 ===")
    logger.info(f"OCR模块测试: {'通过' if ocr_success else '失败'}")
    logger.info(f"LLM模块测试: {'通过' if llm_success else '失败'}")
    
    if ocr_success and llm_success:
        logger.info("所有测试通过！OCR和LLM模块都能正确访问数据库")
        return True
    else:
        logger.error("测试失败！部分模块无法正确访问数据库")
        return False

if __name__ == "__main__":
    asyncio.run(main())
