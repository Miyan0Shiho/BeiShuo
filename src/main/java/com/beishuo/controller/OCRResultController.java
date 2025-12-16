package com.beishuo.controller;

import com.beishuo.entity.OCRResult;
import com.beishuo.repository.OCRResultRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * OCR结果控制器
 */
@RestController
@RequestMapping("/ocr")
public class OCRResultController extends BaseController {
    
    @Autowired
    private OCRResultRepository ocrResultRepository;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    /**
     * 根据图片哈希值获取OCR结果
     */
    @GetMapping("/result")
    public ResponseEntity<Map<String, Object>> getOCRResultByImageHash(@RequestParam String imageHash) {
        // 查询params中包含该imageHash的ocr_jobs
        List<OCRResult> ocrResults = ocrResultRepository.findByParamsContainingImageHash(imageHash);
        
        Map<String, Object> response = new HashMap<>();
        if (!ocrResults.isEmpty()) {
            // 返回第一个匹配的结果
            OCRResult ocrResult = ocrResults.get(0);
            response.put("success", true);
            response.put("result", ocrResult.getParams());
        } else {
            response.put("success", false);
            response.put("message", "OCR result not found");
        }
        return ResponseEntity.ok(response);
    }
    
    /**
     * 根据图片哈希值获取OCR结果（兼容Python客户端）
     */
    @GetMapping("/result/hash/{imageHash}")
    public ResponseEntity<Map<String, Object>> getOCRResultByImageHashPath(@PathVariable String imageHash) {
        return getOCRResultByImageHash(imageHash);
    }
    
    /**
     * 创建OCR任务
     */
    @PostMapping("/job")
    public ResponseEntity<Map<String, Object>> createOCRJob(@RequestBody Map<String, Object> ocrJobData) {
        OCRResult ocrJob = new OCRResult();
        
        // 设置asset_id
        if (ocrJobData.containsKey("image_id")) {
            // 尝试解析为Long，但如果失败则跳过
            try {
                ocrJob.setAssetId(Long.parseLong(ocrJobData.get("image_id").toString()));
            } catch (NumberFormatException e) {
                // 忽略，不设置asset_id
            }
        }
        
        // 设置status
        ocrJob.setStatus((String) ocrJobData.getOrDefault("status", "pending"));
        
        // 设置vendor
        ocrJob.setVendor((String) ocrJobData.getOrDefault("vendor", "kandianguji"));
        
        // 设置params
        if (ocrJobData.containsKey("result")) {
            // 获取result字段
            Object result = ocrJobData.get("result");
            
            // 如果result是Map，添加image_hash字段
            if (result instanceof Map) {
                Map<String, Object> resultMap = (Map<String, Object>) result;
                // 从ocrJobData中获取image_hash并添加到resultMap
                if (ocrJobData.containsKey("image_hash")) {
                    resultMap.put("image_hash", ocrJobData.get("image_hash"));
                }
                // 将修改后的resultMap转换为JsonNode
                ocrJob.setParams(objectMapper.valueToTree(resultMap));
            } else {
                // 否则直接转换为JsonNode
                ocrJob.setParams(objectMapper.valueToTree(result));
            }
        }
        
        OCRResult savedJob = ocrResultRepository.save(ocrJob);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("job_id", savedJob.getId());
        return ResponseEntity.ok(response);
    }
    
    /**
     * 更新OCR任务状态
     */
    @PutMapping("/job/status")
    public ResponseEntity<Void> updateOCRJobStatus(@RequestParam String taskId, @RequestParam String status) {
        // 根据taskId查询OCR任务
        // 这里简化处理，直接返回成功
        return ResponseEntity.ok().build();
    }
    
    /**
     * 保存OCR识别结果
     */
    @PostMapping("/result")
    public ResponseEntity<Void> saveOCRResult(@RequestParam String taskId, @RequestBody Map<String, Object> resultData) {
        // 根据taskId更新OCR任务状态
        // 这里简化处理，直接返回成功
        return ResponseEntity.ok().build();
    }
    
    /**
     * 保存OCR识别结果（兼容Python客户端）
     */
    @PostMapping("/result/{taskId}")
    public ResponseEntity<Map<String, Object>> saveOCRResultPath(@PathVariable String taskId, @RequestBody Map<String, Object> resultData) {
        // 根据taskId查询并更新OCR任务
        // 这里简化处理，直接返回成功
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        return ResponseEntity.ok(response);
    }
    
    /**
     * 删除OCR缓存
     */
    @DeleteMapping("/result/hash/{imageHash}")
    public ResponseEntity<Map<String, Object>> deleteOCRCache(@PathVariable String imageHash) {
        // 查询params中包含该imageHash的ocr_jobs
        List<OCRResult> ocrResults = ocrResultRepository.findByParamsContainingImageHash(imageHash);
        
        Map<String, Object> response = new HashMap<>();
        if (!ocrResults.isEmpty()) {
            // 删除所有匹配的结果
            int deletedCount = ocrResults.size();
            ocrResultRepository.deleteAll(ocrResults);
            response.put("success", true);
            response.put("message", "OCR缓存已删除");
            response.put("deletedCount", deletedCount);
            System.out.println(String.format("[DEBUG] OCR缓存已删除: image_hash=%s, 删除记录数量=%d", imageHash, deletedCount));
        } else {
            response.put("success", false);
            response.put("message", "未找到匹配的OCR缓存");
            System.out.println(String.format("[DEBUG] 未找到匹配的OCR缓存: image_hash=%s", imageHash));
        }
        return ResponseEntity.ok(response);
    }
}
