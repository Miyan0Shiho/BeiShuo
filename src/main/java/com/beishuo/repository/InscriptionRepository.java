package com.beishuo.repository;

import com.beishuo.entity.Inscription;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

/**
 * 碑文数据访问接口
 */
public interface InscriptionRepository extends JpaRepository<Inscription, Long> {
    
    /**
     * 根据状态查询碑文列表
     */
    Page<Inscription> findByStatus(String status, Pageable pageable);
    
    /**
     * 根据创建者查询碑文列表
     */
    Page<Inscription> findByCreatedBy_Id(Long userId, Pageable pageable);
    
    /**
     * 搜索碑文（标题、内容、朝代、地点）
     */
    @Query("SELECT i FROM Inscription i WHERE i.title LIKE %:keyword% OR i.content LIKE %:keyword% OR i.dynasty LIKE %:keyword% OR i.location LIKE %:keyword%")
    List<Inscription> searchByKeyword(String keyword);
}
