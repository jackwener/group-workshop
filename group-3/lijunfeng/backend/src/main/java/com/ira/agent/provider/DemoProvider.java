package com.ira.agent.provider;

import org.springframework.stereotype.Component;

/**
 * Demo 兜底提供商（对齐 08 §4 三级降级 — 第 3 级）
 * 始终可用，纯字符串拼接，不调用任何外部 API。
 */
@Component
public class DemoProvider {

    public boolean isAvailable() {
        return true; // 始终可用
    }

    public String ask(String query) {
        return "[离线演示] 您的问题是：「" + query + "」\n\n"
                + "当前处于离线演示模式，以下为模拟数据：\n"
                + "- 评级：中性\n"
                + "- 目标价：N/A\n"
                + "- 核心观点：该标的基本面平稳，暂无重大变化。\n\n"
                + "提示：这是一条离线演示回复，实际数据需连接 CoPaw 或百炼服务。";
    }

    public String getModel() {
        return "Demo-offline";
    }
}
