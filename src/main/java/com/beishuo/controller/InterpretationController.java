package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
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
@RequestMapping("/ai")
public class InterpretationController {

    private static final Logger logger = LoggerFactory.getLogger(InterpretationController.class);

    @Autowired
    private JwtUtil jwtUtil;

    // TODO: 注入InterpretationService
    // @Autowired
    // private InterpretationService interpretationService;

    /**
     * 获取AI阐释
     */
    @PostMapping("/interpretation")
    public Result<Map<String, Object>> generateInterpretation(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String recognitionId = (String) request.get("recognition_id");
        List<String> aspects = (List<String>) request.get("aspects");
        String depth = (String) request.get("depth");

        if (recognitionId == null) {
            return Result.error(ResultCode.BAD_REQUEST, "recognition_id不能为空");
        }

        // TODO: 调用InterpretationService生成阐释
        Map<String, Object> results = new HashMap<>();
        
        if (aspects == null || aspects.contains("history")) {
            Map<String, Object> history = new HashMap<>();
            history.put("title", "历史背景");
            history.put("content", "");
            history.put("key_points", new java.util.ArrayList<>());
            results.put("history", history);
        }
        
        if (aspects == null || aspects.contains("culture")) {
            Map<String, Object> culture = new HashMap<>();
            culture.put("title", "文化意义");
            culture.put("content", "");
            culture.put("keywords", new java.util.ArrayList<>());
            results.put("culture", culture);
        }
        
        if (aspects == null || aspects.contains("literature")) {
            Map<String, Object> literature = new HashMap<>();
            literature.put("title", "文学价值");
            literature.put("content", "");
            literature.put("style", "");
            literature.put("themes", new java.util.ArrayList<>());
            results.put("literature", literature);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("interpretation_id", "int_" + System.currentTimeMillis());
        result.put("results", results);
        result.put("related_inscriptions", new java.util.ArrayList<>());

        return Result.success(result);
    }

    /**
     * AI对话
     */
    @PostMapping("/chat")
    public Result<Map<String, Object>> chat(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String recognitionId = (String) request.get("recognition_id");
        String message = (String) request.get("message");
        String context = (String) request.get("context");
        String conversationId = (String) request.get("conversation_id");

        if (message == null || message.isEmpty()) {
            return Result.error(ResultCode.BAD_REQUEST, "问题不能为空");
        }

        // TODO: 调用InterpretationService进行对话
        String conversationIdResult = conversationId != null ? conversationId : "conv_" + System.currentTimeMillis();
        
        Map<String, Object> reply = new HashMap<>();
        reply.put("content", "");
        reply.put("type", "text");
        reply.put("sources", new java.util.ArrayList<>());
        reply.put("suggestions", new java.util.ArrayList<>());

        Map<String, Object> result = new HashMap<>();
        result.put("conversation_id", conversationIdResult);
        result.put("reply", reply);
        result.put("related_questions", new java.util.ArrayList<>());

        return Result.success(result);
    }

    /**
     * 获取相关推荐
     */
    @GetMapping("/recommendations")
    public Result<Map<String, Object>> getRecommendations(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @RequestParam(required = false) String type,
            @RequestParam(defaultValue = "5") Integer limit) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("inscriptions", new java.util.ArrayList<>());
        result.put("articles", new java.util.ArrayList<>());
        result.put("questions", new java.util.ArrayList<>());

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

