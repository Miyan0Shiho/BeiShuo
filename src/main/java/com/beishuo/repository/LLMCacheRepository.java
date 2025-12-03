package com.beishuo.repository;

import com.beishuo.entity.LLMCache;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * LLM缓存数据访问接口
 */
public interface LLMCacheRepository extends JpaRepository<LLMCache, Long> {
    
    // 不需要根据cacheKey查询的方法，因为现有表结构没有直接的cache_key字段
    // 实际项目中应该根据prompt_key和context_fingerprint进行查询
}

