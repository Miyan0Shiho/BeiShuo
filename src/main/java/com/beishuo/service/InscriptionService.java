package com.beishuo.service;

import com.beishuo.client.DatabaseClient;
import com.beishuo.client.OSSClient;
import com.beishuo.client.RedisClient;
import com.beishuo.common.PageResult;
import com.beishuo.common.ResultCode;
import com.beishuo.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

@Service
public class InscriptionService {

    private static final Logger logger = LoggerFactory.getLogger(InscriptionService.class);

    @Autowired
    private DatabaseClient databaseClient;

    @Autowired
    private RedisClient redisClient;

    @Autowired
    private OSSClient ossClient;

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.upload.max-size:10485760}")
    private Long maxFileSize;

    @Value("${file.upload.allowed-types:jpg,jpeg,png,webp}")
    private String allowedTypes;

    @Value("${file.upload.url-prefix:/uploads}")
    private String urlPrefix;

    @Value("${cache.inscription-list-ttl:300}")
    private Long inscriptionListTtl;

    @Value("${cache.search-result-ttl:600}")
    private Long searchResultTtl;

    /**
     * 上传碑文图片
     */
    public Map<String, Object> uploadImage(MultipartFile file) {
        // 验证文件
        validateFile(file);

        try {
            // 生成文件名
            String originalFilename = file.getOriginalFilename();
            String extension = getFileExtension(originalFilename);
            String filename = UUID.randomUUID().toString() + "." + extension;

            // 确保上传目录存在
            Path uploadDir = Paths.get(uploadPath);
            if (!Files.exists(uploadDir)) {
                Files.createDirectories(uploadDir);
            }

            // 保存文件
            Path filePath = uploadDir.resolve(filename);
            file.transferTo(filePath.toFile());

            // 生成访问URL
            String imageUrl = urlPrefix + "/" + filename;
            
            // 上传到OSS
            String ossUrl = "";
            try {
                ossUrl = ossClient.uploadFile(filePath.toFile(), filename);
                logger.info("文件上传到OSS成功: filename={}, ossUrl={}", originalFilename, ossUrl);
            } catch (Exception e) {
                logger.warn("文件上传到OSS失败，继续使用本地存储: filename={}", originalFilename, e);
            }

            // 生成图片哈希值
            String imageHash = generateImageHash(file.getInputStream());

            Map<String, Object> result = new HashMap<>();
            result.put("imageUrl", imageUrl);
            result.put("ossUrl", ossUrl);
            result.put("imageId", filename);
            result.put("filename", originalFilename);
            result.put("imageHash", imageHash);

            logger.info("文件上传成功: filename={}, imageUrl={}, imageHash={}", originalFilename, imageUrl, imageHash);
            return result;
        } catch (IOException e) {
            logger.error("文件上传失败", e);
            throw new BusinessException(ResultCode.FILE_UPLOAD_FAILED);
        }
    }

    /**
     * 生成图片哈希值，用于OCR识别结果缓存
     */
    private String generateImageHash(InputStream inputStream) throws IOException {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                md.update(buffer, 0, bytesRead);
            }
            byte[] hashBytes = md.digest();
            BigInteger bigInt = new BigInteger(1, hashBytes);
            String hash = bigInt.toString(16);
            // 手动实现padStart功能
            int length = hash.length();
            if (length < 32) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 32 - length; i++) {
                    sb.append('0');
                }
                sb.append(hash);
                hash = sb.toString();
            }
            return hash;
        } catch (NoSuchAlgorithmException e) {
            logger.error("生成图片哈希值失败", e);
            throw new RuntimeException("生成图片哈希值失败", e);
        } finally {
            inputStream.close();
        }
    }
    
    /**
     * 生成图片哈希值，用于OCR识别结果缓存
     */
    private String generateImageHash(String imageUrl) {
        // 从URL生成哈希值，实际项目中应该下载图片计算哈希值
        // 这里简化处理，直接对URL进行哈希
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hashBytes = md.digest(imageUrl.getBytes());
            BigInteger bigInt = new BigInteger(1, hashBytes);
            String hash = bigInt.toString(16);
            // 手动实现padStart功能
            int length = hash.length();
            if (length < 32) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 32 - length; i++) {
                    sb.append('0');
                }
                sb.append(hash);
                hash = sb.toString();
            }
            return hash;
        } catch (NoSuchAlgorithmException e) {
            logger.error("生成图片哈希值失败", e);
            throw new RuntimeException("生成图片哈希值失败", e);
        }
    }

    /**
     * 提交识别任务
     */
    public String submitRecognitionTask(String imageId, String imageUrl) {
        // 生成图片哈希值
        String imageHash = generateImageHash(imageUrl);
        
        // 查询数据库，检查是否已有识别结果
        Map<String, Object> existingResult = databaseClient.getOCRResultByImageHash(imageHash);
        if (existingResult != null) {
            // 已有结果，直接使用
            logger.info("缓存命中: imageId={}, imageHash={}", imageId, imageHash);
            System.out.println("缓存命中");
            // TODO: 使用已有结果创建inscription记录
            return existingResult.get("task_id").toString();
        }
        
        // 无已有结果，提交OCR任务
        logger.info("缓存未命中: imageId={}, imageHash={}", imageId, imageHash);
        System.out.println("缓存未命中");
        
        String taskId = UUID.randomUUID().toString();
        
        // 创建OCR任务记录
        Map<String, Object> ocrJob = new HashMap<>();
        ocrJob.put("task_id", taskId);
        ocrJob.put("image_id", imageId);
        ocrJob.put("image_url", imageUrl);
        ocrJob.put("image_hash", imageHash);
        ocrJob.put("status", "pending");
        databaseClient.createOCRJob(ocrJob);
        
        // TODO: 实现OCR服务调用
        
        logger.info("提交识别任务: imageId={}, taskId={}", imageId, taskId);
        return taskId;
    }

    /**
     * 获取识别状态
     */
    public Map<String, Object> getRecognitionStatus(String taskId) {
        // 从数据库获取OCR任务状态
        // TODO: 实现databaseClient.getOCRJobStatus方法
        // Map<String, Object> ocrJob = databaseClient.getOCRJobStatus(taskId);
        // if (ocrJob != null) {
        //     return ocrJob;
        // }
        
        // 暂时返回模拟数据，待databaseClient实现getOCRJobStatus方法后替换
        Map<String, Object> status = new HashMap<>();
        status.put("status", "processing");
        status.put("progress", 50);
        status.put("message", "正在识别中...");
        return status;
    }

    /**
     * 获取识别结果
     */
    public Map<String, Object> getRecognitionResult(Long id) {
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }
        return inscription;
    }

    /**
     * 保存校对结果
     */
    public void saveProofread(Long id, String correctedText, List<Map<String, Object>> columns) {
        Map<String, Object> updateData = new HashMap<>();
        updateData.put("correctedText", correctedText);
        updateData.put("columns", columns);
        updateData.put("status", "proofread");

        databaseClient.updateInscription(id, updateData);

        // 清除相关缓存
        clearInscriptionCache(id);

        logger.info("校对结果保存成功: id={}", id);
    }

    /**
     * 重新识别
     */
    public String reRecognize(Long id) {
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }

        String imageUrl = (String) inscription.get("imageUrl");
        return submitRecognitionTask(String.valueOf(id), imageUrl);
    }

    /**
     * 获取我的碑文列表
     */
    public PageResult<Map<String, Object>> getMyInscriptions(Long userId, Integer page, Integer size, String sort, String keyword, String tab) {
        // 构建缓存key
        String cacheKey = String.format("inscription:list:%d:%d:%d:%s:%s:%s", userId, page, size, sort, keyword, tab);

        // 先查缓存
        PageResult<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<PageResult<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // 查询数据库
        Map<String, Object> dbResult = databaseClient.getInscriptionList(userId, page, size, sort, keyword);
        if (dbResult == null) {
            return PageResult.of(Collections.emptyList(), 0L, page, size);
        }

        // 转换为PageResult
        List<Map<String, Object>> list = (List<Map<String, Object>>) dbResult.get("list");
        Long total = dbResult.get("total") != null ? ((Number) dbResult.get("total")).longValue() : 0L;
        PageResult<Map<String, Object>> result = PageResult.of(list != null ? list : Collections.emptyList(), total, page, size);

        // 写入缓存
        redisClient.set(cacheKey, result, inscriptionListTtl);

        return result;
    }

    /**
     * 获取碑文详情
     */
    public Map<String, Object> getInscriptionDetail(Long id) {
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }
        return inscription;
    }

    /**
     * 更新碑文
     */
    public void updateInscription(Long id, Long userId, Map<String, Object> updateData) {
        // 验证权限
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }

        Long ownerId = inscription.get("userId") != null ? ((Number) inscription.get("userId")).longValue() : null;
        if (ownerId == null || !ownerId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权限修改此碑文");
        }

        databaseClient.updateInscription(id, updateData);

        // 清除相关缓存
        clearInscriptionCache(id);

        logger.info("碑文更新成功: id={}", id);
    }

    /**
     * 删除碑文
     */
    public void deleteInscription(Long id, Long userId) {
        // 验证权限
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }

        Long ownerId = inscription.get("userId") != null ? ((Number) inscription.get("userId")).longValue() : null;
        if (ownerId == null || !ownerId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权限删除此碑文");
        }

        databaseClient.deleteInscription(id);

        // 清除相关缓存
        clearInscriptionCache(id);

        logger.info("碑文删除成功: id={}", id);
    }

    /**
     * 收藏碑文
     */
    public void favoriteInscription(Long id, Long userId) {
        databaseClient.addFavorite(userId, "inscription", id);
        logger.info("收藏碑文成功: userId={}, inscriptionId={}", userId, id);
    }

    /**
     * 取消收藏
     */
    public void unfavoriteInscription(Long id, Long userId) {
        databaseClient.removeFavorite(userId, "inscription", id);
        logger.info("取消收藏成功: userId={}, inscriptionId={}", userId, id);
    }

    /**
     * 发布到知识库
     */
    public Long publishToKnowledge(Long id, Long userId) {
        // 验证权限
        Map<String, Object> inscription = databaseClient.getInscriptionById(id);
        if (inscription == null) {
            throw new BusinessException(ResultCode.INSCRIPTION_NOT_FOUND);
        }

        Long ownerId = inscription.get("userId") != null ? ((Number) inscription.get("userId")).longValue() : null;
        if (ownerId == null || !ownerId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权限发布此碑文");
        }

        // TODO: 调用数据库API发布到知识库
        // Map<String, Object> knowledgeData = new HashMap<>();
        // knowledgeData.put("title", inscription.get("title"));
        // knowledgeData.put("content", inscription.get("correctedText"));
        // knowledgeData.put("dynasty", inscription.get("dynasty"));
        // knowledgeData.put("sourceId", id);
        // Map<String, Object> knowledge = databaseClient.createKnowledge(knowledgeData);
        // Long knowledgeId = knowledge.get("id") != null ? ((Number) knowledge.get("id")).longValue() : null;

        // 返回知识库ID（当前返回null，需要实现）
        logger.info("发布到知识库: inscriptionId={}", id);
        return null;
    }

    /**
     * 搜索碑文
     */
    public List<Map<String, Object>> searchInscriptions(String keyword, Integer page, Integer size) {
        // 构建缓存key
        String cacheKey = String.format("inscription:search:%s:%d:%d", keyword, page, size);

        // 先查缓存
        List<Map<String, Object>> cached = redisClient.get(cacheKey, new ParameterizedTypeReference<List<Map<String, Object>>>() {});
        if (cached != null) {
            return cached;
        }

        // 查询数据库
        List<Map<String, Object>> results = databaseClient.searchInscriptions(keyword);
        if (results == null) {
            results = Collections.emptyList();
        }

        // 写入缓存
        redisClient.set(cacheKey, results, searchResultTtl);

        return results;
    }

    /**
     * 验证文件
     */
    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ResultCode.BAD_REQUEST, "文件不能为空");
        }

        if (file.getSize() > maxFileSize) {
            throw new BusinessException(ResultCode.FILE_SIZE_EXCEEDED);
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null) {
            throw new BusinessException(ResultCode.FILE_UPLOAD_FAILED, "文件名不能为空");
        }

        String extension = getFileExtension(originalFilename).toLowerCase();
        List<String> allowedTypesList = Arrays.asList(allowedTypes.split(","));
        if (!allowedTypesList.contains(extension)) {
            throw new BusinessException(ResultCode.FILE_TYPE_NOT_ALLOWED);
        }
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == filename.length() - 1) {
            return "";
        }
        return filename.substring(lastDotIndex + 1);
    }

    /**
     * 清除碑文相关缓存
     */
    private void clearInscriptionCache(Long id) {
        // 清除列表缓存（使用模糊搜索）
        try {
            List<String> keys = redisClient.searchKeys("inscription:list:*");
            if (keys != null) {
                keys.forEach(redisClient::delete);
            }
        } catch (Exception e) {
            logger.warn("清除列表缓存失败", e);
        }

        // 清除搜索缓存
        try {
            List<String> keys = redisClient.searchKeys("inscription:search:*");
            if (keys != null) {
                keys.forEach(redisClient::delete);
            }
        } catch (Exception e) {
            logger.warn("清除搜索缓存失败", e);
        }
    }
}

