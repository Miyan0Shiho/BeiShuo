package com.beishuo.dto.response;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class KnowledgeVO {
    private Long id;
    private String title;
    private String imageUrl;
    private String dynasty;
    private List<String> tags;
    private String description;
    private String author;
    private String location;
    private Integer viewCount;
    private Integer favoriteCount;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Boolean isFavorite;
}

