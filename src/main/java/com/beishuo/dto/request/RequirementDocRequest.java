package com.beishuo.dto.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class RequirementDocRequest {
    @NotBlank(message = "appUuid不能为空")
    private String appUuid;

    @NotBlank(message = "pageUuid不能为空")
    private String pageUuid;

    private String content;
}

