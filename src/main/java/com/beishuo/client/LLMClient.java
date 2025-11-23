package com.beishuo.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class LLMClient {

    private static final Logger logger = LoggerFactory.getLogger(LLMClient.class);

    @Value("${llm.api.base-url}")
    private String baseUrl;

    @Value("${llm.api.api-key}")
    private String apiKey;

    @Value("${llm.api.model:gpt-4}")
    private String model;

    @Value("${llm.api.temperature:0.7}")
    private Double temperature;

    @Value("${llm.api.max-tokens:2000}")
    private Integer maxTokens;

    @Value("${llm.api.timeout:30000}")
    private Integer timeout;

    private final RestTemplate restTemplate;

    public LLMClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * 生成AI阐释
     */
    public String generateInterpretation(String text, String dynasty, String context) {
        String url = baseUrl + "/chat/completions";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", model);

        List<Map<String, String>> messages = new ArrayList<>();

        // 系统提示词
        Map<String, String> systemMsg = new HashMap<>();
        systemMsg.put("role", "system");
        systemMsg.put("content", "你是一位专业的碑文研究专家，擅长解读古代碑文的历史背景和文化意义。");
        messages.add(systemMsg);

        // 用户消息
        Map<String, String> userMsg = new HashMap<>();
        userMsg.put("role", "user");
        StringBuilder content = new StringBuilder();
        content.append("请为以下").append(dynasty != null ? dynasty : "古代").append("时期的碑文内容提供详细的历史文化阐释：\n\n");
        content.append("碑文内容：").append(text).append("\n\n");
        if (context != null && !context.isEmpty()) {
            content.append("上下文：").append(context);
        }
        userMsg.put("content", content.toString());
        messages.add(userMsg);

        requestBody.put("messages", messages);
        requestBody.put("temperature", temperature);
        requestBody.put("max_tokens", maxTokens);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody != null && responseBody.containsKey("choices")) {
                List<Map<String, Object>> choices = (List<Map<String, Object>>) responseBody.get("choices");
                if (choices != null && !choices.isEmpty()) {
                    Map<String, Object> firstChoice = choices.get(0);
                    Map<String, String> message = (Map<String, String>) firstChoice.get("message");
                    if (message != null) {
                        return message.get("content");
                    }
                }
            }
            logger.error("LLM API响应格式异常");
            throw new RuntimeException("AI阐释生成失败：响应格式异常");
        } catch (Exception e) {
            logger.error("调用LLM API失败", e);
            throw new RuntimeException("AI阐释生成失败", e);
        }
    }

    /**
     * AI对话（用于RAG系统）
     */
    public String chat(String question, List<String> context) {
        String url = baseUrl + "/chat/completions";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", model);

        List<Map<String, String>> messages = new ArrayList<>();

        // 添加上下文
        if (context != null && !context.isEmpty()) {
            Map<String, String> contextMsg = new HashMap<>();
            contextMsg.put("role", "system");
            contextMsg.put("content", "相关背景知识：\n" + String.join("\n", context));
            messages.add(contextMsg);
        }

        // 用户问题
        Map<String, String> userMsg = new HashMap<>();
        userMsg.put("role", "user");
        userMsg.put("content", question);
        messages.add(userMsg);

        requestBody.put("messages", messages);
        requestBody.put("temperature", temperature);
        requestBody.put("max_tokens", maxTokens);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody != null && responseBody.containsKey("choices")) {
                List<Map<String, Object>> choices = (List<Map<String, Object>>) responseBody.get("choices");
                if (choices != null && !choices.isEmpty()) {
                    Map<String, Object> firstChoice = choices.get(0);
                    Map<String, String> message = (Map<String, String>) firstChoice.get("message");
                    if (message != null) {
                        return message.get("content");
                    }
                }
            }
            logger.error("LLM API响应格式异常");
            throw new RuntimeException("AI对话失败：响应格式异常");
        } catch (Exception e) {
            logger.error("调用LLM API失败", e);
            throw new RuntimeException("AI对话失败", e);
        }
    }
}

