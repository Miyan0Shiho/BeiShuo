package com.beishuo.service;

import com.beishuo.client.DatabaseClient;
import com.beishuo.client.RedisClient;
import com.beishuo.common.PageResult;
import com.beishuo.common.ResultCode;
import com.beishuo.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@Service
public class KnowledgeService {

    private static final Logger logger = LoggerFactory.getLogger(KnowledgeService.class);

    @Autowired
    private DatabaseClient databaseClient;

    @Autowired
    private RedisClient redisClient;

    @Value("${cache.knowledge-list-ttl:600}")
    private Long knowledgeListTtl;

    @Value("${cache.search-result-ttl:600}")
    private Long searchResultTtl;

    /**
     * 获取知识库列表
     */
    public PageResult<Map<String, Object>> getKnowledgeList(Integer page, Integer size, String keyword, String dynasty, String category) {
        // 构建缓存key
        String cacheKey = String.format("knowledge:list:%d:%d:%s:%s:%s", page, size, keyword, dynasty, category);

        // 先查缓存
        PageResult<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<PageResult<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // 查询数据库
        Map<String, Object> dbResult = databaseClient.getKnowledgeList(page, size, keyword, dynasty, category);
        if (dbResult == null) {
            return PageResult.of(Collections.emptyList(), 0L, page, size);
        }

        // 转换为PageResult
        List<Map<String, Object>> list = (List<Map<String, Object>>) dbResult.get("list");
        Long total = dbResult.get("total") != null ? ((Number) dbResult.get("total")).longValue() : 0L;
        PageResult<Map<String, Object>> result = PageResult.of(list != null ? list : Collections.emptyList(), total, page, size);

        // 写入缓存
        redisClient.set(cacheKey, result, knowledgeListTtl);

        return result;
    }

    /**
     * 获取知识库详情
     */
    public Map<String, Object> getKnowledgeDetail(Long id) {
        Map<String, Object> knowledge = databaseClient.getKnowledgeById(id);
        if (knowledge == null) {
            throw new BusinessException(ResultCode.KNOWLEDGE_NOT_FOUND);
        }
        return knowledge;
    }

    /**
     * 搜索知识库
     */
    public List<Map<String, Object>> searchKnowledge(String keyword, String dynasty, String tags, Integer page, Integer size) {
        // 构建缓存key
        String cacheKey = String.format("knowledge:search:%s:%s:%s:%d:%d", keyword, dynasty, tags, page, size);

        // 先查缓存
        List<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // 查询数据库
        List<Map<String, Object>> results = databaseClient.searchKnowledge(keyword, dynasty, tags);
        if (results == null) {
            results = Collections.emptyList();
        }

        // 写入缓存
        redisClient.set(cacheKey, results, searchResultTtl);

        return results;
    }

    /**
     * 收藏知识库
     */
    public void favoriteKnowledge(Long id, Long userId) {
        databaseClient.addFavorite(userId, "knowledge", id);
        logger.info("收藏知识库成功: userId={}, knowledgeId={}", userId, id);
    }

    /**
     * 取消收藏
     */
    public void unfavoriteKnowledge(Long id, Long userId) {
        databaseClient.removeFavorite(userId, "knowledge", id);
        logger.info("取消收藏成功: userId={}, knowledgeId={}", userId, id);
    }

    /**
     * 获取推荐知识库
     */
    public List<Map<String, Object>> getRecommendKnowledge(Integer page, Integer size) {
        // 构建缓存key
        String cacheKey = String.format("knowledge:recommend:%d:%d", page, size);

        // 先查缓存
        List<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // TODO: 实现推荐算法，当前返回热门列表
        Map<String, Object> dbResult = databaseClient.getKnowledgeList(page, size, null, null, null);
        List<Map<String, Object>> list = dbResult != null ? (List<Map<String, Object>>) dbResult.get("list") : Collections.emptyList();

        // 写入缓存
        redisClient.set(cacheKey, list, knowledgeListTtl);

        return list;
    }

    /**
     * 获取最新收录
     */
    public List<Map<String, Object>> getLatestKnowledge(Integer page, Integer size) {
        // 构建缓存key
        String cacheKey = String.format("knowledge:latest:%d:%d", page, size);

        // 先查缓存
        List<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // TODO: 按创建时间倒序查询，当前返回列表
        Map<String, Object> dbResult = databaseClient.getKnowledgeList(page, size, null, null, null);
        List<Map<String, Object>> list = dbResult != null ? (List<Map<String, Object>>) dbResult.get("list") : Collections.emptyList();

        // 写入缓存
        redisClient.set(cacheKey, list, knowledgeListTtl);

        return list;
    }
}

