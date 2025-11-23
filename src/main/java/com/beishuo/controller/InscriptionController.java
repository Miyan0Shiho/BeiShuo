package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
import com.beishuo.common.PageResult;
import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import com.beishuo.service.InscriptionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/inscription")
public class InscriptionController {

    private static final Logger logger = LoggerFactory.getLogger(InscriptionController.class);

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private InscriptionService inscriptionService;

    /**
     * 上传碑文图片
     */
    @PostMapping("/upload")
    public Result<Map<String, Object>> uploadImage(@RequestParam("file") MultipartFile file) {
        Map<String, Object> result = inscriptionService.uploadImage(file);
        return Result.success(result);
    }

    /**
     * 提交识别任务
     */
    @PostMapping("/recognize")
    public Result<Map<String, Object>> recognize(@RequestBody Map<String, Object> request) {
        // TODO: 实现识别任务提交
        // String taskId = inscriptionService.submitRecognitionTask(imageId, imageUrl);
        // Map<String, Object> result = new HashMap<>();
        // result.put("taskId", taskId);
        // return Result.success(result);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "识别功能待实现");
    }

    /**
     * 查询识别状态
     */
    @GetMapping("/status/{taskId}")
    public Result<Map<String, Object>> getRecognitionStatus(@PathVariable String taskId) {
        // TODO: 实现识别状态查询
        // Map<String, Object> status = inscriptionService.getRecognitionStatus(taskId);
        // return Result.success(status);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "状态查询功能待实现");
    }

    /**
     * 获取识别结果
     */
    @GetMapping("/{id}/result")
    public Result<Map<String, Object>> getRecognitionResult(@PathVariable Long id) {
        // TODO: 实现识别结果获取
        // Map<String, Object> result = inscriptionService.getRecognitionResult(id);
        // return Result.success(result);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "结果获取功能待实现");
    }

    /**
     * 保存校对结果
     */
    @PutMapping("/{id}/save-proofread")
    public Result<?> saveProofread(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        // TODO: 实现校对结果保存
        // inscriptionService.saveProofread(id, correctedText, columns);
        // return Result.success();

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "保存功能待实现");
    }

    /**
     * 重新识别
     */
    @PostMapping("/{id}/re-recognize")
    public Result<Map<String, Object>> reRecognize(@PathVariable Long id) {
        // TODO: 实现重新识别
        // String taskId = inscriptionService.reRecognize(id);
        // Map<String, Object> result = new HashMap<>();
        // result.put("taskId", taskId);
        // return Result.success(result);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "重新识别功能待实现");
    }

    /**
     * 获取我的碑文列表
     */
    @GetMapping("/list")
    public Result<PageResult<Map<String, Object>>> getMyInscriptions(
            @RequestHeader(value = "Authorization", required = false) String authHeader,
            @RequestParam(defaultValue = "0") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String sort,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String tab) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        PageResult<Map<String, Object>> result = inscriptionService.getMyInscriptions(
                userId, page, size, sort, keyword, tab);
        return Result.success(result);
    }

    /**
     * 获取碑文详情
     */
    @GetMapping("/{id}")
    public Result<Map<String, Object>> getInscriptionDetail(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Map<String, Object> detail = inscriptionService.getInscriptionDetail(id);
        return Result.success(detail);
    }

    /**
     * 更新碑文
     */
    @PutMapping("/{id}")
    public Result<?> updateInscription(
            @PathVariable Long id,
            @RequestBody Map<String, Object> request,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        inscriptionService.updateInscription(id, userId, request);
        return Result.success();
    }

    /**
     * 删除碑文
     */
    @DeleteMapping("/{id}")
    public Result<?> deleteInscription(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        inscriptionService.deleteInscription(id, userId);
        return Result.success();
    }

    /**
     * 收藏碑文
     */
    @PostMapping("/{id}/favorite")
    public Result<?> favoriteInscription(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用InscriptionService收藏碑文
        // inscriptionService.favoriteInscription(id, userId);
        // return Result.success();

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "收藏功能待实现");
    }

    /**
     * 取消收藏
     */
    @DeleteMapping("/{id}/favorite")
    public Result<?> unfavoriteInscription(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用InscriptionService取消收藏
        // inscriptionService.unfavoriteInscription(id, userId);
        // return Result.success();

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "取消收藏功能待实现");
    }

    /**
     * 发布到知识库
     */
    @PostMapping("/{id}/publish")
    public Result<Map<String, Object>> publishToKnowledge(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        // TODO: 调用InscriptionService发布到知识库
        // Long knowledgeId = inscriptionService.publishToKnowledge(id, userId);
        // Map<String, Object> result = new HashMap<>();
        // result.put("knowledgeId", knowledgeId);
        // return Result.success(result);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "发布功能待实现");
    }

    /**
     * 搜索碑文
     */
    @GetMapping("/search")
    public Result<List<Map<String, Object>>> searchInscriptions(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {

        List<Map<String, Object>> results = inscriptionService.searchInscriptions(keyword, page, size);
        return Result.success(results);
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

