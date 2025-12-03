package com.beishuo.controller;

import com.beishuo.entity.Inscription;
import com.beishuo.entity.User;
import com.beishuo.repository.InscriptionRepository;
import com.beishuo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 碑文控制器
 */
@RestController
@RequestMapping("/inscription")
public class InscriptionController extends BaseController {
    
    @Autowired
    private InscriptionRepository inscriptionRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    /**
     * 查询碑文列表
     */
    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getInscriptionList(
            @RequestParam(required = false) Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String sort) {
        
        Sort sortObj = Sort.unsorted();
        if (sort != null) {
            String[] sortParts = sort.split(",");
            if (sortParts.length == 2) {
                if (sortParts[1].equalsIgnoreCase("desc")) {
                    sortObj = Sort.by(Sort.Direction.DESC, sortParts[0]);
                } else {
                    sortObj = Sort.by(Sort.Direction.ASC, sortParts[0]);
                }
            }
        }
        
        Pageable pageable = PageRequest.of(page, size, sortObj);
        
        if (userId != null) {
            return ResponseEntity.ok(buildPageResult(inscriptionRepository.findByCreatedBy_Id(userId, pageable)));
        } else {
            return ResponseEntity.ok(buildPageResult(inscriptionRepository.findByStatus("active", pageable)));
        }
    }
    
    /**
     * 根据ID查询碑文详情
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getInscriptionById(@PathVariable Long id) {
        Inscription inscription = inscriptionRepository.findById(id).orElse(null);
        if (inscription != null) {
            return ResponseEntity.ok(convertInscriptionToMap(inscription));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 创建碑文记录
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createInscription(@RequestBody Map<String, Object> inscriptionData) {
        Inscription inscription = new Inscription();
        inscription.setTitle((String) inscriptionData.get("title"));
        inscription.setContent((String) inscriptionData.get("content"));
        inscription.setDynasty((String) inscriptionData.get("dynasty"));
        inscription.setLocation((String) inscriptionData.get("location"));
        inscription.setAuthor((String) inscriptionData.get("author"));
        inscription.setCreatedYear((String) inscriptionData.get("createdYear"));
        inscription.setImageUrl((String) inscriptionData.get("imageUrl"));
        inscription.setStatus((String) inscriptionData.getOrDefault("status", "active"));
        
        if (inscriptionData.containsKey("createdBy")) {
            Long createdById = Long.parseLong(inscriptionData.get("createdBy").toString());
            User createdBy = userRepository.findById(createdById).orElse(null);
            if (createdBy != null) {
                inscription.setCreatedBy(createdBy);
            }
        }
        
        Inscription savedInscription = inscriptionRepository.save(inscription);
        return ResponseEntity.ok(convertInscriptionToMap(savedInscription));
    }
    
    /**
     * 更新碑文
     */
    @PutMapping("/{id}")
    public ResponseEntity<Void> updateInscription(@PathVariable Long id, @RequestBody Map<String, Object> inscriptionData) {
        Inscription inscription = inscriptionRepository.findById(id).orElse(null);
        if (inscription != null) {
            if (inscriptionData.containsKey("title")) {
                inscription.setTitle((String) inscriptionData.get("title"));
            }
            if (inscriptionData.containsKey("content")) {
                inscription.setContent((String) inscriptionData.get("content"));
            }
            if (inscriptionData.containsKey("dynasty")) {
                inscription.setDynasty((String) inscriptionData.get("dynasty"));
            }
            if (inscriptionData.containsKey("location")) {
                inscription.setLocation((String) inscriptionData.get("location"));
            }
            if (inscriptionData.containsKey("author")) {
                inscription.setAuthor((String) inscriptionData.get("author"));
            }
            if (inscriptionData.containsKey("createdYear")) {
                inscription.setCreatedYear((String) inscriptionData.get("createdYear"));
            }
            if (inscriptionData.containsKey("imageUrl")) {
                inscription.setImageUrl((String) inscriptionData.get("imageUrl"));
            }
            if (inscriptionData.containsKey("status")) {
                inscription.setStatus((String) inscriptionData.get("status"));
            }
            
            inscriptionRepository.save(inscription);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 删除碑文
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteInscription(@PathVariable Long id) {
        Inscription inscription = inscriptionRepository.findById(id).orElse(null);
        if (inscription != null) {
            inscriptionRepository.delete(inscription);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 模糊搜索碑文
     */
    @GetMapping("/search")
    public ResponseEntity<List<Map<String, Object>>> searchInscriptions(@RequestParam String keyword) {
        List<Inscription> inscriptions = inscriptionRepository.searchByKeyword(keyword);
        List<Map<String, Object>> result = inscriptions.stream()
                .map(this::convertInscriptionToMap)
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }
    
    /**
     * 将Inscription对象转换为Map
     */
    private Map<String, Object> convertInscriptionToMap(Inscription inscription) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", inscription.getId());
        result.put("title", inscription.getTitle());
        result.put("content", inscription.getContent());
        result.put("dynasty", inscription.getDynasty());
        result.put("location", inscription.getLocation());
        result.put("author", inscription.getAuthor());
        result.put("createdYear", inscription.getCreatedYear());
        result.put("imageUrl", inscription.getImageUrl());
        result.put("status", inscription.getStatus());
        if (inscription.getCreatedBy() != null) {
            result.put("createdBy", inscription.getCreatedBy().getId());
        }
        result.put("createdAt", inscription.getCreatedAt());
        result.put("updatedAt", inscription.getUpdatedAt());
        return result;
    }
}
