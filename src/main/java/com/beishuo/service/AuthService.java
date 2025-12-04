package com.beishuo.service;

import com.beishuo.common.ResultCode;
import com.beishuo.common.exception.BusinessException;
import com.beishuo.entity.User;
import com.beishuo.repository.UserRepository;
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
    private UserRepository userRepository;

    @Autowired(required = false)
    private PasswordEncoder passwordEncoder;

    @Value("${cache.user-info-ttl:1800}")
    private Long userInfoTtl;

    /**
     * 用户注册
     */
    public Map<String, Object> register(String email, String password, String username) {
        // 检查邮箱是否已存在
        if (userRepository.existsByEmail(email)) {
            throw new BusinessException(ResultCode.USER_ALREADY_EXISTS);
        }

        // 确保用户名唯一，如果已存在则添加随机后缀
        String uniqueUsername = username;
        if (userRepository.existsByUsername(username)) {
            uniqueUsername = username + "_" + System.currentTimeMillis() % 10000;
        }

        // 创建用户
        User user = new User();
        user.setEmail(email);
        user.setUsername(uniqueUsername);
        user.setDisplayName(username);
        user.setPasswordHash(encodePassword(password));
        user.setRole("user");

        // 保存用户
        User savedUser = userRepository.save(user);
        
        logger.info("用户注册成功: email={}, username={}", email, uniqueUsername);
        return convertToMap(savedUser);
    }

    /**
     * 用户登录
     */
    public Map<String, Object> login(String email, String password) {
        // 查询用户
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException(ResultCode.INVALID_CREDENTIALS));

        // 验证密码
        if (!verifyPassword(password, user.getPasswordHash())) {
            throw new BusinessException(ResultCode.INVALID_CREDENTIALS);
        }

        logger.info("用户登录成功: email={}", email);
        return convertToMap(user);
    }

    /**
     * 根据ID获取用户信息
     */
    public Map<String, Object> getUserById(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ResultCode.USER_NOT_FOUND));
        return convertToMap(user);
    }

    /**
     * 更新用户信息
     */
    public void updateUser(Long userId, Map<String, Object> userData) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ResultCode.USER_NOT_FOUND));
        
        if (userData.containsKey("username")) {
            user.setUsername((String) userData.get("username"));
        }
        if (userData.containsKey("display_name")) {
            user.setDisplayName((String) userData.get("display_name"));
        }
        if (userData.containsKey("avatar_url")) {
            user.setAvatarUrl((String) userData.get("avatar_url"));
        }
        if (userData.containsKey("password")) {
            String password = (String) userData.get("password");
            user.setPasswordHash(encodePassword(password));
        }

        userRepository.save(user);
        logger.info("用户信息更新成功: userId={}", userId);
    }

    /**
     * 转换 User 实体为 Map
     */
    private Map<String, Object> convertToMap(User user) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", user.getId());
        map.put("username", user.getUsername());
        map.put("email", user.getEmail());
        map.put("display_name", user.getDisplayName());
        map.put("avatar_url", user.getAvatarUrl());
        map.put("role", user.getRole());
        map.put("created_at", user.getCreatedAt());
        map.put("updated_at", user.getUpdatedAt());
        return map;
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
