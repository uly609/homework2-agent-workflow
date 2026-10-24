from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.code_agent.schemas import CodeAgentResponse


@dataclass
class WorkflowMessage:
    sequence: int
    sender: str
    recipient: str
    kind: str
    payload: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class WorkflowState:
    workflow_id: str
    original_code: str
    current_code: str
    messages: list[WorkflowMessage] = field(default_factory=list)
    patches: list[dict[str, Any]] = field(default_factory=list)
    review_runs: list[CodeAgentResponse] = field(default_factory=list)
    status: str = "created"
    error: str | None = None

    def send(self, sender: str, recipient: str, kind: str, payload: dict[str, Any]) -> None:
        self.messages.append(WorkflowMessage(
            sequence=len(self.messages) + 1, sender=sender, recipient=recipient,
            kind=kind, payload=payload,
        ))

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "original_code": self.original_code,
            "final_code": self.current_code,
            "patches": self.patches,
            "review_runs": [r.model_dump(mode="json") for r in self.review_runs],
            "messages": [asdict(m) for m in self.messages],
            "error": self.error,
        }


@dataclass
class WorkflowResult:
    state: WorkflowState

    @property
    def final_review(self) -> CodeAgentResponse:
        return self.state.review_runs[-1]

    def to_dict(self) -> dict[str, Any]:
        return self.state.to_dict()
