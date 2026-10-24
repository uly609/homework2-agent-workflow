from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from app.workflow import WorkflowEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Homework 2 sequential multi-Agent workflow")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="Python file to review and safely patch")
    source.add_argument("--code", help="Python source code as text")
    parser.add_argument("--workflow-id", default="homework2-demo")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    code = args.file.read_text(encoding="utf-8") if args.file else (args.code or "")
    result = WorkflowEngine().run_sync(code, args.workflow_id)
    state = result.state
    if args.as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"Workflow: {state.workflow_id} ({state.status})")
    for i, review in enumerate(state.review_runs, start=1):
        print(f"\nReview {i}: {len(review.issues)} issue(s)")
        for issue in review.issues:
            where = f"line {issue.line}" if issue.line else "file"
            print(f"- [{issue.severity}] {issue.rule_id} {where}: {issue.message}")
            print(f"  建议：{issue.suggestion}")
    if state.patches:
        print("\nPatch:")
        print("".join(difflib.unified_diff(
            state.original_code.splitlines(keepends=True),
            state.current_code.splitlines(keepends=True),
            fromfile="before.py", tofile="after.py",
        )), end="")
    else:
        print("\nNo automatic patch was applicable.")
    print(f"\nMessages exchanged: {len(state.messages)}")
    for message in state.messages:
        print(f"{message.sequence}. {message.sender} -> {message.recipient}: {message.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
