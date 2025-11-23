package com.beishuo.dto.response;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class InscriptionVO {
    private Long id;
    private String title;
    private String imageUrl;
    private String dynasty;
    private List<String> tags;
    private String description;
    private Integer wordCount;
    private Double confidence;
    private String status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Boolean isFavorite;
}

