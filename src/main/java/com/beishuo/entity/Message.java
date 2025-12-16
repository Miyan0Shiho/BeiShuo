package com.beishuo.entity;

import lombok.Data;
import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 消息实体类
 */
@Data
@Entity
@Table(name = "messages")
public class Message {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "conversation_id")
    private Conversation conversation;

    @Column(nullable = false, length = 20)
    private String role; // 'user' or 'assistant'

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(updatable = false)
    private LocalDateTime createdAt;
}
