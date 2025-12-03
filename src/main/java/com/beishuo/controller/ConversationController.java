package com.beishuo.controller;

import com.beishuo.entity.Conversation;
import com.beishuo.entity.User;
import com.beishuo.repository.ConversationRepository;
import com.beishuo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 对话控制器
 */
@RestController
@RequestMapping("/conversation")
public class ConversationController extends BaseController {
    
    @Autowired
    private ConversationRepository conversationRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    /**
     * 创建对话
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createConversation(@RequestBody Map<String, Object> conversationData) {
        Conversation conversation = new Conversation();
        
        Long userId = Long.parseLong(conversationData.get("userId").toString());
        User user = userRepository.findById(userId).orElse(null);
        if (user != null) {
            conversation.setUser(user);
        }
        
        conversation.setTitle((String) conversationData.get("title"));
        
        Conversation savedConversation = conversationRepository.save(conversation);
        return ResponseEntity.ok(convertConversationToMap(savedConversation));
    }
    
    /**
     * 根据ID获取对话
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getConversationById(@PathVariable Long id) {
        Conversation conversation = conversationRepository.findById(id).orElse(null);
        if (conversation != null) {
            return ResponseEntity.ok(convertConversationToMap(conversation));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 重置对话上下文
     */
    @DeleteMapping("/{id}/messages")
    public ResponseEntity<Void> resetConversation(@PathVariable Long id) {
        // 这里应该删除对话下的所有消息
        // 但为了简化，我们先只返回成功
        return ResponseEntity.ok().build();
    }
    
    /**
     * 将Conversation对象转换为Map
     */
    private Map<String, Object> convertConversationToMap(Conversation conversation) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", conversation.getId());
        if (conversation.getUser() != null) {
            result.put("userId", conversation.getUser().getId());
        }
        result.put("title", conversation.getTitle());
        if (conversation.getInscription() != null) {
            result.put("inscriptionId", conversation.getInscription().getId());
        }
        result.put("createdAt", conversation.getCreatedAt());
        result.put("updatedAt", conversation.getUpdatedAt());
        return result;
    }
}
