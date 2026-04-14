package com.ira.agent.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * 会话实体（对齐文档 10）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Session {

    @JsonProperty("session_id")
    private String sessionId;

    /** 会话标题，≤23 字 */
    private String title;

    @JsonProperty("created_at")
    private Instant createdAt;

    @JsonProperty("updated_at")
    private Instant updatedAt;

    @JsonProperty("query_count")
    @Builder.Default
    private int queryCount = 0;
}
