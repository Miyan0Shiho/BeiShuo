package com.beishuo.controller;

import com.beishuo.entity.Message;
import com.beishuo.entity.Conversation;
import com.beishuo.repository.MessageRepository;
import com.beishuo.repository.ConversationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 消息控制器
 */
@RestController
@RequestMapping("/message")
public class MessageController extends BaseController {
    
    @Autowired
    private MessageRepository messageRepository;
    
    @Autowired
    private ConversationRepository conversationRepository;
    
    /**
     * 添加对话消息
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> addMessage(@RequestBody Map<String, Object> messageData) {
        Long conversationId = Long.parseLong(messageData.get("conversationId").toString());
        Conversation conversation = conversationRepository.findById(conversationId).orElse(null);
        
        if (conversation != null) {
            Message message = new Message();
            message.setConversation(conversation);
            message.setRole((String) messageData.get("role"));
            message.setContent((String) messageData.get("content"));
            
            Message savedMessage = messageRepository.save(message);
            return ResponseEntity.ok(convertMessageToMap(savedMessage));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 获取对话消息列表
     */
    @GetMapping("/list")
    public ResponseEntity<List<Map<String, Object>>> getMessages(
            @RequestParam Long conversationId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "asc") String order) {
        
        List<Message> messages;
        if (order.equalsIgnoreCase("asc")) {
            messages = messageRepository.findByConversation_IdOrderByCreatedAtAsc(conversationId);
        } else {
            messages = messageRepository.findByConversation_IdOrderByCreatedAtDesc(conversationId);
        }
        
        List<Map<String, Object>> result = messages.stream()
                .map(this::convertMessageToMap)
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }
    
    /**
     * 更新对话消息状态
     */
    @PutMapping("/{id}/status")
    public ResponseEntity<Map<String, Object>> updateMessageStatus(@PathVariable Long id, @RequestBody Map<String, Object> statusData) {
        // 这里应该更新消息状态
        // 但为了简化，我们先只返回成功
        return ResponseEntity.ok(new HashMap<>());
    }
    
    /**
     * 将Message对象转换为Map
     */
    private Map<String, Object> convertMessageToMap(Message message) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", message.getId());
        result.put("conversationId", message.getConversation().getId());
        result.put("role", message.getRole());
        result.put("content", message.getContent());
        result.put("createdAt", message.getCreatedAt());
        return result;
    }
}
