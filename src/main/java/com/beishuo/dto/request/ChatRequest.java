package com.beishuo.dto.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class ChatRequest {
    private Long inscriptionId;

    @NotBlank(message = "问题不能为空")
    private String question;

    private List<String> context;
}

