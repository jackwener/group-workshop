package com.ira.agent.provider;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * LLM 提供商统一返回结果
 */
@Data
@AllArgsConstructor
public class LlmResult {
    private String answer;
    private String answerSource;  // copaw / bailian / demo
    private boolean llmUsed;
    private String model;
}
