package com.beishuo.controller;

import com.beishuo.common.JwtUtil;
import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import com.beishuo.service.InscriptionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/upload")
public class UploadController {

    private static final Logger logger = LoggerFactory.getLogger(UploadController.class);

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private InscriptionService inscriptionService;

    /**
     * 上传图片
     */
    @PostMapping("/image")
    public Result<Map<String, Object>> uploadImage(
            @RequestParam("image") MultipartFile file,
            @RequestParam(value = "filename", required = false) String filename,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Long userId = getUserIdFromToken(authHeader);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }

        Map<String, Object> uploadResult = inscriptionService.uploadImage(file);
        
        // 转换为前端期望的格式
        Map<String, Object> result = new HashMap<>();
        result.put("image_id", uploadResult.get("imageId") != null ? 
                uploadResult.get("imageId").toString() : "img_" + System.currentTimeMillis());
        result.put("image_url", uploadResult.get("imageUrl"));
        
        // 图片尺寸信息（需要从服务层获取或解析）
        Map<String, Integer> imageSize = new HashMap<>();
        imageSize.put("width", 0);
        imageSize.put("height", 0);
        result.put("image_size", imageSize);
        
        result.put("file_size", file.getSize());
        result.put("upload_time", java.time.Instant.now()
                .atZone(java.time.ZoneId.of("UTC"))
                .format(java.time.format.DateTimeFormatter.ISO_INSTANT));

        return Result.success("图片上传成功", result);
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

