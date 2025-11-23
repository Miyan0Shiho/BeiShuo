package com.beishuo.dto.response;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class UserInfoResponse {
    private Long id;
    private String username;
    private String email;
    private String avatar;
    private String phone;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}

