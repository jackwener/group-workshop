package com.ira.agent.controller;

import com.ira.agent.config.TraceIdFilter;
import com.ira.agent.dto.*;
import com.ira.agent.model.QARecord;
import com.ira.agent.model.Session;
import com.ira.agent.provider.LlmResult;
import com.ira.agent.service.AgentService;
import com.ira.agent.service.StorageService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Agent API Controller（对齐文档 09 — 6 个核心端点）
 * Base URL: /api/v1/agent
 */
@RestController
@RequestMapping("/api/v1/agent")
public class AgentController {

    private final AgentService agentService;
    private final StorageService storageService;

    public AgentController(AgentService agentService, StorageService storageService) {
        this.agentService = agentService;
        this.storageService = storageService;
    }

    // ========== 1. GET /capabilities — 能力探测 ==========

    @GetMapping("/capabilities")
    public ResponseEntity<Map<String, Object>> getCapabilities(HttpServletRequest request) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("traceId", getTraceId(request));
        body.put("providers", agentService.getCapabilities());
        return ResponseEntity.ok(body);
    }

    // ========== 2. POST /ask — 问答提交 ==========

    @PostMapping("/ask")
    public ResponseEntity<?> ask(@RequestBody AskRequest askRequest, HttpServletRequest request) {
        String traceId = getTraceId(request);
        String query = askRequest.getQuery();
        String sessionId = askRequest.getSessionId();

        // 参数校验
        if (query == null || query.isBlank()) {
            return badRequest("EMPTY_QUERY", "query 不能为空", traceId);
        }
        if (query.length() > 500) {
            return badRequest("INVALID_QUERY", "query 长度不能超过 500 字符", traceId);
        }
        if (sessionId == null || sessionId.isBlank()) {
            return badRequest("MISSING_SESSION_ID", "session_id 不能为空", traceId);
        }

        // 校验 session 存在
        Session session = storageService.getSession(sessionId);
        if (session == null) {
            return notFound("SESSION_NOT_FOUND", "会话不存在: " + sessionId, traceId);
        }

        // 执行问答
        long start = System.currentTimeMillis();
        LlmResult result = agentService.ask(query);
        long elapsed = System.currentTimeMillis() - start;

        // 持久化记录
        QARecord record = QARecord.builder()
                .sessionId(sessionId)
                .query(query)
                .answer(result.getAnswer())
                .llmUsed(result.isLlmUsed())
                .model(result.getModel())
                .responseTimeMs(elapsed)
                .answerSource(result.getAnswerSource())
                .build();
        record = storageService.addRecord(record);

        // 构建响应
        AskResponse response = AskResponse.builder()
                .answer(result.getAnswer())
                .llmUsed(result.isLlmUsed())
                .model(result.getModel())
                .responseTimeMs(elapsed)
                .answerSource(result.getAnswerSource())
                .recordId(record.getId())
                .traceId(traceId)
                .build();

        return ResponseEntity.ok(response);
    }

    // ========== 3. GET /sessions — 会话列表 ==========

    @GetMapping("/sessions")
    public ResponseEntity<Map<String, Object>> getSessions(HttpServletRequest request) {
        List<Session> sessions = storageService.getSessions();
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("traceId", getTraceId(request));
        body.put("sessions", sessions);
        body.put("total", sessions.size());
        return ResponseEntity.ok(body);
    }

    // ========== 4. POST /sessions — 新建会话 ==========

    @PostMapping("/sessions")
    public ResponseEntity<Map<String, Object>> createSession(
            @RequestBody(required = false) SessionRequest sessionRequest,
            HttpServletRequest request) {
        String title = (sessionRequest != null) ? sessionRequest.getTitle() : null;
        Session session = storageService.createSession(title);
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("traceId", getTraceId(request));
        body.put("session", session);
        return ResponseEntity.status(HttpStatus.CREATED).body(body);
    }

    // ========== 5. DELETE /sessions/{id} — 删除会话 ==========

    @DeleteMapping("/sessions/{id}")
    public ResponseEntity<?> deleteSession(@PathVariable String id, HttpServletRequest request) {
        String traceId = getTraceId(request);
        boolean deleted = storageService.deleteSession(id);
        if (!deleted) {
            return notFound("SESSION_NOT_FOUND", "会话不存在: " + id, traceId);
        }
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("traceId", traceId);
        body.put("deleted", true);
        return ResponseEntity.ok(body);
    }

    // ========== 6. GET /sessions/{id}/records — 问答记录 ==========

    @GetMapping("/sessions/{id}/records")
    public ResponseEntity<?> getRecords(@PathVariable String id, HttpServletRequest request) {
        String traceId = getTraceId(request);
        Session session = storageService.getSession(id);
        if (session == null) {
            return notFound("SESSION_NOT_FOUND", "会话不存在: " + id, traceId);
        }
        List<QARecord> records = storageService.getRecordsBySession(id);
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("traceId", traceId);
        body.put("records", records);
        body.put("total", records.size());
        return ResponseEntity.ok(body);
    }

    // ========== 辅助方法 ==========

    private String getTraceId(HttpServletRequest request) {
        Object traceId = request.getAttribute(TraceIdFilter.TRACE_ID_KEY);
        return traceId != null ? traceId.toString() : "unknown";
    }

    private ResponseEntity<ErrorResponse> badRequest(String code, String message, String traceId) {
        return ResponseEntity.badRequest().body(
                new ErrorResponse(new ErrorResponse.ErrorBody(code, message, traceId)));
    }

    private ResponseEntity<ErrorResponse> notFound(String code, String message, String traceId) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(
                new ErrorResponse(new ErrorResponse.ErrorBody(code, message, traceId)));
    }
}
