package com.beishuo.repository;

import com.beishuo.entity.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/**
 * 对话数据访问接口
 */
public interface ConversationRepository extends JpaRepository<Conversation, Long> {
    
    /**
     * 根据用户ID查询对话列表
     */
    List<Conversation> findByUser_Id(Long userId);
    
    /**
     * 根据碑文ID查询对话列表
     */
    List<Conversation> findByInscription_Id(Long inscriptionId);
}
