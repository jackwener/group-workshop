"""
Skill Client — 对齐 Spec 08 §2 Skill Client 层
调用 Rabyte Skill API、处理异步结果
"""

import uuid


class SkillClient:
    """Rabyte Skill 深度分析客户端"""

    def __init__(self):
        self._tasks = {}  # analyze_id -> task dict

    def trigger_analysis(self, session_id, file_id):
        """对齐 Spec 09 §12 — 触发深度分析，返回 202"""
        analyze_id = f"ana_{uuid.uuid4().hex[:12]}"
        task = {
            "analyze_id": analyze_id,
            "session_id": session_id,
            "file_id": file_id,
            "status": "queued",
            "progress": 0,
            "result": None,
            "error": None,
        }
        self._tasks[analyze_id] = task

        # TODO: 异步调用 Rabyte Skill API
        # 当前为 stub，直接标记为 completed
        task["status"] = "completed"
        task["progress"] = 100
        task["result"] = self._mock_report()

        return {
            "analyze_id": analyze_id,
            "status": task["status"],
        }

    def get_analysis_status(self, analyze_id):
        """对齐 Spec 09 §13"""
        task = self._tasks.get(analyze_id)
        if not task:
            return None
        return {
            "analyze_id": task["analyze_id"],
            "status": task["status"],
            "progress": task["progress"],
            "result": task["result"],
            "error": task["error"],
        }

    def _mock_report(self):
        return (
            "# 深度分析报告（演示）\n\n"
            "## 1. 战略定位\n待实现 Rabyte Skill 集成\n\n"
            "## 2. 业务结构\n待实现\n\n"
            "## 3. 财务分析\n待实现\n\n"
            "## 4. 评级比对\n待实现\n"
        )


# 单例
skill_client = SkillClient()
