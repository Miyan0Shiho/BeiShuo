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
@RequestMapping("/favorites")
public class FavoriteController {

    private static final Logger logger = LoggerFactory.getLogger(FavoriteController.class);

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 获取收藏列表
     */
    @GetMapping
    public Result<Map<String, Object>> getFavorites(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @RequestParam(required = false) String type,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer per_page) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用服务层获取收藏列表
        Map<String, Object> result = new HashMap<>();
        result.put("favorites", new java.util.ArrayList<>());
        
        Map<String, Integer> stats = new HashMap<>();
        stats.put("total_count", 0);
        stats.put("inscriptions_count", 0);
        stats.put("articles_count", 0);
        result.put("stats", stats);
        
        Map<String, Object> pagination = new HashMap<>();
        pagination.put("current_page", page);
        pagination.put("total_pages", 0);
        pagination.put("total_count", 0);
        result.put("pagination", pagination);

        return Result.success(result);
    }

    /**
     * 添加收藏
     */
    @PostMapping
    public Result<Map<String, Object>> addFavorite(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String type = (String) request.get("type");
        String itemId = (String) request.get("item_id");
        String notes = (String) request.get("notes");
        List<String> tags = (List<String>) request.get("tags");

        if (type == null || itemId == null) {
            return Result.error(ResultCode.BAD_REQUEST, "type和item_id不能为空");
        }

        // TODO: 调用服务层添加收藏
        Map<String, Object> result = new HashMap<>();
        result.put("favorite_id", 1);

        return Result.success("已添加到收藏", result);
    }

    /**
     * 更新收藏
     */
    @PutMapping("/{favorite_id}")
    public Result<?> updateFavorite(
            @PathVariable("favorite_id") Long favoriteId,
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用服务层更新收藏
        return Result.success("收藏已更新", null);
    }

    /**
     * 删除收藏
     */
    @DeleteMapping("/{favorite_id}")
    public Result<?> deleteFavorite(
            @PathVariable("favorite_id") Long favoriteId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用服务层删除收藏
        return Result.success("已从收藏中移除", null);
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

