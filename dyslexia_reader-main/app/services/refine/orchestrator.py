"""
LangGraph 编排器 — 状态图 + 迭代循环
"""

import logging
import copy
from typing import Literal, Optional

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from app.services.refine.base_agent import BaseAgent
from app.services.refine.evaluator import DyslexiaEvaluator
from app.services.refine.full_refine_agent import FullRefineAgent
from app.services.refine.summary_agent import SummaryAgent

logger = logging.getLogger(__name__)


# ---------- 状态 ----------

class RefineState(TypedDict):
    original_text: str
    mode: str                     # "full_refine" | "summary"
    summary_length: str           # 仅 summary 模式："简短" | "标准" | "详细"
    max_iterations: int
    pass_threshold: Optional[float]

    lang: str
    refined_text: str
    iter_count: int

    origin_score: dict
    current_score: dict
    score_history: list

    done: bool
    result: dict
    error: Optional[str]


# ---------- Orchestrator ----------

class RefineOrchestrator:
    """LangGraph 状态图编排器"""

    def __init__(self):
        self._base = BaseAgent()
        self.evaluator = DyslexiaEvaluator(self._base.client)
        self.full_refine_agent = FullRefineAgent(self._base.client)
        self.summary_agent = SummaryAgent(self._base.client)
        self.graph = self._build_graph()

    # ==================== 构建图 ====================

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(RefineState)

        workflow.add_node("pre_evaluate", self._pre_evaluate)
        workflow.add_node("refine_agent", self._refine_agent)
        workflow.add_node("summary_agent", self._summary_agent)
        workflow.add_node("judge", self._judge)

        workflow.set_entry_point("pre_evaluate")
        workflow.add_conditional_edges(
            "pre_evaluate",
            self._route_mode,
            {"full_refine": "refine_agent", "summary": "summary_agent"},
        )
        workflow.add_edge("refine_agent", "judge")
        workflow.add_edge("summary_agent", "judge")
        workflow.add_conditional_edges(
            "judge",
            self._should_continue,
            {"continue": "pre_evaluate", "end": END},
        )

        return workflow.compile()

    # ==================== 节点 ====================

    async def _pre_evaluate(self, state: RefineState) -> RefineState:
        """计算原文基线分"""
        lang = self._base._detect_lang(state["original_text"])
        origin_score = await self.evaluator.evaluate_all(
            state["original_text"], state["original_text"]
        )
        state["lang"] = lang
        state["origin_score"] = origin_score
        return state

    async def _refine_agent(self, state: RefineState) -> RefineState:
        """全文改写"""
        prev_score = state.get("current_score")
        state["iter_count"] = state.get("iter_count", 0) + 1

        state["refined_text"] = await self.full_refine_agent.refine(
            state["original_text"],
            state["lang"],
            prev_score,
        )
        return state

    async def _summary_agent(self, state: RefineState) -> RefineState:
        """摘要"""
        prev_score = state.get("current_score")
        state["iter_count"] = state.get("iter_count", 0) + 1

        state["refined_text"] = await self.summary_agent.summarize(
            state["original_text"],
            state["lang"],
            state.get("summary_length", "标准"),
            prev_score,
        )
        return state

    async def _judge(self, state: RefineState) -> RefineState:
        """评估本轮结果"""
        score = await self.evaluator.evaluate_all(
            state["original_text"], state["refined_text"]
        )
        state["current_score"] = score
        state["score_history"].append({
            "iteration": state["iter_count"],
            "total_score": score["total_score"],
            "content_fidelity": score["content"]["dimension_score"],
            "reading": score["reading"]["dimension_score"],
        })
        return state

    # ==================== 路由 & 终止判断 ====================

    @staticmethod
    def _route_mode(state: RefineState) -> Literal["full_refine", "summary"]:
        iter_count = state.get("iter_count", 0)
        # 第一轮直接路由到对应 Agent
        if iter_count == 0:
            return state["mode"]
        # 非首轮根据 mode 路由
        return state["mode"]

    @staticmethod
    def _should_continue(state: RefineState) -> Literal["continue", "end"]:
        if state.get("error"):
            return "end"

        # 最大轮次兜底
        if state["iter_count"] >= state["max_iterations"]:
            return "end"

        # 阈值判断
        threshold = state["pass_threshold"] or (0.65 if state["lang"] == "zh" else 0.70)
        sc = state["current_score"]
        content_ok = sc["content"]["dimension_score"] >= 0.70
        total_ok = sc["total_score"] >= threshold

        if total_ok and content_ok:
            return "end"
        return "continue"

    # ==================== 对外接口 ====================

    async def run(self, original_text: str, mode: str, *,
                  summary_length: str = "标准",
                  max_iterations: int = 3,
                  pass_threshold: float = None) -> dict:
        """运行完整流水线"""
        initial_state: RefineState = {
            "original_text": original_text,
            "mode": mode,
            "summary_length": summary_length,
            "max_iterations": max_iterations,
            "pass_threshold": pass_threshold,
            "lang": "",
            "refined_text": "",
            "iter_count": 0,
            "origin_score": {},
            "current_score": {},
            "score_history": [],
            "done": False,
            "result": {},
            "error": None,
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)

            # 计算改善幅度
            improvement = {}
            if final_state["origin_score"] and final_state["current_score"]:
                for dim in ["total_score", "reading", "content", "layout", "narrative"]:
                    if dim == "total_score":
                        before = final_state["origin_score"].get("total_score", 0)
                        after = final_state["current_score"].get("total_score", 0)
                    else:
                        before = final_state["origin_score"].get(dim, {}).get("dimension_score", 0)
                        after = final_state["current_score"].get(dim, {}).get("dimension_score", 0)
                    improvement[dim] = f"{after - before:+.4f}"

            return {
                "success": True,
                "mode": mode,
                "lang": final_state["lang"],
                "refined_text": final_state["refined_text"],
                "iterations": final_state["iter_count"],
                "origin_score": final_state["origin_score"],
                "final_score": final_state["current_score"],
                "improvement": improvement,
                "score_history": final_state["score_history"],
            }
        except Exception as e:
            logger.error(f"RefineOrchestrator 异常: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "mode": mode,
                "refined_text": "",
            }
