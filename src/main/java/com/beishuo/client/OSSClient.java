package com.beishuo.client;

import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.aliyun.oss.model.PutObjectRequest;
import com.aliyun.oss.model.PutObjectResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.InputStream;
import java.net.URL;
import java.util.Date;

/**
 * OSS客户端工具类，用于封装阿里云OSS的操作
 */
@Component
public class OSSClient {

    private static final Logger logger = LoggerFactory.getLogger(OSSClient.class);

    @Value("${aliyun.oss.access-key-id}")
    private String accessKeyId;

    @Value("${aliyun.oss.access-key-secret}")
    private String accessKeySecret;

    @Value("${aliyun.oss.endpoint}")
    private String endpoint;

    @Value("${aliyun.oss.bucket-name}")
    private String bucketName;

    @Value("${aliyun.oss.domain}")
    private String domain;

    private OSS ossClient;

    /**
     * 获取OSS客户端实例
     */
    private OSS getOSSClient() {
        if (ossClient == null) {
            ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
        }
        return ossClient;
    }

    /**
     * 上传文件到OSS
     *
     * @param file     本地文件
     * @param objectName OSS对象名称
     * @return OSS文件URL
     */
    public String uploadFile(File file, String objectName) {
        try {
            // 创建PutObjectRequest对象
            PutObjectRequest putObjectRequest = new PutObjectRequest(bucketName, objectName, file);

            // 上传文件
            PutObjectResult result = getOSSClient().putObject(putObjectRequest);
            logger.info("文件上传OSS成功: bucket={}, objectName={}, etag={}", bucketName, objectName, result.getETag());

            // 生成URL
            return getFileUrl(objectName);
        } catch (Exception e) {
            logger.error("文件上传OSS失败: bucket={}, objectName={}", bucketName, objectName, e);
            throw new RuntimeException("文件上传OSS失败", e);
        }
    }

    /**
     * 上传输入流到OSS
     *
     * @param inputStream 输入流
     * @param objectName  OSS对象名称
     * @return OSS文件URL
     */
    public String uploadInputStream(InputStream inputStream, String objectName) {
        try {
            // 创建PutObjectRequest对象
            PutObjectRequest putObjectRequest = new PutObjectRequest(bucketName, objectName, inputStream);

            // 上传文件
            PutObjectResult result = getOSSClient().putObject(putObjectRequest);
            logger.info("输入流上传OSS成功: bucket={}, objectName={}, etag={}", bucketName, objectName, result.getETag());

            // 生成URL
            return getFileUrl(objectName);
        } catch (Exception e) {
            logger.error("输入流上传OSS失败: bucket={}, objectName={}", bucketName, objectName, e);
            throw new RuntimeException("输入流上传OSS失败", e);
        }
    }

    /**
     * 获取OSS文件URL
     *
     * @param objectName OSS对象名称
     * @return OSS文件URL
     */
    public String getFileUrl(String objectName) {
        try {
            // 设置URL过期时间为365天
            Date expiration = new Date(System.currentTimeMillis() + 365 * 24 * 60 * 60 * 1000L);
            
            // 生成URL
            URL url = getOSSClient().generatePresignedUrl(bucketName, objectName, expiration);
            
            // 如果配置了自定义域名，使用自定义域名
            if (domain != null && !domain.isEmpty()) {
                String urlStr = url.toString();
                String endpointHost = new URL(endpoint).getHost();
                return urlStr.replace(endpointHost, domain);
            }
            
            return url.toString();
        } catch (Exception e) {
            logger.error("获取OSS文件URL失败: bucket={}, objectName={}", bucketName, objectName, e);
            throw new RuntimeException("获取OSS文件URL失败", e);
        }
    }

    /**
     * 删除OSS文件
     *
     * @param objectName OSS对象名称
     */
    public void deleteFile(String objectName) {
        try {
            getOSSClient().deleteObject(bucketName, objectName);
            logger.info("删除OSS文件成功: bucket={}, objectName={}", bucketName, objectName);
        } catch (Exception e) {
            logger.error("删除OSS文件失败: bucket={}, objectName={}", bucketName, objectName, e);
            throw new RuntimeException("删除OSS文件失败", e);
        }
    }

    /**
     * 关闭OSS客户端
     */
    public void close() {
        if (ossClient != null) {
            ossClient.shutdown();
            ossClient = null;
        }
    }
}
