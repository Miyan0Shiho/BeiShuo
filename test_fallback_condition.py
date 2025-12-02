#!/usr/bin/env python3
"""
测试OCR备用模式触发条件
验证当前代码中的备用模式触发逻辑是否正确
"""

def _normalize_ocr(data):
    """模拟OCR结果归一化函数"""
    if isinstance(data, list):
        texts = [str(x) for x in data]
        full_text = "\n".join(texts) if texts else ""
        return {
            "width": 0,
            "height": 0,
            "text_angel": None,
            "texts": texts,
            "text_lines": [],
            "full_text": full_text,
            "word_count": len(full_text) if full_text else 0,
            "confidence": 0.0,
            "layout": None,
        }
    if not isinstance(data, dict):
        return {
            "width": 0,
            "height": 0,
            "text_angel": None,
            "texts": [],
            "text_lines": [],
            "full_text": "",
            "word_count": 0,
            "confidence": 0.0,
            "layout": None,
        }
    width = data.get("width") or 0
    height = data.get("height") or 0
    text_angel = data.get("text_angel")
    texts = data.get("texts") or []
    text_lines = data.get("text_lines") or []
    full_text = "\n".join(texts) if texts else ("\n".join([str(tl.get("text") or "") for tl in text_lines]) if text_lines else (str(data.get("text") or "")))
    word_count = 0
    confidences = []
    for tl in text_lines or []:
        words = tl.get("words") or []
        word_count += len(words)
        for w in words:
            c = w.get("confidence")
            if c is None:
                c = w.get("det_confidence")
            if isinstance(c, (int, float)):
                confidences.append(float(c))
    if word_count == 0 and full_text:
        word_count = len(full_text)
    avg_conf = 0.0
    if confidences:
        avg_conf = round(sum(confidences) / len(confidences), 2)
    elif isinstance(data.get("text_angel_confidence"), (int, float)):
        avg_conf = float(data.get("text_angel_confidence"))
    return {
        "width": width,
        "height": height,
        "text_angel": text_angel,
        "texts": texts,
        "text_lines": text_lines,
        "full_text": full_text or "",
        "word_count": word_count,
        "confidence": avg_conf,
        "layout": data.get("layout") or None,
    }

def test_fallback_condition(norm):
    """测试备用模式触发条件"""
    condition = not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0)
    
    print(f"=== 测试条件: not full_text and (not text_lines or word_count == 0) ===")
    print(f"full_text: '{norm['full_text']}' (长度: {len(norm['full_text'])})")
    print(f"text_lines: {norm['text_lines']} (长度: {len(norm['text_lines'])})")
    print(f"word_count: {norm['word_count']}")
    print(f"not full_text: {not norm['full_text']}")
    print(f"not text_lines: {not norm['text_lines']}")
    print(f"word_count == 0: {norm['word_count'] == 0}")
    print(f"not text_lines or word_count == 0: {not norm['text_lines'] or norm['word_count'] == 0}")
    print(f"最终条件结果: {condition}")
    
    return condition

def main():
    """主测试函数"""
    print("=== OCR备用模式触发条件测试 ===\n")
    
    # 测试用例1: OCR返回空列表 []
    print("测试用例1: OCR返回空列表 []")
    data1 = []
    norm1 = _normalize_ocr(data1)
    should_fallback1 = test_fallback_condition(norm1)
    print(f"是否应该触发备用模式: {should_fallback1}")
    print()
    
    # 测试用例2: OCR返回空字典 {}
    print("测试用例2: OCR返回空字典 {}")
    data2 = {}
    norm2 = _normalize_ocr(data2)
    should_fallback2 = test_fallback_condition(norm2)
    print(f"是否应该触发备用模式: {should_fallback2}")
    print()
    
    # 测试用例3: OCR返回有内容的结果
    print("测试用例3: OCR返回有内容的结果")
    data3 = {
        "texts": ["大唐西亰千福寺多寳佛"],
        "text_lines": [{"text": "大唐西亰千福寺多寳佛", "words": [{"text": "大唐", "confidence": 0.9}]}],
        "width": 100,
        "height": 100
    }
    norm3 = _normalize_ocr(data3)
    should_fallback3 = test_fallback_condition(norm3)
    print(f"是否应该触发备用模式: {should_fallback3}")
    print()
    
    # 测试用例4: 检查实际调试脚本中的空结果
    print("测试用例4: 模拟实际调试脚本中的空结果")
    data4 = []
    norm4 = _normalize_ocr(data4)
    print(f"归一化结果: {norm4}")
    should_fallback4 = test_fallback_condition(norm4)
    print(f"是否应该触发备用模式: {should_fallback4}")
    print()
    
    # 分析问题
    print("=== 问题分析 ===")
    print("如果备用模式触发条件正确，但实际识别仍然失败，可能原因:")
    print("1. 备用模式本身也返回空结果")
    print("2. 备用模式调用时出现异常被pass捕获")
    print("3. 备用模式的参数设置有问题")
    print("4. 图片数据本身有问题")
    
    # 检查备用模式参数
    print("\n=== 备用模式参数检查 ===")
    primary_options = {
        "version": "v2",
        "det_mode": "auto",
        "return_position": True
    }
    
    sp_options = {**primary_options, "det_mode": "sp", "sp_line_words_angel": "top2bottom"}
    hp_options = {**primary_options, "det_mode": "hp", "hp_line_words_angel": "left2right"}
    beta_sp_options = {**primary_options, "version": "beta", "det_mode": "sp", "sp_line_words_angel": "top2bottom"}
    
    print(f"主模式参数: {primary_options}")
    print(f"SP模式参数: {sp_options}")
    print(f"HP模式参数: {hp_options}")
    print(f"Beta+SP模式参数: {beta_sp_options}")

if __name__ == "__main__":
    main()