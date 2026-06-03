# 数字人视频 LLM 导演链路说明

## 当前问题

此前验证视频证明了 ComfyUI、Wan I2V、MuseTalk、TTS、ffmpeg 合成可以跑通，但它更接近一条单线视频渲染流程：

- 输入素材后直接生成或拼接视频片段。
- 数字人主要是照片口播，缺少统一人物设定和跨镜头一致性约束。
- 运营主题没有先经过 LLM 编剧、分镜、素材策略和质量门槛规划。
- 素材没有被明确区分为“参考约束”和“可直接使用素材”，容易变成素材拼接。

这不满足高质量商业视频产品要求。目标链路必须是 LLM 先做导演级生产规格，再交给视频生成和合成节点执行。

## 新增链路

已新增 `app/digital_humans/creative_planner.py`，并接入 `DigitalHumanService.create_video_job()`。

当创建数字人视频任务时传入：

```json
{
  "llm_planning_enabled": true,
  "planning_context": {
    "style": "真实高级",
    "requirement": "人物统一，素材只作参考"
  }
}
```

后端会先调用 `LLMClient`，根据运营目标、初始脚本、人像资产、素材资产、投放渠道、声音设置和时长要求生成一份结构化导演计划。

第二步新增 `POST /api/v1/digital-humans/video-jobs/{job_id}/shot-execution-plan`。它会把 LLM 的 `shot_plan` 转成逐镜头执行计划：

- 每个镜头有独立 `positive_prompt` / `negative_prompt`。
- 每个镜头有 `render_mode`，区分 `scene_i2v`、`avatar_scene_i2v`、`avatar_performance`。
- 每个镜头绑定身份参考、人像参考、场景/素材参考。
- 每个镜头有分辨率、帧率、时长、帧数和质量门槛。
- 输出 `prompt_contract` 和 `workflow_contract`，供后续 ComfyUI 真实图执行前替换为审核过的真实节点图。

## LLM 输出内容

LLM 计划会写入任务的 `provider_request.creative_plan` 和 `metadata.llm_creative_plan`，并转成 `scene_plan`。

计划包含：

- `production_intent`：定位、受众、叙事角度、核心价值。
- `character_bible`：人物身份、性格、视觉设定、服装和一致性规则。
- `voiceover`：最终口播、语气、节奏、去 AI 腔要求。
- `story_beats`：完整故事节奏。
- `shot_plan`：逐镜头分镜，每个镜头包含时长、镜头目标、运镜、视觉提示词、负面提示词、素材使用策略、人物一致性规则、口播句和质检项。
- `asset_strategy`：素材作为参考约束的策略，明确禁止简单素材拼接。
- `comfyui_plan`：建议的视频模型、工作流模板、分辨率、帧率和生成 pass。
- `quality_gates`：人物统一、画面连贯、声音自然、场景高级等质检门槛。

## 与本机 LLM 的关系

当前 `.env` 已配置：

```env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434
LOCAL_LLM_MODEL=llama70b
LOCAL_LLM_NUM_CTX=4096
```

因此在 Docker 后端内启用 `llm_planning_enabled` 后，会通过 Ollama 兼容接口调用本机 `llama70b`，而不是只走 mock 计划。

## 后续高质量生成要求

这次改动解决的是“LLM 是否进入生产链路”的问题，不等于马上达到最终商业成片质量。下一步必须按 LLM 分镜计划执行：

- 使用角色一致性工作流锁定同一个人物，而不是只做照片口播。
- 素材只作为空间、灯光、服装、人物和产品参考，输出应是重新生成的连贯镜头。
- 每个镜头按 `shot_plan.visual_prompt` 和 `shot_plan.negative_prompt` 生成，并按 `quality_checks` 自动/人工筛选。
- 声音需要优先接真人录音或声纹克隆；普通 TTS 只能作为预览。
- 低清预览通过后，再升到 1080x1920 或更高质量参数渲染。

## 验证

新增测试覆盖：

- 创建数字人视频任务时可调用 LLM 生成导演计划。
- LLM 生成的分镜写入 `provider_request.creative_plan`。
- LLM 生成的计划写入 `metadata.llm_creative_plan`。
- `scene_plan` 不再只有固定生产步骤，而包含 `llm_creative_direction` 和逐镜头 `llm_shot_*`。
- 逐镜头执行计划会写入 `metadata.shot_execution_plan` 和 `outputs`。
- ComfyUI handoff 在没有显式真实 prompt 时会优先使用逐镜头执行计划，而不是退回单一占位 prompt。

本地验证命令：

```powershell
$env:DIGITAL_HUMAN_PROVIDER='mock'
$env:DIGITAL_HUMAN_ENABLED='false'
$env:DIGITAL_HUMAN_ALLOW_EXTERNAL_API='false'
$env:COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED='false'
.\.venv\Scripts\python.exe -m pytest tests/test_digital_human_foundation.py tests/test_digital_human_workflow_binding.py tests/test_digital_human_execution_loop.py
```

## Commercial main-agent video orchestration

The commercial operation loop now has an explicit video-routing entrypoint:

`POST /api/v1/commercial-operations/{operation_id}/video-agent-orchestration`

This endpoint represents the expected big-agent pattern:

1. `commercial_video_main_agent` reads the commercial operation objective, channel, style, and requested materials.
2. `rag_agent` retrieves commercial knowledge context from the configured RAG collection when available.
3. The main agent routes video requests into the digital-human flow instead of treating them as plain content drafts.
4. `creative_director_agent`, `digital_human_video_agent`, `shot_execution_agent`, `voice_normalization_agent`, `comfyui_render_agent`, and `quality_review_agent` are returned as the specialist chain.
5. When `create_digital_human_job=true`, the endpoint creates a `DigitalHumanVideoJob` with `llm_planning_enabled=true` and passes the RAG evidence into `planning_context`.
6. When `prepare_shot_execution_plan=true`, the endpoint also converts the LLM creative plan into per-shot render contracts.

This closes the previous architectural gap where RAG and LLM planning existed, but the commercial video flow did not yet have a main agent deciding that a video specialist chain should run.

## Local LLM runtime note

On this server, `llama70b` must be called with `LOCAL_LLM_NUM_CTX=4096`.
Without this override, Ollama may load the model with a 131072-token context window, which increases the resident model size to roughly 120 GB and can force mixed CPU/GPU inference.
With `num_ctx=4096`, the same model loads at roughly 44 GB and stays on GPU for the planning calls.

The backend local provider now forwards `LOCAL_LLM_NUM_CTX` to Ollama as `options.num_ctx`, and the commercial video main-agent flow prefers fast seed planning before building shot contracts.
