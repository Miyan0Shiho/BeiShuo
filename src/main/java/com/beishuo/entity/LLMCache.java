package com.beishuo.entity;

import lombok.Data;
import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * LLM缓存实体类
 */
@Data
@Entity
@Table(name = "llm_cache")
public class LLMCache {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "prompt_key", nullable = false, length = 64)
    private String promptKey;

    @Column(name = "context_fingerprint", nullable = false, length = 64)
    private String contextFingerprint;

    @Column(name = "message_id", nullable = false)
    private Long messageId;

    @Column(name = "citations_fingerprint", length = 64)
    private String citationsFingerprint;

    @Column(name = "model_key", nullable = false, length = 100)
    private String modelKey;

    @Column(name = "model_provider", nullable = false, length = 50)
    private String modelProvider;

    @Column(name = "token_count")
    private Integer tokenCount;

    @Column(name = "hit_count", nullable = false, columnDefinition = "int unsigned default 0")
    private Integer hitCount;

    @Column(name = "expires_at", nullable = false)
    private LocalDateTime expiresAt;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
