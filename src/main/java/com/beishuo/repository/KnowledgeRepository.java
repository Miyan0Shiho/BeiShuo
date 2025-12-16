package com.beishuo.repository;

import com.beishuo.entity.Knowledge;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

/**
 * 知识库数据访问接口
 */
public interface KnowledgeRepository extends JpaRepository<Knowledge, Long> {
    
    /**
     * 根据分类查询知识库
     */
    Page<Knowledge> findByCategory(String category, Pageable pageable);
    
    /**
     * 根据朝代查询知识库
     */
    Page<Knowledge> findByDynasty(String dynasty, Pageable pageable);
    
    /**
     * 搜索知识库（标题、内容）
     */
    @Query("SELECT k FROM Knowledge k WHERE k.title LIKE %:keyword% OR k.content LIKE %:keyword%")
    List<Knowledge> searchByKeyword(String keyword);
    
    /**
     * 根据标签搜索知识库
     */
    @Query("SELECT k FROM Knowledge k WHERE k.tags LIKE %:tag%")
    List<Knowledge> searchByTag(String tag);
}
