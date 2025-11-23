package com.beishuo.dto.request;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;

@Data
public class InscriptionCreateRequest {
    @NotBlank(message = "图片URL不能为空")
    private String imageUrl;

    private String imageId;

    private String title;

    private String dynasty;

    private List<String> tags;

    private String description;
}

