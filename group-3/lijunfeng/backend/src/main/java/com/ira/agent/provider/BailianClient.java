package com.ira.agent.provider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Mock 百炼提供商（对齐 08 §4 三级降级 — 第 2 级）
 */
@Component
public class BailianClient {

    private static final Logger log = LoggerFactory.getLogger(BailianClient.class);

    @Value("${app.bailian.enabled:false}")
    private boolean enabled;

    public boolean isAvailable() {
        return enabled;
    }

    /**
     * 模拟调用百炼 LLM
     * @return 模拟回答，null 表示调用失败
     */
    public String ask(String query) {
        if (!enabled) {
            return null;
        }
        log.info("[百炼 Mock] Processing query: {}", query);
        try {
            Thread.sleep(300);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "[百炼] 针对您的问题「" + query + "」，分析如下：\n\n"
                + "基于最新研报数据，该标的近期表现符合行业趋势，"
                + "建议结合宏观经济指标综合判断。"
                + "具体评级和目标价请参考原始研报。\n\n"
                + "（以上为百炼模拟回答）";
    }

    public String getModel() {
        return "Bailian-v1";
    }
}
