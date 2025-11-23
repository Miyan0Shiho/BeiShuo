package com.beishuo.controller;

import com.beishuo.common.Result;
import com.beishuo.common.ResultCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/requirement-doc")
public class RequirementDocController {

    private static final Logger logger = LoggerFactory.getLogger(RequirementDocController.class);

    // TODO: 注入RequirementDocService
    // @Autowired
    // private RequirementDocService requirementDocService;

    /**
     * 获取需求文档
     */
    @GetMapping
    public Result<Map<String, Object>> getRequirementDoc(
            @RequestParam String appUuid,
            @RequestParam String pageUuid) {

        // TODO: 调用RequirementDocService获取文档
        // String content = requirementDocService.getRequirementDoc(appUuid, pageUuid);
        // Map<String, Object> result = new HashMap<>();
        // result.put("content", content);
        // return Result.success(result);

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "文档获取功能待实现");
    }

    /**
     * 保存需求文档
     */
    @PutMapping
    public Result<?> saveRequirementDoc(@RequestBody Map<String, Object> request) {
        String appUuid = (String) request.get("appUuid");
        String pageUuid = (String) request.get("pageUuid");
        String content = (String) request.get("content");

        if (appUuid == null || pageUuid == null) {
            return Result.error(ResultCode.BAD_REQUEST, "appUuid和pageUuid不能为空");
        }

        // TODO: 调用RequirementDocService保存文档
        // requirementDocService.saveRequirementDoc(appUuid, pageUuid, content);
        // return Result.success();

        return Result.error(ResultCode.INTERNAL_SERVER_ERROR, "文档保存功能待实现");
    }
}

