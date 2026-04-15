package com.ira.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AskResponse {
    private String answer;

    @JsonProperty("llm_used")
    private boolean llmUsed;

    private String model;

    @JsonProperty("response_time_ms")
    private long responseTimeMs;

    @JsonProperty("answer_source")
    private String answerSource;

    @JsonProperty("record_id")
    private String recordId;

    private String traceId;
}
