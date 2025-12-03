package com.beishuo.controller;

import org.springframework.data.domain.Page;

import java.util.HashMap;
import java.util.Map;

/**
 * 基础控制器类
 */
public abstract class BaseController {
    
    /**
     * 构建分页响应
     */
    protected <T> Map<String, Object> buildPageResult(Page<T> page) {
        Map<String, Object> result = new HashMap<>();
        result.put("content", page.getContent());
        result.put("totalElements", page.getTotalElements());
        result.put("totalPages", page.getTotalPages());
        result.put("number", page.getNumber());
        result.put("size", page.getSize());
        result.put("first", page.isFirst());
        result.put("last", page.isLast());
        return result;
    }
}
