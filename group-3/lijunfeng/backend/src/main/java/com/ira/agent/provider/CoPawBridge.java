package com.ira.agent.provider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Mock CoPaw 提供商（对齐 08 §4 三级降级 — 第 1 级）
 */
@Component
public class CoPawBridge {

    private static final Logger log = LoggerFactory.getLogger(CoPawBridge.class);

    @Value("${app.copaw.enabled:false}")
    private boolean enabled;

    public boolean isAvailable() {
        return enabled;
    }

    /**
     * 模拟调用 CoPaw LLM
     * @return 模拟回答，null 表示调用失败
     */
    public String ask(String query) {
        if (!enabled) {
            return null;
        }
        log.info("[CoPaw Mock] Processing query: {}", query);
        try {
            // 模拟网络延迟
            Thread.sleep(200);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "[CoPaw] 根据研报分析，关于「" + query + "」的解读如下：\n\n"
                + "1. 评级：增持\n"
                + "2. 目标价：预计未来12个月目标价上调10%\n"
                + "3. 核心观点：行业景气度持续上行，公司基本面稳健，建议关注。\n\n"
                + "（以上为 CoPaw 模拟回答）";
    }

    public String getModel() {
        return "CoPaw-v1";
    }
}
