package com.beishuo.entity;

import lombok.Data;
import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 碑文实体类
 */
@Data
@Entity
@Table(name = "inscriptions")
public class Inscription {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(length = 50)
    private String dynasty;

    @Column(length = 200)
    private String location;

    @Column(length = 100)
    private String author;

    @Column(length = 50)
    private String createdYear;

    @Column(length = 255)
    private String imageUrl;

    @Column(length = 20, columnDefinition = "DEFAULT 'active'")
    private String status;

    @ManyToOne
    @JoinColumn(name = "created_by")
    private User createdBy;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
