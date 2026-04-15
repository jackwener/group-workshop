package com.ira.agent.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.ira.agent.model.QARecord;
import com.ira.agent.model.Session;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

/**
 * JSON 文件存储服务（对齐文档 10）
 * 数据文件：{dataDir}/sessions.json、{dataDir}/records.json
 */
@Service
public class StorageService {

    private static final Logger log = LoggerFactory.getLogger(StorageService.class);

    private final ObjectMapper mapper;
    private final String dataDir;

    private File sessionsFile;
    private File recordsFile;

    public StorageService(@Value("${app.data-dir:./data}") String dataDir) {
        this.dataDir = dataDir;
        this.mapper = new ObjectMapper();
        this.mapper.registerModule(new JavaTimeModule());
    }

    @PostConstruct
    public void init() throws IOException {
        File dir = new File(dataDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }
        sessionsFile = new File(dir, "sessions.json");
        recordsFile = new File(dir, "records.json");
        if (!sessionsFile.exists()) {
            mapper.writeValue(sessionsFile, new ArrayList<>());
        }
        if (!recordsFile.exists()) {
            mapper.writeValue(recordsFile, new ArrayList<>());
        }
        log.info("StorageService initialized, dataDir={}", dir.getAbsolutePath());
    }

    // ========== Session 操作 ==========

    public synchronized List<Session> getSessions() {
        try {
            return mapper.readValue(sessionsFile, new TypeReference<List<Session>>() {});
        } catch (IOException e) {
            log.error("Failed to read sessions", e);
            return new ArrayList<>();
        }
    }

    public synchronized Session createSession(String title) {
        List<Session> sessions = getSessions();
        Session session = Session.builder()
                .sessionId(UUID.randomUUID().toString())
                .title(title != null && !title.isBlank() ? title : "新会话")
                .createdAt(Instant.now())
                .updatedAt(Instant.now())
                .queryCount(0)
                .build();
        sessions.add(0, session);
        writeSessions(sessions);
        return session;
    }

    public synchronized Session getSession(String sessionId) {
        return getSessions().stream()
                .filter(s -> s.getSessionId().equals(sessionId))
                .findFirst()
                .orElse(null);
    }

    public synchronized boolean deleteSession(String sessionId) {
        List<Session> sessions = getSessions();
        boolean removed = sessions.removeIf(s -> s.getSessionId().equals(sessionId));
        if (removed) {
            writeSessions(sessions);
            // 级联删除问答记录
            deleteRecordsBySession(sessionId);
        }
        return removed;
    }

    public synchronized void updateSession(Session session) {
        List<Session> sessions = getSessions();
        for (int i = 0; i < sessions.size(); i++) {
            if (sessions.get(i).getSessionId().equals(session.getSessionId())) {
                session.setUpdatedAt(Instant.now());
                sessions.set(i, session);
                break;
            }
        }
        writeSessions(sessions);
    }

    // ========== QARecord 操作 ==========

    public synchronized List<QARecord> getAllRecords() {
        try {
            return mapper.readValue(recordsFile, new TypeReference<List<QARecord>>() {});
        } catch (IOException e) {
            log.error("Failed to read records", e);
            return new ArrayList<>();
        }
    }

    public synchronized List<QARecord> getRecordsBySession(String sessionId) {
        return getAllRecords().stream()
                .filter(r -> r.getSessionId().equals(sessionId))
                .collect(Collectors.toList());
    }

    public synchronized QARecord addRecord(QARecord record) {
        List<QARecord> records = getAllRecords();
        if (record.getId() == null) {
            record.setId("rec_" + System.currentTimeMillis());
        }
        if (record.getCreatedAt() == null) {
            record.setCreatedAt(Instant.now());
        }
        records.add(record);
        writeRecords(records);

        // 首次问答自动命名 + 更新 query_count
        Session session = getSession(record.getSessionId());
        if (session != null) {
            session.setQueryCount(session.getQueryCount() + 1);
            if (session.getQueryCount() == 1 && "新会话".equals(session.getTitle())) {
                String autoTitle = record.getQuery().length() > 20
                        ? record.getQuery().substring(0, 20) + "..."
                        : record.getQuery();
                session.setTitle(autoTitle);
            }
            updateSession(session);
        }
        return record;
    }

    public synchronized void deleteRecordsBySession(String sessionId) {
        List<QARecord> records = getAllRecords();
        records.removeIf(r -> r.getSessionId().equals(sessionId));
        writeRecords(records);
    }

    // ========== 私有方法 ==========

    private void writeSessions(List<Session> sessions) {
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(sessionsFile, sessions);
        } catch (IOException e) {
            log.error("Failed to write sessions", e);
        }
    }

    private void writeRecords(List<QARecord> records) {
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(recordsFile, records);
        } catch (IOException e) {
            log.error("Failed to write records", e);
        }
    }
}
