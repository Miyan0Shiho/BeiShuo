package com.beishuo.repository;

import com.beishuo.entity.Message;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/**
 * 消息数据访问接口
 */
public interface MessageRepository extends JpaRepository<Message, Long> {
    
    /**
     * 根据对话ID查询消息列表
     */
    List<Message> findByConversation_IdOrderByCreatedAtAsc(Long conversationId);
    
    /**
     * 根据对话ID查询消息列表（按创建时间降序）
     */
    List<Message> findByConversation_IdOrderByCreatedAtDesc(Long conversationId);
    
    /**
     * 删除对话下的所有消息
     */
    void deleteByConversation_Id(Long conversationId);
}
