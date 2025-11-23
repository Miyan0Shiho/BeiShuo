package com.beishuo.filter;

import com.beishuo.common.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

@Component
public class JwtTokenProvider {

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 从Token中获取认证信息
     */
    public Authentication getAuthentication(String token) {
        if (token == null || !jwtUtil.validateToken(token)) {
            return null;
        }

        Long userId = jwtUtil.getUserIdFromToken(token);
        String username = jwtUtil.getUsernameFromToken(token);

        if (userId == null || username == null) {
            return null;
        }

        // 创建用户详情（这里简化处理，实际可以根据userId从数据库获取用户权限）
        List<SimpleGrantedAuthority> authorities = Collections.singletonList(
                new SimpleGrantedAuthority("ROLE_USER")
        );

        UserDetails userDetails = User.builder()
                .username(String.valueOf(userId))
                .password("")
                .authorities(authorities)
                .build();

        return new UsernamePasswordAuthenticationToken(userDetails, token, authorities);
    }

    /**
     * 验证Token
     */
    public boolean validateToken(String token) {
        return jwtUtil.validateToken(token);
    }

    /**
     * 从请求头中提取Token
     */
    public String extractToken(String authHeader) {
        return jwtUtil.extractTokenFromHeader(authHeader);
    }
}

