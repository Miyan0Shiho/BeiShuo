package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import com.beishuo.service.AuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private AuthService authService;

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public Result<Map<String, Object>> register(@RequestBody Map<String, Object> request) {
        String email = (String) request.get("email");
        String password = (String) request.get("password");
        String name = (String) request.get("name");
        String phone = (String) request.get("phone");
        String avatar = (String) request.get("avatar");

        if (email == null || password == null || name == null) {
            return Result.error(ResultCode.BAD_REQUEST, "邮箱、密码和姓名不能为空");
        }

        // 调用AuthService进行注册
        Map<String, Object> user = authService.register(email, password, name);

        Long userId = ((Number) user.get("id")).longValue();
        String usernameFromUser = (String) user.get("username");

        // 生成Token
        String token = jwtUtil.generateToken(userId, usernameFromUser);
        String refreshToken = jwtUtil.generateRefreshToken(userId, usernameFromUser);

        // 计算过期时间（24小时后）
        long expiresAt = System.currentTimeMillis() + 86400000L;
        String expiresAtStr = java.time.Instant.ofEpochMilli(expiresAt)
                .atZone(java.time.ZoneId.of("UTC"))
                .format(java.time.format.DateTimeFormatter.ISO_INSTANT);

        Map<String, Object> result = new HashMap<>();
        result.put("user_id", userId);
        result.put("token", token);
        result.put("expires_at", expiresAtStr);
        result.put("user", user);

        return Result.success("注册成功", result);
    }

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, Object> request) {
        String email = (String) request.get("email");
        String password = (String) request.get("password");
        Boolean rememberMe = request.get("remember_me") != null ? 
                (Boolean) request.get("remember_me") : false;

        if (email == null || password == null) {
            return Result.error(ResultCode.BAD_REQUEST, "邮箱和密码不能为空");
        }

        // 调用AuthService进行登录验证
        Map<String, Object> user = authService.login(email, password);

        Long userId = ((Number) user.get("id")).longValue();
        String username = (String) user.get("username");

        // 生成Token
        String token = jwtUtil.generateToken(userId, username);
        String refreshToken = jwtUtil.generateRefreshToken(userId, username);

        // 计算过期时间（根据remember_me决定）
        long expiration = rememberMe ? 604800000L : 86400000L; // 7天或1天
        long expiresAt = System.currentTimeMillis() + expiration;
        String expiresAtStr = java.time.Instant.ofEpochMilli(expiresAt)
                .atZone(java.time.ZoneId.of("UTC"))
                .format(java.time.format.DateTimeFormatter.ISO_INSTANT);

        Map<String, Object> result = new HashMap<>();
        result.put("token", token);
        result.put("expires_at", expiresAtStr);
        result.put("user", user);

        return Result.success("登录成功", result);
    }

    /**
     * 用户登出
     */
    @PostMapping("/logout")
    public Result<?> logout(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        // TODO: 实现登出逻辑（如将Token加入黑名单等）
        return Result.success("已成功登出", null);
    }

    /**
     * 获取当前用户信息
     */
    @GetMapping("/profile")
    public Result<Map<String, Object>> getCurrentUserInfo(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        if (authHeader == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String token = jwtUtil.extractTokenFromHeader(authHeader);
        if (token == null || !jwtUtil.validateToken(token)) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        Long userId = jwtUtil.getUserIdFromToken(token);

        // 调用AuthService获取用户详细信息
        Map<String, Object> user = authService.getUserById(userId);

        // 添加统计信息（需要从服务层获取）
        Map<String, Object> stats = new HashMap<>();
        stats.put("total_recognitions", 0);
        stats.put("total_favorites", 0);
        stats.put("total_questions", 0);
        user.put("stats", stats);

        return Result.success(user);
    }

    /**
     * 刷新Token
     */
    @PostMapping("/refresh")
    public Result<Map<String, Object>> refreshToken(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        
        if (authHeader == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String token = jwtUtil.extractTokenFromHeader(authHeader);
        if (token == null || !jwtUtil.validateToken(token)) {
            return Result.error(ResultCode.TOKEN_INVALID);
        }

        Long userId = jwtUtil.getUserIdFromToken(token);
        String username = jwtUtil.getUsernameFromToken(token);

        // 生成新的Token
        String newToken = jwtUtil.generateToken(userId, username);

        // 计算过期时间
        long expiresAt = System.currentTimeMillis() + 86400000L;
        String expiresAtStr = java.time.Instant.ofEpochMilli(expiresAt)
                .atZone(java.time.ZoneId.of("UTC"))
                .format(java.time.format.DateTimeFormatter.ISO_INSTANT);

        Map<String, Object> result = new HashMap<>();
        result.put("token", newToken);
        result.put("expires_at", expiresAtStr);

        return Result.success(result);
    }
}

