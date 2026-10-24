# HW2：代码审查与修复工作流

这是一个可以运行的双 Agent 协作示例，复用 HW1 的代码审查 Agent，并新增修复 Agent。审查 Agent 先检查 Python 代码；如果发现裸 `except:`，修复 Agent 会进行安全、范围明确的修改；随后审查 Agent 再次检查修复结果。

## 环境要求

- Python 3.10 或更高版本
- `pydantic` 2.x

## 安装与运行

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=backend python scripts/homework2_workflow.py --file examples/unsafe_example.py
```

也可以直接传入代码。添加 `--json` 可查看完整工作流状态、Agent 消息、补丁和审查结果：

```bash
PYTHONPATH=backend python scripts/homework2_workflow.py \
  --code $'def parse_number(value):\n    try:\n        return int(value)\n    except:\n        return None' --json
```

内置审查 Agent 支持与 HW1 相同的 OpenAI 兼容服务配置：`CODE_AGENT_API_URL`、`CODE_AGENT_API_KEY` 和 `CODE_AGENT_MODEL`。静态分析和确定性工作流不需要模型密钥。请勿将密钥提交到仓库。

## 项目介绍

本项目演示两个 Agent 如何通过共享状态和消息按顺序协作，完成“审查 → 修复 → 复审”的代码处理流程。工作流根据审查结果进行分支：代码没有问题时跳过修复；发现问题时调用修复 Agent；只有应用了补丁才会执行第二轮审查。

代码检查使用 Python AST 静态分析，不会运行用户提交的代码。当前修复 Agent 仅自动处理审查规则 `PY002` 指出的裸 `except:`，其他问题会保留在结果中供开发者手动处理。对话记忆会把问题摘要保存在 `.homework2/`，但不会保存提交的源代码。

## 提交内容

- [`docs/design.md`](docs/design.md)：项目目标、架构、工作流、共享状态、安全策略和限制。
- [`examples/unsafe_example.py`](examples/unsafe_example.py)：可用于演示完整流程的示例输入。
- [`demo-video.mp4`](demo-video.mp4)：21 秒的实际终端操作录屏，展示运行命令、问题审查、自动修复、复审结果和 Agent 消息记录。
