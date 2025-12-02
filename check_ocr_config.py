#!/usr/bin/env python3
"""
检查OCR配置加载情况
"""

import sys
sys.path.append('/Users/liuminxuan/Desktop/团队项目/python')

from app.config import settings

print("=== OCR配置检查 ===")
print(f"kandianguji_ocr_token: {settings.kandianguji_ocr_token}")
print(f"kandianguji_ocr_email: {settings.kandianguji_ocr_email}")
print(f"kandianguji_ocr_timeout: {settings.kandianguji_ocr_timeout}")

# 检查环境变量
import os
print("\n=== 环境变量检查 ===")
print(f"KANDIANGUJI_OCR_TOKEN: {os.getenv('KANDIANGUJI_OCR_TOKEN')}")
print(f"KANDIANGUJI_OCR_EMAIL: {os.getenv('KANDIANGUJI_OCR_EMAIL')}")

# 检查配置是否为空
if not settings.kandianguji_ocr_token or not settings.kandianguji_ocr_email:
    print("\n❌ OCR配置为空，需要检查.env文件加载")
else:
    print("\n✅ OCR配置已正确加载")