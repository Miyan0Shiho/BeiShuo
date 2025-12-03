package com.beishuo.controller;

import com.beishuo.entity.User;
import com.beishuo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 用户控制器
 */
@RestController
@RequestMapping("/user")
public class UserController extends BaseController {
    
    @Autowired
    private UserRepository userRepository;
    
    /**
     * 根据邮箱查询用户
     */
    @GetMapping("/email/{email}")
    public ResponseEntity<Map<String, Object>> getUserByEmail(@PathVariable String email) {
        User user = userRepository.findByEmail(email);
        if (user != null) {
            return ResponseEntity.ok(convertUserToMap(user));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 根据ID查询用户
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable Long id) {
        User user = userRepository.findById(id).orElse(null);
        if (user != null) {
            return ResponseEntity.ok(convertUserToMap(user));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 创建用户
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody Map<String, Object> userData) {
        User user = new User();
        user.setUsername((String) userData.get("username"));
        user.setEmail((String) userData.get("email"));
        user.setPasswordHash((String) userData.get("passwordHash"));
        user.setDisplayName((String) userData.get("displayName"));
        user.setAvatarUrl((String) userData.get("avatarUrl"));
        user.setRole((String) userData.getOrDefault("role", "user"));
        
        User savedUser = userRepository.save(user);
        return ResponseEntity.ok(convertUserToMap(savedUser));
    }
    
    /**
     * 更新用户信息
     */
    @PutMapping("/{id}")
    public ResponseEntity<Void> updateUser(@PathVariable Long id, @RequestBody Map<String, Object> userData) {
        User user = userRepository.findById(id).orElse(null);
        if (user != null) {
            if (userData.containsKey("username")) {
                user.setUsername((String) userData.get("username"));
            }
            if (userData.containsKey("email")) {
                user.setEmail((String) userData.get("email"));
            }
            if (userData.containsKey("passwordHash")) {
                user.setPasswordHash((String) userData.get("passwordHash"));
            }
            if (userData.containsKey("displayName")) {
                user.setDisplayName((String) userData.get("displayName"));
            }
            if (userData.containsKey("avatarUrl")) {
                user.setAvatarUrl((String) userData.get("avatarUrl"));
            }
            if (userData.containsKey("role")) {
                user.setRole((String) userData.get("role"));
            }
            
            userRepository.save(user);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 将User对象转换为Map
     */
    private Map<String, Object> convertUserToMap(User user) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", user.getId());
        result.put("username", user.getUsername());
        result.put("email", user.getEmail());
        result.put("passwordHash", user.getPasswordHash());
        result.put("displayName", user.getDisplayName());
        result.put("avatarUrl", user.getAvatarUrl());
        result.put("role", user.getRole());
        result.put("createdAt", user.getCreatedAt());
        result.put("updatedAt", user.getUpdatedAt());
        return result;
    }
}
