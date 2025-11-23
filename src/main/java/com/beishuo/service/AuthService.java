package com.beishuo.service;

import com.beishuo.client.DatabaseClient;
import com.beishuo.common.ResultCode;
import com.beishuo.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    @Autowired
    private DatabaseClient databaseClient;

    @Autowired(required = false)
    private PasswordEncoder passwordEncoder;

    @Value("${cache.user-info-ttl:1800}")
    private Long userInfoTtl;

    /**
     * 用户注册
     */
    public Map<String, Object> register(String email, String password, String username) {
        // 检查用户是否已存在
        Map<String, Object> existingUser = databaseClient.getUserByEmail(email);
        if (existingUser != null) {
            throw new BusinessException(ResultCode.USER_ALREADY_EXISTS);
        }

        // 加密密码
        String encodedPassword = encodePassword(password);

        // 创建用户数据
        Map<String, Object> userData = new HashMap<>();
        userData.put("email", email);
        userData.put("password", encodedPassword);
        userData.put("username", username);

        // 调用数据库API创建用户
        Map<String, Object> user = databaseClient.createUser(userData);
        if (user == null) {
            throw new BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "用户创建失败");
        }

        logger.info("用户注册成功: email={}, username={}", email, username);
        return user;
    }

    /**
     * 用户登录
     */
    public Map<String, Object> login(String email, String password) {
        // 查询用户
        Map<String, Object> user = databaseClient.getUserByEmail(email);
        if (user == null) {
            throw new BusinessException(ResultCode.INVALID_CREDENTIALS);
        }

        // 验证密码
        String storedPassword = (String) user.get("password");
        if (!verifyPassword(password, storedPassword)) {
            throw new BusinessException(ResultCode.INVALID_CREDENTIALS);
        }

        logger.info("用户登录成功: email={}", email);
        return user;
    }

    /**
     * 根据ID获取用户信息
     */
    public Map<String, Object> getUserById(Long userId) {
        Map<String, Object> user = databaseClient.getUserById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        return user;
    }

    /**
     * 更新用户信息
     */
    public void updateUser(Long userId, Map<String, Object> userData) {
        // 如果包含密码，需要加密
        if (userData.containsKey("password")) {
            String password = (String) userData.get("password");
            userData.put("password", encodePassword(password));
        }

        databaseClient.updateUser(userId, userData);
        logger.info("用户信息更新成功: userId={}", userId);
    }

    /**
     * 加密密码
     */
    private String encodePassword(String password) {
        if (passwordEncoder != null) {
            return passwordEncoder.encode(password);
        }
        // 如果没有配置PasswordEncoder，使用简单的哈希（生产环境必须配置）
        logger.warn("未配置PasswordEncoder，使用简单哈希（不安全）");
        return String.valueOf(password.hashCode());
    }

    /**
     * 验证密码
     */
    private boolean verifyPassword(String rawPassword, String encodedPassword) {
        if (passwordEncoder != null) {
            return passwordEncoder.matches(rawPassword, encodedPassword);
        }
        // 如果没有配置PasswordEncoder，使用简单比较（生产环境必须配置）
        logger.warn("未配置PasswordEncoder，使用简单比较（不安全）");
        return String.valueOf(rawPassword.hashCode()).equals(encodedPassword);
    }
}

