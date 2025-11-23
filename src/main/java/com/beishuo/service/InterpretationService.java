package com.beishuo.service;

import com.beishuo.client.DatabaseClient;
import com.beishuo.client.LLMClient;
import com.beishuo.client.RedisClient;
import com.beishuo.common.ResultCode;
import com.beishuo.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class InterpretationService {

    private static final Logger logger = LoggerFactory.getLogger(InterpretationService.class);

    @Autowired
    private DatabaseClient databaseClient;

    @Autowired
    private LLMClient llmClient;

    @Autowired
    private RedisClient redisClient;

    @Value("${rag.api.base-url:http://localhost:8083/api/rag}")
    private String ragBaseUrl;

    @Value("${business.interpretation.max-context-length:5000}")
    private Integer maxContextLength;

    /**
     * 生成AI阐释
     */
    public Map<String, Object> generateInterpretation(Long inscriptionId, String text, String dynasty) {
        // 获取碑文详情作为上下文
        String context = "";
        if (inscriptionId != null) {
            Map<String, Object> inscription = databaseClient.getInscriptionById(inscriptionId);
            if (inscription != null) {
                StringBuilder contextBuilder = new StringBuilder();
                if (inscription.get("title") != null) {
                    contextBuilder.append("标题：").append(inscription.get("title")).append("\n");
                }
                if (inscription.get("dynasty") != null) {
                    contextBuilder.append("朝代：").append(inscription.get("dynasty")).append("\n");
                }
                if (inscription.get("tags") != null) {
                    contextBuilder.append("标签：").append(inscription.get("tags")).append("\n");
                }
                context = contextBuilder.toString();
            }
        }

        // 从RAG获取相关背景知识
        List<String> ragContext = getRagContext(inscriptionId, text);
        if (ragContext != null && !ragContext.isEmpty()) {
            context += "\n相关背景知识：\n" + String.join("\n", ragContext);
        }

        // 限制上下文长度
        if (context.length() > maxContextLength) {
            context = context.substring(0, maxContextLength) + "...";
        }

        // 调用LLM生成阐释
        String interpretation = llmClient.generateInterpretation(text, dynasty, context);

        // 构建返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("interpretation", interpretation);
        result.put("translation", ""); // TODO: 如果需要翻译，可以调用LLM生成
        result.put("history", ""); // TODO: 历史背景可以从阐释中提取或单独生成
        result.put("culture", ""); // TODO: 文化意义可以从阐释中提取或单独生成
        result.put("figures", ""); // TODO: 相关人物可以从阐释中提取或单独生成
        result.put("reading", ""); // TODO: 延伸阅读可以从阐释中提取或单独生成

        // 保存阐释结果到数据库
        if (inscriptionId != null) {
            saveInterpretation(inscriptionId, result);
        }

        logger.info("AI阐释生成成功: inscriptionId={}", inscriptionId);
        return result;
    }

    /**
     * AI对话
     */
    public String chat(Long inscriptionId, String question, List<String> context) {
        // 获取碑文上下文
        List<String> ragContext = getRagContext(inscriptionId, null);
        if (ragContext != null && !ragContext.isEmpty()) {
            if (context == null) {
                context = new ArrayList<>();
            }
            context.addAll(ragContext);
        }

        // 调用LLM进行对话
        String answer = llmClient.chat(question, context);

        logger.info("AI对话成功: inscriptionId={}, question={}", inscriptionId, question);
        return answer;
    }

    /**
     * 获取阐释详情
     */
    public Map<String, Object> getInterpretationDetail(Long id) {
        // TODO: 从数据库获取保存的阐释结果
        // Map<String, Object> interpretation = databaseClient.getInterpretationById(id);
        // if (interpretation == null) {
        //     throw new BusinessException(ResultCode.NOT_FOUND, "阐释不存在");
        // }
        // return interpretation;

        throw new BusinessException(ResultCode.INTERNAL_SERVER_ERROR, "阐释详情查询功能待实现");
    }

    /**
     * 从RAG获取相关背景知识
     */
    private List<String> getRagContext(Long inscriptionId, String text) {
        try {
            // TODO: 调用RAG API获取相关文档
            // 当前返回空列表，需要实现RAG客户端调用
            // String ragUrl = ragBaseUrl + "/retrieve";
            // Map<String, Object> request = new HashMap<>();
            // request.put("query", text != null ? text : "");
            // request.put("inscriptionId", inscriptionId);
            // request.put("topK", 5);
            //
            // // 调用RAG API
            // List<String> context = ragClient.retrieve(request);
            // return context;

            return Collections.emptyList();
        } catch (Exception e) {
            logger.warn("获取RAG上下文失败", e);
            return Collections.emptyList();
        }
    }

    /**
     * 保存阐释结果
     */
    private void saveInterpretation(Long inscriptionId, Map<String, Object> interpretation) {
        try {
            // TODO: 保存到数据库
            // Map<String, Object> data = new HashMap<>();
            // data.put("inscriptionId", inscriptionId);
            // data.put("content", interpretation.get("interpretation"));
            // data.put("translation", interpretation.get("translation"));
            // data.put("history", interpretation.get("history"));
            // data.put("culture", interpretation.get("culture"));
            // data.put("figures", interpretation.get("figures"));
            // data.put("reading", interpretation.get("reading"));
            // databaseClient.saveInterpretation(data);
        } catch (Exception e) {
            logger.warn("保存阐释结果失败", e);
        }
    }
}

