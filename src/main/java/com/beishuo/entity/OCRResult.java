package com.beishuo.entity;

import com.fasterxml.jackson.databind.JsonNode;
import com.vladmihalcea.hibernate.type.json.JsonBinaryType;
import lombok.Data;
import org.hibernate.annotations.Type;
import org.hibernate.annotations.TypeDef;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * OCR识别结果实体类
 */
@Data
@Entity
@Table(name = "ocr_jobs")
@TypeDef(name = "jsonb", typeClass = JsonBinaryType.class)
public class OCRResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "asset_id")
    private Long assetId;

    @Column(name = "status", nullable = false, length = 20, columnDefinition = "varchar(20) default 'pending'")
    private String status;

    @Column(name = "vendor", nullable = false)
    private String vendor;

    @Type(type = "jsonb")
    @Column(name = "params", columnDefinition = "json")
    private JsonNode params;

    @Column(name = "confidence")
    private Double confidence;

    @Column(name = "duration_ms")
    private Integer durationMs;

    @Column(name = "retries")
    private Integer retries;

    @Column(name = "error_message", columnDefinition = "text")
    private String errorMessage;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
