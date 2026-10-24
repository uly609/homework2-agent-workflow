from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from app.workflow.agents import FixAgent, ReviewAgent
from app.workflow.models import WorkflowResult, WorkflowState


class WorkflowEngine:
    """Sequential review -> fix -> review workflow with conditional branch and shared state."""

    def __init__(self, memory_path: Path | None = None) -> None:
        self.reviewer = ReviewAgent(memory_path)
        self.fixer = FixAgent()

    async def run(self, code: str, workflow_id: str | None = None) -> WorkflowResult:
        if not code.strip():
            raise ValueError("code must not be empty")
        state = WorkflowState(
            workflow_id=workflow_id or str(uuid.uuid4()),
            original_code=code, current_code=code, status="running",
        )
        state.send("workflow", "review_agent", "review_requested", {"source": "original_code"})
        await self.reviewer.run(state)

        if state.review_runs[-1].issues:
            state.send("workflow", "fix_agent", "fix_requested", {
                "based_on_review_run": len(state.review_runs),
            })
            self.fixer.run(state)
        else:
            state.send("workflow", "workflow", "fix_skipped", {"reason": "no_issues_found"})

        if state.patches:
            state.send("workflow", "review_agent", "review_requested", {"source": "patched_code"})
            await self.reviewer.run(state)
        state.status = "completed"
        state.send("workflow", "caller", "workflow_completed", {
            "review_runs": len(state.review_runs), "patch_count": len(state.patches),
            "remaining_issue_count": len(state.review_runs[-1].issues),
        })
        return WorkflowResult(state)

    def run_sync(self, code: str, workflow_id: str | None = None) -> WorkflowResult:
        return asyncio.run(self.run(code, workflow_id))
