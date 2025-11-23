package com.beishuo.dto.response;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class InscriptionDetailVO {
    private Long id;
    private Long userId;
    private String title;
    private String imageUrl;
    private String imageId;
    private String originalText;
    private String correctedText;
    private String dynasty;
    private List<String> tags;
    private String description;
    private Integer wordCount;
    private Double confidence;
    private String status;
    private List<Map<String, Object>> columns;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Boolean isFavorite;
}

