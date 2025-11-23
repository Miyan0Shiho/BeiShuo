package com.beishuo.dto.response;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class InterpretationVO {
    private Long id;
    private Long inscriptionId;
    private String interpretation;
    private String translation;
    private String history;
    private String culture;
    private String figures;
    private String reading;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}

