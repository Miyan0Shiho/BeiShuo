package com.beishuo.controller;

import com.beishuo.entity.Knowledge;
import com.beishuo.repository.KnowledgeRepository;
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
 * 知识库控制器
 */
@RestController
@RequestMapping("/knowledge")
public class KnowledgeController extends BaseController {
    
    @Autowired
    private KnowledgeRepository knowledgeRepository;
    
    /**
     * 查询知识库列表
     */
    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getKnowledgeList(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String dynasty,
            @RequestParam(required = false) String category) {
        
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "id"));
        
        if (category != null) {
            return ResponseEntity.ok(buildPageResult(knowledgeRepository.findByCategory(category, pageable)));
        } else if (dynasty != null) {
            return ResponseEntity.ok(buildPageResult(knowledgeRepository.findByDynasty(dynasty, pageable)));
        } else {
            return ResponseEntity.ok(buildPageResult(knowledgeRepository.findAll(pageable)));
        }
    }
    
    /**
     * 根据ID查询知识库详情
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getKnowledgeById(@PathVariable Long id) {
        Knowledge knowledge = knowledgeRepository.findById(id).orElse(null);
        if (knowledge != null) {
            return ResponseEntity.ok(convertKnowledgeToMap(knowledge));
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 搜索知识库
     */
    @GetMapping("/search")
    public ResponseEntity<List<Map<String, Object>>> searchKnowledge(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String dynasty,
            @RequestParam(required = false) String tags) {
        
        List<Knowledge> knowledgeList;
        if (keyword != null) {
            knowledgeList = knowledgeRepository.searchByKeyword(keyword);
        } else if (tags != null) {
            knowledgeList = knowledgeRepository.searchByTag(tags);
        } else {
            knowledgeList = knowledgeRepository.findAll();
        }
        
        List<Map<String, Object>> result = knowledgeList.stream()
                .map(this::convertKnowledgeToMap)
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }
    
    /**
     * 将Knowledge对象转换为Map
     */
    private Map<String, Object> convertKnowledgeToMap(Knowledge knowledge) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", knowledge.getId());
        result.put("title", knowledge.getTitle());
        result.put("content", knowledge.getContent());
        result.put("category", knowledge.getCategory());
        result.put("dynasty", knowledge.getDynasty());
        result.put("tags", knowledge.getTags());
        result.put("source", knowledge.getSource());
        result.put("status", knowledge.getStatus());
        if (knowledge.getCreatedBy() != null) {
            result.put("createdBy", knowledge.getCreatedBy().getId());
        }
        result.put("createdAt", knowledge.getCreatedAt());
        result.put("updatedAt", knowledge.getUpdatedAt());
        return result;
    }
}
