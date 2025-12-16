package com.beishuo.entity;

import lombok.Data;
import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 知识库实体类
 */
@Data
@Entity
@Table(name = "knowledge")
public class Knowledge {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(length = 50)
    private String category;

    @Column(length = 50)
    private String dynasty;

    @Column(columnDefinition = "TEXT")
    private String tags;

    @Column(length = 200)
    private String source;

    @Column(length = 20, columnDefinition = "DEFAULT 'active'")
    private String status;

    @ManyToOne
    @JoinColumn(name = "created_by")
    private User createdBy;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
