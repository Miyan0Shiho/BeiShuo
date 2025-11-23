package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import com.beishuo.service.InscriptionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/recognition")
public class RecognitionController {

    private static final Logger logger = LoggerFactory.getLogger(RecognitionController.class);

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private InscriptionService inscriptionService;

    /**
     * 开始碑文识别
     */
    @PostMapping("/start")
    public Result<Map<String, Object>> startRecognition(
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String imageId = (String) request.get("image_id");
        String language = (String) request.get("language");
        Map<String, Object> options = (Map<String, Object>) request.get("options");

        if (imageId == null) {
            return Result.error(ResultCode.BAD_REQUEST, "image_id不能为空");
        }

        // TODO: 实现识别任务提交
        String taskId = "task_" + System.currentTimeMillis();

        Map<String, Object> result = new HashMap<>();
        result.put("task_id", taskId);
        result.put("status", "processing");
        result.put("estimated_time", 30);
        result.put("progress", 0);

        return Result.success("识别任务已开始", result);
    }

    /**
     * 查询识别进度
     */
    @GetMapping("/progress/{task_id}")
    public Result<Map<String, Object>> getRecognitionProgress(
            @PathVariable("task_id") String taskId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 实现识别状态查询
        Map<String, Object> result = new HashMap<>();
        result.put("task_id", taskId);
        result.put("status", "completed");
        result.put("progress", 100);

        Map<String, Object> recognitionResult = new HashMap<>();
        recognitionResult.put("recognition_id", "rec_" + System.currentTimeMillis());
        recognitionResult.put("original_text", "");
        recognitionResult.put("modern_text", "");
        recognitionResult.put("confidence", 0.0);
        recognitionResult.put("word_count", 0);
        recognitionResult.put("dynasty", "");
        recognitionResult.put("period", "");
        recognitionResult.put("location", "");
        recognitionResult.put("person", "");
        recognitionResult.put("estimated_year", "");
        recognitionResult.put("processing_time", 0);

        result.put("result", recognitionResult);

        return Result.success(result);
    }

    /**
     * 获取识别历史记录
     */
    @GetMapping("/history")
    public Result<Map<String, Object>> getRecognitionHistory(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer per_page,
            @RequestParam(required = false) String dynasty,
            @RequestParam(required = false) String sort) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // 转换为后端分页格式（从1开始转为从0开始）
        int pageIndex = page > 0 ? page - 1 : 0;
        String sortParam = sort != null ? sort : "date_desc";

        // 调用服务层获取列表
        com.beishuo.common.PageResult<Map<String, Object>> pageResult = 
                inscriptionService.getMyInscriptions(userId, pageIndex, per_page, sortParam, null, null);

        // 转换为前端期望的格式
        List<Map<String, Object>> recognitionList = pageResult.getList();
        for (Map<String, Object> item : recognitionList) {
            // 转换字段名
            item.put("id", item.get("id"));
            item.put("title", item.get("title"));
            item.put("image_url", item.get("imageUrl"));
            item.put("original_text", item.get("text"));
            item.put("confidence", item.get("confidence") != null ? item.get("confidence") : 0.0);
            item.put("dynasty", item.get("dynasty"));
            item.put("created_at", item.get("createdAt"));
            item.put("is_favorited", item.get("isFavorited") != null ? item.get("isFavorited") : false);
            item.put("tags", item.get("tags") != null ? item.get("tags") : new java.util.ArrayList<>());
        }

        Map<String, Object> pagination = new HashMap<>();
        pagination.put("current_page", page);
        pagination.put("total_pages", pageResult.getTotalPages());
        pagination.put("total_count", pageResult.getTotal().intValue());
        pagination.put("per_page", per_page);

        Map<String, Object> result = new HashMap<>();
        result.put("recognition_list", recognitionList);
        result.put("pagination", pagination);

        return Result.success(result);
    }

    /**
     * 更新识别结果（校对）
     */
    @PutMapping("/{recognition_id}/correct")
    public Result<Map<String, Object>> correctRecognition(
            @PathVariable("recognition_id") String recognitionId,
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        String correctedText = (String) request.get("corrected_text");
        List<Map<String, Object>> corrections = (List<Map<String, Object>>) request.get("corrections");
        String notes = (String) request.get("notes");

        // TODO: 实现校对结果保存
        try {
            Long id = Long.parseLong(recognitionId.replace("rec_", ""));
            Map<String, Object> updateData = new HashMap<>();
            updateData.put("correctedText", correctedText);
            inscriptionService.updateInscription(id, userId, updateData);

            Map<String, Object> result = new HashMap<>();
            result.put("recognition_id", recognitionId);
            result.put("version", 2);
            result.put("correction_count", corrections != null ? corrections.size() : 0);

            return Result.success("校对结果已保存", result);
        } catch (NumberFormatException e) {
            return Result.error(ResultCode.BAD_REQUEST, "无效的识别ID");
        }
    }

    /**
     * 从Token中获取用户ID
     */
    private Long getUserIdFromToken(String authHeader) {
        if (authHeader == null) {
            return null;
        }
        String token = jwtUtil.extractTokenFromHeader(authHeader);
        if (token == null || !jwtUtil.validateToken(token)) {
            return null;
        }
        return jwtUtil.getUserIdFromToken(token);
    }
}

