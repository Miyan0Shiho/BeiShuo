package com.beishuo.dto.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class InterpretationRequest {
    private Long inscriptionId;

    @NotBlank(message = "碑文内容不能为空")
    private String text;

    private String dynasty;

    private String context;
}

