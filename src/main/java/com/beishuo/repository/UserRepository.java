package com.beishuo.repository;

import com.beishuo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 用户数据访问接口
 */
public interface UserRepository extends JpaRepository<User, Long> {
    
    /**
     * 根据邮箱查询用户
     */
    User findByEmail(String email);
    
    /**
     * 根据用户名查询用户
     */
    User findByUsername(String username);
}
