package com.ira.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class AskRequest {
    private String query;

    @JsonProperty("session_id")
    private String sessionId;
}
