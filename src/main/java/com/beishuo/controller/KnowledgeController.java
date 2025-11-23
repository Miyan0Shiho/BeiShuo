package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
import com.beishuo.common.PageResult;
import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/knowledge")
public class KnowledgeController {

    private static final Logger logger = LoggerFactory.getLogger(KnowledgeController.class);

    @Autowired
    private JwtUtil jwtUtil;

    // TODO: 注入KnowledgeService
    // @Autowired
    // private KnowledgeService knowledgeService;

    /**
     * 获取知识库首页
     */
    @GetMapping("/home")
    public Result<Map<String, Object>> getKnowledgeHome(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String period) {

        // TODO: 调用KnowledgeService获取首页数据
        Map<String, Object> result = new HashMap<>();
        result.put("categories", new java.util.ArrayList<>());
        result.put("featured", new java.util.ArrayList<>());
        result.put("recent_articles", new java.util.ArrayList<>());

        return Result.success(result);
    }

    /**
     * 获取文章详情
     */
    @GetMapping("/articles/{article_id}")
    public Result<Map<String, Object>> getArticleDetail(@PathVariable("article_id") Long articleId) {
        // TODO: 调用KnowledgeService获取详情
        Map<String, Object> result = new HashMap<>();
        result.put("id", articleId);
        result.put("title", "");
        result.put("content", "");
        result.put("excerpt", "");
        result.put("cover_image", "");
        result.put("author", new HashMap<>());
        result.put("metadata", new HashMap<>());
        result.put("stats", new HashMap<>());
        result.put("related_articles", new java.util.ArrayList<>());

        return Result.success(result);
    }

    /**
     * 搜索知识库
     */
    @GetMapping("/search")
    public Result<Map<String, Object>> searchKnowledge(
            @RequestParam("q") String keyword,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String dynasty,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer per_page) {

        // TODO: 调用KnowledgeService搜索知识库
        Map<String, Object> result = new HashMap<>();
        result.put("query", keyword);
        result.put("total_results", 0);
        result.put("results", new java.util.ArrayList<>());
        result.put("suggestions", new java.util.ArrayList<>());
        result.put("facets", new HashMap<>());

        return Result.success(result);
    }


    /**
     * 从Token中获取用户ID
     */
    private Long getUserIdFromToken(String authHeader) {
        if (authHeader == null) {
            return null;
        }
        String token = jwtUtil.extractTokenFromHeader(authHeader);
        if (token == null || !jwtUtil.validateToken(token)) {
            return null;
        }
        return jwtUtil.getUserIdFromToken(token);
    }
}

