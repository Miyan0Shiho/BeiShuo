package com.beishuo.repository;

import com.beishuo.entity.OCRResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

/**
 * OCR结果数据访问接口
 */
public interface OCRResultRepository extends JpaRepository<OCRResult, Long> {
    
    /**
     * 根据图片哈希值查询OCR结果
     * @param imageHash 图片哈希值
     * @return OCR结果列表
     */
    @Query(value = "SELECT * FROM ocr_jobs WHERE CAST(params AS text) LIKE CONCAT('%', ?1, '%') AND status = 'completed'", nativeQuery = true)
    List<OCRResult> findByParamsContainingImageHash(String imageHash);
}

