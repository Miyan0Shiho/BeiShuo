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
public class DatabaseClient {

    private static final Logger logger = LoggerFactory.getLogger(DatabaseClient.class);

    @Value("${database.api.base-url}")
    private String baseUrl;

    private final RestTemplate restTemplate;

    public DatabaseClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    // ========== 用户相关 ==========

    /**
     * 根据邮箱查询用户
     */
    public Map<String, Object> getUserByEmail(String email) {
        String url = baseUrl + "/user/email/" + email;
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询用户失败: email={}", email, e);
            return null;
        }
    }

    /**
     * 根据ID查询用户
     */
    public Map<String, Object> getUserById(Long id) {
        String url = baseUrl + "/user/" + id;
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询用户失败: id={}", id, e);
            return null;
        }
    }

    /**
     * 创建用户
     */
    public Map<String, Object> createUser(Map<String, Object> userData) {
        String url = baseUrl + "/user";
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(userData);
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, request,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("创建用户失败", e);
            throw new RuntimeException("创建用户失败", e);
        }
    }

    /**
     * 更新用户信息
     */
    public void updateUser(Long id, Map<String, Object> userData) {
        String url = baseUrl + "/user/" + id;
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(userData);
            restTemplate.exchange(url, HttpMethod.PUT, request, Void.class);
        } catch (Exception e) {
            logger.error("更新用户失败: id={}", id, e);
            throw new RuntimeException("更新用户失败", e);
        }
    }

    // ========== 碑文相关 ==========

    /**
     * 查询碑文列表（支持分页、排序、搜索）
     */
    public Map<String, Object> getInscriptionList(Long userId, Integer page, Integer size, String sort, String keyword) {
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(baseUrl + "/inscription/list")
                .queryParam("userId", userId)
                .queryParam("page", page)
                .queryParam("size", size);

        if (sort != null) {
            builder.queryParam("sort", sort);
        }
        if (keyword != null) {
            builder.queryParam("keyword", keyword);
        }

        String url = builder.toUriString();
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询碑文列表失败: userId={}, page={}, size={}", userId, page, size, e);
            return null;
        }
    }

    /**
     * 根据ID查询碑文详情
     */
    public Map<String, Object> getInscriptionById(Long id) {
        String url = baseUrl + "/inscription/" + id;
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询碑文详情失败: id={}", id, e);
            return null;
        }
    }

    /**
     * 创建碑文记录
     */
    public Map<String, Object> createInscription(Map<String, Object> inscriptionData) {
        String url = baseUrl + "/inscription";
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(inscriptionData);
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, request,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("创建碑文失败", e);
            throw new RuntimeException("创建碑文失败", e);
        }
    }

    /**
     * 更新碑文
     */
    public void updateInscription(Long id, Map<String, Object> inscriptionData) {
        String url = baseUrl + "/inscription/" + id;
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(inscriptionData);
            restTemplate.exchange(url, HttpMethod.PUT, request, Void.class);
        } catch (Exception e) {
            logger.error("更新碑文失败: id={}", id, e);
            throw new RuntimeException("更新碑文失败", e);
        }
    }

    /**
     * 删除碑文
     */
    public void deleteInscription(Long id) {
        String url = baseUrl + "/inscription/" + id;
        try {
            restTemplate.exchange(url, HttpMethod.DELETE, null, Void.class);
        } catch (Exception e) {
            logger.error("删除碑文失败: id={}", id, e);
            throw new RuntimeException("删除碑文失败", e);
        }
    }

    /**
     * 模糊搜索碑文
     */
    public List<Map<String, Object>> searchInscriptions(String keyword) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/inscription/search")
                .queryParam("keyword", keyword)
                .toUriString();
        try {
            ResponseEntity<List<Map<String, Object>>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<List<Map<String, Object>>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("搜索碑文失败: keyword={}", keyword, e);
            return null;
        }
    }

    // ========== 知识库相关 ==========

    /**
     * 查询知识库列表
     */
    public Map<String, Object> getKnowledgeList(Integer page, Integer size, String keyword, String dynasty, String category) {
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(baseUrl + "/knowledge/list")
                .queryParam("page", page)
                .queryParam("size", size);

        if (keyword != null) {
            builder.queryParam("keyword", keyword);
        }
        if (dynasty != null) {
            builder.queryParam("dynasty", dynasty);
        }
        if (category != null) {
            builder.queryParam("category", category);
        }

        String url = builder.toUriString();
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询知识库列表失败", e);
            return null;
        }
    }

    /**
     * 根据ID查询知识库详情
     */
    public Map<String, Object> getKnowledgeById(Long id) {
        String url = baseUrl + "/knowledge/" + id;
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询知识库详情失败: id={}", id, e);
            return null;
        }
    }

    /**
     * 搜索知识库
     */
    public List<Map<String, Object>> searchKnowledge(String keyword, String dynasty, String tags) {
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(baseUrl + "/knowledge/search");

        if (keyword != null) {
            builder.queryParam("keyword", keyword);
        }
        if (dynasty != null) {
            builder.queryParam("dynasty", dynasty);
        }
        if (tags != null) {
            builder.queryParam("tags", tags);
        }

        String url = builder.toUriString();
        try {
            ResponseEntity<List<Map<String, Object>>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<List<Map<String, Object>>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("搜索知识库失败: keyword={}", keyword, e);
            return null;
        }
    }

    // ========== 收藏相关 ==========

    /**
     * 添加收藏
     */
    public void addFavorite(Long userId, String type, Long targetId) {
        String url = baseUrl + "/favorite";
        Map<String, Object> data = new HashMap<>();
        data.put("userId", userId);
        data.put("type", type); // "inscription" 或 "knowledge"
        data.put("targetId", targetId);
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(data);
            restTemplate.exchange(url, HttpMethod.POST, request, Void.class);
        } catch (Exception e) {
            logger.error("添加收藏失败: userId={}, type={}, targetId={}", userId, type, targetId, e);
            throw new RuntimeException("添加收藏失败", e);
        }
    }

    /**
     * 取消收藏
     */
    public void removeFavorite(Long userId, String type, Long targetId) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/favorite")
                .queryParam("userId", userId)
                .queryParam("type", type)
                .queryParam("targetId", targetId)
                .toUriString();
        try {
            restTemplate.exchange(url, HttpMethod.DELETE, null, Void.class);
        } catch (Exception e) {
            logger.error("取消收藏失败: userId={}, type={}, targetId={}", userId, type, targetId, e);
            throw new RuntimeException("取消收藏失败", e);
        }
    }

    /**
     * 查询收藏列表
     */
    public List<Map<String, Object>> getFavoriteList(Long userId, String type) {
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(baseUrl + "/favorite/list")
                .queryParam("userId", userId);

        if (type != null) {
            builder.queryParam("type", type);
        }

        String url = builder.toUriString();
        try {
            ResponseEntity<List<Map<String, Object>>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<List<Map<String, Object>>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("查询收藏列表失败: userId={}, type={}", userId, type, e);
            return null;
        }
    }
    
    // ========== OCR相关 ==========
    
    /**
     * 根据图片哈希值查询OCR结果
     */
    public Map<String, Object> getOCRResultByImageHash(String imageHash) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/ocr/result")
                .queryParam("imageHash", imageHash)
                .toUriString();
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET, null,
                    new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            return response.getBody();
        } catch (Exception e) {
            logger.error("根据图片哈希查询OCR结果失败: imageHash={}", imageHash, e);
            return null;
        }
    }
    
    /**
     * 创建OCR任务
     */
    public void createOCRJob(Map<String, Object> ocrJobData) {
        String url = baseUrl + "/ocr/job";
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(ocrJobData);
            restTemplate.exchange(url, HttpMethod.POST, request, Void.class);
            logger.info("创建OCR任务成功: taskId={}", ocrJobData.get("task_id"));
        } catch (Exception e) {
            logger.error("创建OCR任务失败", e);
            throw new RuntimeException("创建OCR任务失败", e);
        }
    }
    
    /**
     * 更新OCR任务状态
     */
    public void updateOCRJobStatus(String taskId, String status) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/ocr/job/status")
                .queryParam("taskId", taskId)
                .queryParam("status", status)
                .toUriString();
        try {
            restTemplate.exchange(url, HttpMethod.PUT, null, Void.class);
            logger.info("更新OCR任务状态成功: taskId={}, status={}", taskId, status);
        } catch (Exception e) {
            logger.error("更新OCR任务状态失败: taskId={}, status={}", taskId, status, e);
            throw new RuntimeException("更新OCR任务状态失败", e);
        }
    }
    
    /**
     * 保存OCR识别结果
     */
    public void saveOCRResult(String taskId, Map<String, Object> resultData) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/ocr/result")
                .queryParam("taskId", taskId)
                .toUriString();
        try {
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(resultData);
            restTemplate.exchange(url, HttpMethod.POST, request, Void.class);
            logger.info("保存OCR识别结果成功: taskId={}", taskId);
        } catch (Exception e) {
            logger.error("保存OCR识别结果失败: taskId={}", taskId, e);
            throw new RuntimeException("保存OCR识别结果失败", e);
        }
    }
}