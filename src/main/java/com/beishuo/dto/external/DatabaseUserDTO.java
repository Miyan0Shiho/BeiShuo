package com.beishuo.dto.external;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class DatabaseUserDTO {
    private Long id;
    private String username;
    private String email;
    private String password;
    private String phone;
    private String avatar;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}

