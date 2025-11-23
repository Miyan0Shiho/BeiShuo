package com.beishuo.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class RedisClient {

    private static final Logger logger = LoggerFactory.getLogger(RedisClient.class);

    @Value("${redis.api.base-url}")
    private String baseUrl;

    private final RestTemplate restTemplate;

    public RedisClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * 设置缓存
     */
    public void set(String key, Object value, Long timeout) {
        String url = baseUrl + "/cache/set";
        Map<String, Object> data = new HashMap<>();
        data.put("key", key);
        data.put("value", value);
        data.put("timeout", timeout);
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(data);
            restTemplate.exchange(url, HttpMethod.POST, request, Void.class);
        } catch (Exception e) {
            logger.error("设置缓存失败: key={}", key, e);
        }
    }

    /**
     * 获取缓存
     */
    public <T> T get(String key, Class<T> clazz) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/cache/get")
                .queryParam("key", key)
                .toUriString();
        try {
            ResponseEntity<T> response = restTemplate.exchange(
                    url, HttpMethod.GET, null, clazz
            );
            return response.getBody();
        } catch (Exception e) {
            logger.debug("获取缓存失败: key={}", key, e);
            return null;
        }
    }

    /**
     * 获取缓存（泛型）
     */
    public <T> T get(String key, ParameterizedTypeReference<T> typeReference) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/cache/get")
                .queryParam("key", key)
                .toUriString();
        try {
            ResponseEntity<T> response = restTemplate.exchange(
                    url, HttpMethod.GET, null, typeReference
            );
            return response.getBody();
        } catch (Exception e) {
            logger.debug("获取缓存失败: key={}", key, e);
            return null;
        }
    }

    /**
     * 删除缓存
     */
    public void delete(String key) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/cache/delete")
                .queryParam("key", key)
                .toUriString();
        try {
            restTemplate.exchange(url, HttpMethod.DELETE, null, Void.class);
        } catch (Exception e) {
            logger.error("删除缓存失败: key={}", key, e);
        }
    }

    /**
     * 检查key是否存在
     */
    public Boolean exists(String key) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/cache/exists")
                .queryParam("key", key)
                .toUriString();
        try {
            ResponseEntity<Boolean> response = restTemplate.exchange(
                    url, HttpMethod.GET, null, Boolean.class
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("检查key是否存在失败: key={}", key, e);
            return false;
        }
    }

    /**
     * 模糊搜索key
     */
    public List<String> searchKeys(String pattern) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/cache/search")
                .queryParam("pattern", pattern)
                .toUriString();
        try {
            ResponseEntity<List<String>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<List<String>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("搜索key失败: pattern={}", pattern, e);
            return null;
        }
    }
}

