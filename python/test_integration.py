#!/usr/bin/env python3
"""
集成测试脚本：测试从图片上传到AI阐释的完整流程
"""

import asyncio
import logging
import requests
import json
import uuid
import time
from app.client.mysql_client import mysql_client
from app.services.interpretation_service import InterpretationService

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API端点配置
BASE_URL = "http://localhost:8080"
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
UPLOAD_URL = f"{BASE_URL}/api/v1/upload/image"
OCR_RECOGNIZE_URL = f"{BASE_URL}/api/v1/recognition/start"
INTERPRETATION_URL = f"{BASE_URL}/api/v1/ai/interpretation/sections"

class IntegrationTest:
    def __init__(self):
        self.test_image_path = "/Users/liuminxuan/Desktop/团队项目/python/uploads/微信图片_20251209100916_204_184.png"
        self.interpretation_service = InterpretationService()
        self.token = None
        self.user_email = f"test_user_{int(time.time())}@example.com"
        self.user_password = "Test@123456"
        self.user_name = f"TestUser_{int(time.time())}"
    
    async def register_user(self):
        """测试用户注册"""
        logger.info("=== 测试用户注册 ===")
        
        try:
            data = {
                "email": self.user_email,
                "password": self.user_password,
                "name": self.user_name
            }
            
            response = requests.post(REGISTER_URL, json=data)
            logger.info(f"注册响应状态码: {response.status_code}")
            logger.info(f"注册响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"用户注册成功，用户ID: {data.get('data', {}).get('user_id')}")
                self.token = data.get('data', {}).get('token')
                return True
            else:
                logger.error(f"用户注册失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"用户注册异常: {e}")
            return False
    
    async def login_user(self):
        """测试用户登录"""
        logger.info("=== 测试用户登录 ===")
        
        try:
            data = {
                "email": self.user_email,
                "password": self.user_password
            }
            
            response = requests.post(LOGIN_URL, json=data)
            logger.info(f"登录响应状态码: {response.status_code}")
            logger.info(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"用户登录成功，用户ID: {data.get('data', {}).get('user', {}).get('id')}")
                self.token = data.get('data', {}).get('token')
                return True
            else:
                logger.error(f"用户登录失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"用户登录异常: {e}")
            return False
    
    async def upload_image(self):
        """测试图片上传"""
        logger.info("=== 测试图片上传 ===")
        
        if not self.token:
            logger.error("图片上传失败: 未获取到认证令牌")
            return None
        
        try:
            with open(self.test_image_path, "rb") as f:
                files = {
                    "image": ("test_image.png", f, "image/png")
                }
                
                headers = {
                    "Authorization": f"Bearer {self.token}"
                }
                
                response = requests.post(UPLOAD_URL, files=files, headers=headers)
                logger.info(f"上传响应状态码: {response.status_code}")
                logger.info(f"上传响应内容: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"图片上传成功，图片URL: {data.get('data', {}).get('image_url')}")
                    return data.get('data', {})
                else:
                    logger.error(f"图片上传失败: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"图片上传异常: {e}")
            return None
    
    async def test_ocr_recognition(self, image_url):
        """测试OCR识别"""
        logger.info("=== 测试OCR识别 ===")
        
        if not self.token:
            logger.error("OCR识别失败: 未获取到认证令牌")
            return None
        
        try:
            data = {
                "image_url": image_url
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.post(OCR_RECOGNIZE_URL, json=data, headers=headers)
            logger.info(f"OCR识别响应状态码: {response.status_code}")
            logger.info(f"OCR识别响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {}).get('result', {})
                logger.info(f"OCR识别成功，识别文本: {result.get('text', '')[:100]}...")
                return data.get('data', {})
            else:
                logger.error(f"OCR识别失败: {response.text}")
                return None
        except Exception as e:
            logger.error(f"OCR识别异常: {e}")
            return None
    
    async def test_ai_interpretation(self, text):
        """测试AI阐释生成"""
        logger.info("=== 测试AI阐释生成 ===")
        
        if not self.token:
            logger.error("AI阐释生成失败: 未获取到认证令牌")
            return None
        
        try:
            data = {
                "text": text
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.post(INTERPRETATION_URL, json=data, headers=headers)
            logger.info(f"AI阐释响应状态码: {response.status_code}")
            logger.info(f"AI阐释响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"AI阐释成功，生成了阐释内容")
                return data.get('data', {})
            else:
                logger.error(f"AI阐释失败: {response.text}")
                return None
        except Exception as e:
            logger.error(f"AI阐释异常: {e}")
            return None
    
    async def test_llm_cache(self, text):
        """测试LLM缓存功能"""
        logger.info("=== 测试LLM缓存功能 ===")
        
        try:
            # 连接数据库
            await mysql_client.connect()
            logger.info("数据库连接成功")
            
            # 生成缓存键
            cache_key = await self.interpretation_service.generate_interpretation_cache_key(text, None)
            logger.info(f"生成的缓存键: {cache_key}")
            
            # 查询缓存
            cached_result = await mysql_client.get_llm_cache(cache_key)
            if cached_result:
                logger.info(f"LLM缓存命中，缓存内容: {cached_result}")
                return True
            else:
                logger.info("LLM缓存未命中")
                return False
        except Exception as e:
            logger.error(f"LLM缓存测试异常: {e}")
            return False
        finally:
            await mysql_client.disconnect()
            logger.info("数据库连接已断开")
    
    async def run_complete_flow(self):
        """运行完整的集成测试流程"""
        logger.info("开始运行完整集成测试流程")
        
        try:
            # 1. 注册用户
            register_success = await self.register_user()
            if not register_success:
                logger.error("集成测试失败：用户注册失败")
                return False
            
            # 2. 登录用户
            login_success = await self.login_user()
            if not login_success:
                logger.error("集成测试失败：用户登录失败")
                return False
            
            # 3. 上传图片
            upload_result = await self.upload_image()
            if not upload_result:
                logger.error("集成测试失败：图片上传失败")
                return False
            
            image_url = upload_result.get("image_url")
            if not image_url:
                logger.error("集成测试失败：获取image_url失败")
                return False
            
            # 4. 执行OCR识别
            ocr_result = await self.test_ocr_recognition(image_url)
            if not ocr_result:
                logger.error("集成测试失败：OCR识别失败")
                return False
            
            result = ocr_result.get("result", {})
            text = result.get("text")
            if not text:
                logger.error("集成测试失败：获取识别文本失败")
                return False
            
            # 5. 第一次生成AI阐释（应该不会命中缓存）
            logger.info("\n--- 第一次生成AI阐释（预期不会命中缓存）---")
            first_interpretation = await self.test_ai_interpretation(text)
            if not first_interpretation:
                logger.error("集成测试失败：第一次AI阐释生成失败")
                return False
            
            # 6. 检查缓存是否已保存
            logger.info("\n--- 检查缓存是否已保存 ---\n")
            await asyncio.sleep(1)  # 等待缓存保存完成
            cache_check = await self.test_llm_cache(text)
            if not cache_check:
                logger.error("集成测试失败：缓存未保存成功")
                return False
            
            # 7. 第二次生成AI阐释（应该会命中缓存）
            logger.info("\n--- 第二次生成AI阐释（预期会命中缓存）---\n")
            second_interpretation = await self.test_ai_interpretation(text)
            if not second_interpretation:
                logger.error("集成测试失败：第二次AI阐释生成失败")
                return False
            
            # 8. 验证两次阐释结果一致（缓存命中）
            logger.info("\n--- 验证两次阐释结果一致性 ---\n")
            first_sections = first_interpretation.get("sections", {})
            second_sections = second_interpretation.get("sections", {})
            
            if first_sections and second_sections:
                logger.info("两次阐释生成成功")
                if first_sections == second_sections:
                    logger.info("两次阐释内容完全一致，缓存命中成功")
                else:
                    logger.error("两次阐释内容不一致，缓存未命中")
                    return False
            else:
                logger.error("阐释数据格式不正确")
                return False
            
            logger.info("\n=== 集成测试成功！===\n")
            logger.info("完整流程测试通过：")
            logger.info("1. 用户注册成功")
            logger.info("2. 用户登录成功")
            logger.info("3. 图片上传成功")
            logger.info("4. OCR识别成功")
            logger.info("5. AI阐释生成成功")
            logger.info("6. LLM缓存功能正常")
            logger.info("7. 两次生成结果一致（缓存命中）")
            
            return True
        except Exception as e:
            logger.error(f"集成测试异常: {e}")
            return False

async def main():
    """主函数"""
    test = IntegrationTest()
    success = await test.run_complete_flow()
    
    if success:
        logger.info("所有集成测试通过！")
        return 0
    else:
        logger.error("集成测试失败！")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
