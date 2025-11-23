package com.beishuo.dto.request;

import lombok.Data;

import javax.validation.constraints.Size;
import java.util.List;
import java.util.Map;

@Data
public class InscriptionUpdateRequest {
    @Size(max = 100, message = "标题长度不能超过100个字符")
    private String title;

    private String dynasty;

    private List<String> tags;

    @Size(max = 1000, message = "描述长度不能超过1000个字符")
    private String description;

    private String correctedText;

    private List<Map<String, Object>> columns;

    private String status;
}

