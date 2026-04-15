package com.ira.agent.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@AllArgsConstructor
public class ErrorResponse {
    private ErrorBody error;

    @Data
    @Builder
    @AllArgsConstructor
    public static class ErrorBody {
        private String code;
        private String message;
        private String traceId;
    }
}
