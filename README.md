# Homework 2: Code Review and Fix Workflow

A runnable two-Agent workflow that reuses the code review Agent from Homework 1. The Review Agent checks Python code; the Fix Agent applies a narrow safe fix for bare `except:`; then the workflow reviews the patched code again.

## Requirements

- Python 3.10 or newer
- `pydantic` 2.x

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=backend python scripts/homework2_workflow.py --file examples/unsafe_example.py
```

Pass inline source with `--code`, or use `--json` for the complete state, messages, patches, and review results:

```bash
PYTHONPATH=backend python scripts/homework2_workflow.py \
  --code $'def parse_number(value):\n    try:\n        return int(value)\n    except:\n        return None' --json
```

The included review Agent supports the same optional OpenAI-compatible provider settings as Homework 1: `CODE_AGENT_API_URL`, `CODE_AGENT_API_KEY`, and `CODE_AGENT_MODEL`. Static analysis and the deterministic workflow work without a model key. Do not commit credentials.

## What it demonstrates

- Two Agents collaborate in a complete sequential workflow: review → patch → re-review.
- Agents communicate through typed messages stored in a shared `WorkflowState`.
- The workflow branches: a clean review skips the Fix Agent; a review with issues invokes it. A second review runs only if a patch was applied.
- Review findings use static Python AST checks. The workflow never runs submitted source code.
- The Fix Agent only applies the reviewed `PY002` bare-except change. Other findings remain visible for manual repair.
- Conversation memory stores finding summaries under `.homework2/`; it does not save submitted source code.

## Project documents

- [`docs/design.md`](docs/design.md): architecture, workflow, state, safety, and limitations.
- [`examples/unsafe_example.py`](examples/unsafe_example.py): input for a complete demo run.
