package com.ira.agent.service;

import com.ira.agent.provider.BailianClient;
import com.ira.agent.provider.CoPawBridge;
import com.ira.agent.provider.DemoProvider;
import com.ira.agent.provider.LlmResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 问答编排服务 — 三级降级（对齐 08 §4）
 * 降级链：CoPaw → 百炼 → Demo
 */
@Service
public class AgentService {

    private static final Logger log = LoggerFactory.getLogger(AgentService.class);

    private final CoPawBridge coPawBridge;
    private final BailianClient bailianClient;
    private final DemoProvider demoProvider;

    public AgentService(CoPawBridge coPawBridge, BailianClient bailianClient, DemoProvider demoProvider) {
        this.coPawBridge = coPawBridge;
        this.bailianClient = bailianClient;
        this.demoProvider = demoProvider;
    }

    /**
     * 执行问答，按三级降级链尝试
     */
    public LlmResult ask(String query) {
        long start = System.currentTimeMillis();

        // 第 1 级：CoPaw
        if (coPawBridge.isAvailable()) {
            try {
                String answer = coPawBridge.ask(query);
                if (answer != null) {
                    log.info("CoPaw returned answer in {}ms", System.currentTimeMillis() - start);
                    return new LlmResult(answer, "copaw", true, coPawBridge.getModel());
                }
            } catch (Exception e) {
                log.warn("CoPaw failed, falling back to 百炼: {}", e.getMessage());
            }
        }

        // 第 2 级：百炼
        if (bailianClient.isAvailable()) {
            try {
                String answer = bailianClient.ask(query);
                if (answer != null) {
                    log.info("百炼 returned answer in {}ms", System.currentTimeMillis() - start);
                    return new LlmResult(answer, "bailian", true, bailianClient.getModel());
                }
            } catch (Exception e) {
                log.warn("百炼 failed, falling back to Demo: {}", e.getMessage());
            }
        }

        // 第 3 级：Demo（始终可用）
        String answer = demoProvider.ask(query);
        log.info("Demo returned answer in {}ms", System.currentTimeMillis() - start);
        return new LlmResult(answer, "demo", false, demoProvider.getModel());
    }

    /**
     * 获取各提供商能力状态
     */
    public Map<String, Object> getCapabilities() {
        Map<String, Object> caps = new LinkedHashMap<>();

        Map<String, Object> copaw = new LinkedHashMap<>();
        copaw.put("available", coPawBridge.isAvailable());
        copaw.put("model", coPawBridge.getModel());
        caps.put("copaw", copaw);

        Map<String, Object> bailian = new LinkedHashMap<>();
        bailian.put("available", bailianClient.isAvailable());
        bailian.put("model", bailianClient.getModel());
        caps.put("bailian", bailian);

        Map<String, Object> demo = new LinkedHashMap<>();
        demo.put("available", demoProvider.isAvailable());
        demo.put("model", demoProvider.getModel());
        caps.put("demo", demo);

        return caps;
    }
}
