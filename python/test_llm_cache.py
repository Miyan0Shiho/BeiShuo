#!/usr/bin/env python3
"""
测试LLM缓存功能的脚本
"""
import asyncio
import traceback
from app.client.mysql_client import mysql_client

async def test_llm_cache():
    """测试LLM缓存功能"""
    print("开始测试LLM缓存功能")
    
    try:
        # 连接数据库
        print("连接数据库...")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 1. 测试保存LLM结果
        print("\n测试1: 保存LLM结果")
        
        # 模拟LLM结果数据
        cache_key = "test_cache_key_123"
        cache_data = {
            "reply": {
                "content": "测试LLM回复内容",
                "role": "assistant",
                "type": "text"
            }
        }
        ttl = 3600
        
        # 保存LLM结果
        print(f"保存LLM结果... cache_key={cache_key}")
        saved_result = await mysql_client.set_llm_cache(cache_key, cache_data, ttl)
        if saved_result:
            print(f"保存LLM结果成功")
        else:
            print("保存LLM结果失败")
        
        # 2. 测试查询LLM结果
        print("\n测试2: 查询LLM结果")
        print(f"查询LLM结果... cache_key={cache_key}")
        llm_result = await mysql_client.get_llm_cache(cache_key)
        if llm_result:
            print(f"查询LLM结果成功: {llm_result}")
        else:
            print("查询LLM结果失败: 未找到结果")
        
        # 3. 测试缓存命中（同一脚本内）
        print("\n测试3: 测试缓存命中（同一脚本内）")
        print(f"再次查询LLM结果... cache_key={cache_key}")
        llm_result_again = await mysql_client.get_llm_cache(cache_key)
        if llm_result_again:
            print(f"缓存命中成功: {llm_result_again}")
        else:
            print("缓存命中失败: 未找到结果")
        
        print("\nLLM缓存测试完成")
        
    except Exception as e:
        print(f"测试LLM缓存失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")

if __name__ == "__main__":
    asyncio.run(test_llm_cache())