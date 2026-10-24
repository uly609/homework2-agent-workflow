from __future__ import annotations

import re
from pathlib import Path

from app.code_agent import CodeAgentRequest, CodeReviewAgent
from app.code_agent.memory import ConversationMemory
from app.workflow.models import WorkflowState


class ReviewAgent:
    """Reuses the Homework 1 review agent and publishes findings to shared state."""

    def __init__(self, memory_path: Path | None = None) -> None:
        memory = ConversationMemory(memory_path or Path(".homework2/memory.json"))
        self.agent = CodeReviewAgent(memory=memory)

    async def run(self, state: WorkflowState) -> None:
        response = await self.agent.run(CodeAgentRequest(
            task="review", code=state.current_code, session_id=state.workflow_id,
        ))
        state.review_runs.append(response)
        state.send("review_agent", "workflow", "review_completed", {
            "run": len(state.review_runs),
            "issue_count": len(response.issues),
            "rules": [issue.rule_id for issue in response.issues],
        })


class FixAgent:
    """Applies only the safe, narrow PY002 fix; leaves other findings for a person."""

    _BARE_EXCEPT = re.compile(r"^(?P<indent>[ \t]*)except[ \t]*:(?P<tail>[ \t]*(?:#.*)?)$")

    def run(self, state: WorkflowState) -> None:
        review = state.review_runs[-1]
        lines = state.current_code.splitlines(keepends=True)
        changed: list[int] = []
        for issue in review.issues:
            if issue.rule_id != "PY002" or issue.line is None:
                continue
            index = issue.line - 1
            if index < 0 or index >= len(lines):
                continue
            ending = "\n" if lines[index].endswith("\n") else ""
            body = lines[index][:-1] if ending else lines[index]
            match = self._BARE_EXCEPT.match(body)
            if match:
                lines[index] = f"{match.group('indent')}except Exception:{match.group('tail')}{ending}"
                changed.append(issue.line)

        if changed:
            before = state.current_code
            state.current_code = "".join(lines)
            state.patches.append({
                "agent": "fix_agent", "rule_id": "PY002",
                "lines": changed, "description": "将裸 except 改为 except Exception",
                "before": before, "after": state.current_code,
            })
        state.send("fix_agent", "workflow", "fix_completed", {
            "changed_lines": changed,
            "unresolved_rules": sorted({i.rule_id for i in review.issues if i.rule_id != "PY002"}),
        })
