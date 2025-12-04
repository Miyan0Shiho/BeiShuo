package com.beishuo.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.Arrays;
import java.util.List;

@Configuration
public class CorsConfig {

    @Value("${cors.allowed-origins:}")
    private List<String> allowedOrigins;

    @Value("${cors.allowed-methods:}")
    private List<String> allowedMethods;

    @Value("${cors.allowed-headers:}")
    private List<String> allowedHeaders;

    @Value("${cors.allow-credentials:true}")
    private boolean allowCredentials;

    @Value("${cors.max-age:3600}")
    private long maxAge;

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();

        // 设置允许的源（如果没有配置，使用默认值）
        if (allowedOrigins == null || allowedOrigins.isEmpty()) {
            config.setAllowedOrigins(Arrays.asList(
                    "http://localhost:3000",
                    "http://localhost:5173",
                    "http://localhost:8080",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:5173",
                    "http://127.0.0.1:8080"
            ));
        } else {
            config.setAllowedOrigins(allowedOrigins);
        }

        // 设置允许的HTTP方法（如果没有配置，使用默认值）
        if (allowedMethods == null || allowedMethods.isEmpty()) {
            config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        } else {
            config.setAllowedMethods(allowedMethods);
        }

        // 设置允许的请求头
        if (allowedHeaders == null || allowedHeaders.isEmpty() || allowedHeaders.contains("*")) {
            config.addAllowedHeader("*");
        } else {
            config.setAllowedHeaders(allowedHeaders);
        }

        // 是否允许携带凭证
        config.setAllowCredentials(allowCredentials);

        // 预检请求的有效期（秒）
        config.setMaxAge(maxAge);

        // 对所有路径应用CORS配置
        source.registerCorsConfiguration("/**", config);

        return new CorsFilter(source);
    }
}
