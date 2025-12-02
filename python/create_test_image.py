#!/usr/bin/env python3
"""
创建测试图片脚本 - 生成包含文字的测试图片

功能：
- 创建包含中文字符的测试图片
- 模拟碑文或古籍文字
- 用于OCR识别测试
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建测试图片"""
    
    # 图片尺寸
    width, height = 800, 600
    
    # 创建白色背景图片
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体
    try:
        # 尝试使用macOS系统字体
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS 中文字体
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/AppleGothic.ttf",
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 36)
                    break
                except:
                    continue
        
        if font is None:
            # 使用默认字体
            font = ImageFont.load_default()
            
    except:
        font = ImageFont.load_default()
    
    # 测试文字内容（模拟碑文）
    text_content = [
        "大明嘉靖二十三年",
        "岁次甲辰仲春吉日",
        "立石人：张三李四",
        "功德主：王五赵六",
        "刻字匠人：钱七孙八",
        "此碑记载重要历史事件",
        "永垂不朽，万世流芳"
    ]
    
    # 绘制文字
    y_position = 50
    for line in text_content:
        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_position = (width - text_width) // 2
        
        # 绘制文字
        draw.text((x_position, y_position), line, fill='black', font=font)
        y_position += text_height + 20
    
    # 保存图片
    output_path = "/Users/liuminxuan/Desktop/团队项目/python/test_images/test_inscription.jpg"
    image.save(output_path, "JPEG", quality=95)
    
    print(f"✅ 测试图片已创建: {output_path}")
    print(f"图片尺寸: {width}x{height}")
    print("包含文字内容:")
    for line in text_content:
        print(f"  - {line}")
    
    return output_path

if __name__ == "__main__":
    # 创建测试图片目录
    test_images_dir = "/Users/liuminxuan/Desktop/团队项目/python/test_images"
    os.makedirs(test_images_dir, exist_ok=True)
    
    # 创建测试图片
    image_path = create_test_image()
    
    print("\n测试图片准备完成，可以运行OCR功能测试了！")