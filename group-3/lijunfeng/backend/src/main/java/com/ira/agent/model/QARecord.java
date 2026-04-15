package com.ira.agent.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * 问答记录实体（对齐文档 10）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QARecord {

    /** 主键 rec_{timestamp} */
    private String id;

    @JsonProperty("session_id")
    private String sessionId;

    /** 用户提问，1-500 字符 */
    private String query;

    /** AI 回答 */
    private String answer;

    @JsonProperty("llm_used")
    private boolean llmUsed;

    /** 模型名称 */
    private String model;

    @JsonProperty("response_time_ms")
    private long responseTimeMs;

    @JsonProperty("answer_source")
    private String answerSource;

    @JsonProperty("created_at")
    private Instant createdAt;
}
