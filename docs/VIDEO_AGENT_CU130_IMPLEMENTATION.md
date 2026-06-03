# 视频 Agent CU130 实现记录

更新日期：2026-05-28

本文记录当前视频 specialist Agent 的实现范围、输入输出契约、CU130 工作流选择逻辑，以及用最初抖音/KTV需求跑出的验证结果。它是主 Agent 下面的视频生产分支文档，不是单个 KTV 项目的 prompt 备忘录。

## 1. 当前结论

已新增 `app/commercial_operations/video_agent.py`，视频 Agent 现在能完成四件事：

1. 读取 `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl`，基于 CU130 真实工作流 RAG 文档做阶段化选流。
2. 输出 `video_analysis_result` 契约：有参考视频时进入视频解析合同；只有场景图时走场景图锚定路线。
3. 输出 `workflow_selection`：按 `reference_video_analysis`、`ai_virtual_host_seed`、`scene_i2v_motion`、`digital_human_i2v`、`motion_transfer`、`post_processing` 分阶段给出候选工作流。
4. 输出 `execution_package`：把选流结果转成可审查的执行包，但不直接提交 ComfyUI 队列。

当前视频 Agent 不是“凭感觉写 ComfyUI 节点图”。它先基于已审计的 CU130 工作流知识库选流，再把选流结果交给人工审核、运行时预检和 ComfyUI gate。

## 2. API 变化

接口仍是：

```http
POST /api/v1/commercial-operations/{operation_id}/video-agent-orchestration
```

请求新增关键字段：

```json
{
  "source_video_uri": "file:///D:/ai-operations-system/douyin_7575632283172932870.mp4",
  "scene_image_uri": "file:///D:/ai-operations-system/douyin_frames/frame_004.jpg",
  "reference_video_uri": null,
  "needs_ai_virtual_person": true,
  "allow_real_person_cutout": false,
  "allow_comfyui_prompt_submission": false
}
```

响应新增关键字段：

```json
{
  "video_agent_plan": {},
  "video_analysis_result": {},
  "workflow_selection": {},
  "execution_package": {},
  "runtime_evidence": {}
}
```

`allow_comfyui_prompt_submission` 当前只作为安全边界字段保留。视频 Agent 不会因为它是 `true` 就自动提交队列，真实渲染仍应由后续 runtime gate/approval 触发。

## 3. 针对最初需求的正确理解

最初需求是：

1. 一张 KTV/商K场景图，生成同场景视频。
2. 人物必须是 AI 生成的虚拟美女/虚拟主持人。
3. 不找真人画像、不抠图、不把真人贴进场景。
4. 抖音参考视频只用于学习结构、镜头、节奏、口播、场景风格，不作为真人身份来源。

因此视频 Agent 的默认 `primary_character_source` 是：

```json
"ai_generated_fictional_host"
```

旧逻辑里“上传授权肖像”的下一步动作已经调整。现在默认下一步是生成并审核一个 fictional AI virtual-host identity。

## 4. 分阶段工作流选择

视频 Agent 现在按生产阶段选择工作流，而不是只给一个泛泛候选：

| 阶段 | 作用 | CU130能力标签 |
|---|---|---|
| `reference_video_analysis` | 解析参考视频：抽帧、音频、ASR、VLM、分镜 | `video_analysis` |
| `ai_virtual_host_seed` | 生成虚拟主持人身份/首帧/场景关键帧 | `image_generation` |
| `scene_i2v_motion` | 场景图/关键帧转视频 | `image_to_video` |
| `digital_human_i2v` | 数字人口播、对口型、轻动作 | `image_to_video`, `digital_human` |
| `motion_transfer` | 只有存在参考动作视频时使用 | `motion_transfer`, `segmentation` |
| `post_processing` | 合成、字幕、音频、质检物料 | `post_processing` |

对于“只有场景图”的路线，`motion_transfer` 会被跳过；对于“有参考动作视频”的路线，才把 WanAnimate/SAM/MatAnyone 等作为主候选。

## 5. 原始需求本地验证

验证脚本：

```powershell
.\.venv\Scripts\python.exe scripts\run_video_agent_requirement_test.py
```

输出文件：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_video_agent_output.json
```

本次输出摘要：

```json
{
  "status": "ready_for_review",
  "workflow_candidate_count": 114,
  "primary_digital_human_workflow": "Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json",
  "primary_ai_host_seed_workflow": "Qwan-Image-Edit+SAM3_人物图像遮罩替换.json",
  "blocking_conditions": []
}
```

这说明视频 Agent 对最初需求的判断是：

1. 场景图素材存在，能够进入同场景虚拟主持人路线。
2. CU130 工作流知识库中有 114 个候选工作流。
3. 数字人主流程优先选 `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json`。
4. 虚拟主持人首帧/身份阶段优先选 Qwen Image Edit + SAM3 类工作流。
5. 当前状态是 `ready_for_review`，不是自动渲染完成。

## 6. 运行时验证

已运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\verify_comfyui_cu130_aiops.ps1
```

结果：

```text
ComfyUI_cu130 AI Ops verification completed successfully.
models=341 total_gb=950.47 workflows=114
```

关键能力已确认：

1. ComfyUI `0.21.1`
2. PyTorch `2.9.1+cu130`
3. RTX 5090
4. `LoadVideo` / `VHS_LoadVideo`
5. `AILab_Qwen3ASR`
6. `AILab_QwenVL`
7. `SAM3_Detect`
8. `DepthAnything_V2`
9. `Wan2_1-infiniTetalk-single_fp16.safetensors`

## 7. 已通过测试

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\test_commercial_video_agent.py `
  tests\test_commercial_operation_main_agent.py `
  tests\test_commercial_operations_api.py -q
```

结果：

```text
8 passed
```

## 8. 当前边界

已完成的是“视频 Agent 闭环的计划、选流、执行包输出和原始需求验证”，不是最终成片渲染。

还没有自动做的事：

1. 不自动改写 ComfyUI UI workflow 节点图。
2. 不自动提交 ComfyUI 队列。
3. 不自动生成最终 mp4。
4. 不自动发布到社媒。

这些边界是刻意保留的，因为真实服务器上的 ComfyUI 渲染、账号发布和客户机执行都必须走审批与 runtime gate。

## 9. Workflow 只读副本策略

原始 CU130 workflow 必须视为只读模板，不能被任务执行覆盖。当前已新增：

```text
app/comfyui_runtime/workflow_materializer.py
```

它的职责是：

1. 读取原始 `workflow_path`。
2. 计算原始文件 `sha256`。
3. 在内存里 deep copy workflow。
4. 把本次任务的 `positive_prompt`、`negative_prompt`、`image`、`video`、`audio`、`width`、`height`、`frames`、`fps`、`filename_prefix` 注入副本。
5. 写入 `storage/comfyui_materialized_workflows/{run_id}/{stage_key}/...materialized.json`。
6. 再次计算原始文件 `sha256`，确认 `original_unchanged=true`。

支持两类工作流：

1. API prompt JSON：节点形态为 `{ "1": { "class_type": "...", "inputs": {} } }`。
2. UI workflow JSON：节点形态为 `{ "nodes": [{ "type": "...", "widgets_values": ... }] }`。

默认会按节点类型和字段名自动注入常见字段；如果某个工作流节点很特殊，可以通过 `node_overrides` 精确指定节点和输入名：

```json
{
  "6": {
    "prompt": "exact Qwen edit instruction for this run"
  },
  "317": {
    "positive_prompt": "exact Wan positive prompt",
    "negative_prompt": "exact Wan negative prompt"
  }
}
```

注意：materializer 仍然不提交 `/prompt`。它只生成安全的运行副本。后续提交必须继续通过 runtime gate。

已用最初需求选中的真实工作流做过一次只读 materialize smoke：

```json
{
  "source": "E:\\ComfyUI_cu130\\ComfyUI\\user\\default\\workflows\\5-数字人：图像语音对口型-唱歌-带货-对话\\Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json",
  "materialized": "D:\\ai-operations-system\\storage\\comfyui_materialized_workflows\\original_douyin_requirement_smoke\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ.materialized.json",
  "graph_format": "ui_workflow",
  "original_unchanged": true,
  "injected_change_count": 11
}
```

## 10. API prompt 预检与短视频 smoke 状态

本节新增了真实 ComfyUI API prompt 预检脚本：

```powershell
.\.venv\Scripts\python.exe scripts\preflight_selected_comfyui_video_workflow.py
```

脚本职责：

1. 读取视频 Agent 对最初 KTV/抖音需求生成的 `execution_package`。
2. 找到主工作流 `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json`。
3. 复制原始 workflow 到 `storage/comfyui_materialized_workflows/...`，保持源 workflow 只读。
4. 把 UI workflow 转换为 ComfyUI `/prompt` 可提交的 API prompt。
5. 调用真实 ComfyUI `/object_info` 做节点类型和 required input 预检。
6. 检查 ComfyUI input 目录是否存在本次运行必需素材。
7. 只输出报告，不提交队列。

当前真实预检结果：

```json
{
  "status": "ready_for_queue_submit",
  "queue_submission_attempted": false,
  "source_workflow_original_unchanged": true,
  "api_prompt_node_count": 26,
  "prompt_structurally_ready": true,
  "missing_node_types": [],
  "unresolved_inputs_count": 0,
  "asset_ready": true,
  "api_prompt_path": "D:\\ai-operations-system\\storage\\comfyui_materialized_workflows\\original_douyin_requirement_short_video_safetensors\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ.materialized.api_prompt.json"
}
```

为避免直接跑 12 秒完整版，短视频 smoke 使用了节点覆盖：

```json
{
  "319": { "value": 640 },
  "320": { "value": 49 },
  "122": {
    "model": "Wan\\Wan2.1-I2V_14B_480p_fp8_e4m3fn_scaled_KJ.safetensors"
  },
  "120": {
    "model": "Wan\\Wan2_1-InfiniteTalk-Single_fp8_e4m3fn_scaled_KJ.safetensors"
  }
}
```

含义：

1. `319` 控制首帧缩放最长边，smoke 固定为 640。
2. `320` 控制 InfiniteTalk 帧数，smoke 固定为 49 帧。
3. `122` 是完整 WanVideo 主模型，必须是 full WanVideo model。
4. `120` 是 InfiniteTalk/MultiTalk 分支模型，必须和主模型格式匹配；本次使用 safetensors + safetensors。

已准备的运行素材：

```text
E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed.png
E:\ComfyUI_cu130\ComfyUI\input\voiceover.wav
```

注意：当前 `scene_ai_virtual_host_seed.png` 使用的是服务器已有 AI 虚拟主持人 KTV 首帧，目的是验证视频链路可运行，不代表最终商业质量或最终同场景锁定结果。正式成片仍需要先跑并审核 `ai_virtual_host_seed` 阶段。

短视频 smoke 执行记录：

| 尝试 | prompt_id | 结果 | 结论 |
|---|---|---|---|
| resource gate | 无 | `video resource admission queued` | 当时 ComfyUI 已有运行中任务，未插队 |
| widget fixed | `e5d00b95-40c0-4700-ba0a-5b09c0650ba5` | `WanVideoSampler KeyError: blocks.0.norm_x.weight` | UI widget 顺序已修正，但原 workflow 的 AniWan 主模型与 sampler 权重不匹配 |
| model fixed GGUF | `e05faa46-64b6-4584-b783-f35c1629bd79` | `No patch_embedding weight found` | InfiniteTalk GGUF 不是完整主模型，不能放入主模型节点 |
| full Wan safetensors | `4a0c426f-f78e-4d54-80b5-8e43d914786b` | `Multitalk/InfiniteTalk model is a GGUF model` | 主模型 safetensors 不能搭配 InfiniteTalk GGUF |
| safetensors matched | `b9aac859-326a-494c-8aca-98ba1fad7a5f` | `success` | 产出 mp4 |

最终成功的 history 摘要：

```json
{
  "prompt_id": "b9aac859-326a-494c-8aca-98ba1fad7a5f",
  "status": "success",
  "completed": true,
  "video": "E:\\ComfyUI_cu130\\ComfyUI\\output\\aiops\\original_douyin_requirement_short_video_safetensors\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ_00001-audio.mp4",
  "width": 368,
  "height": 640,
  "frames": 49,
  "fps": 24,
  "duration_seconds": 2.041667
}
```

汇总报告已写入：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_short_video_smoke_result.json
```

这说明视频链路已经从“选流/预检”推进到“真实 ComfyUI 产出 mp4”。当前产物仍是 49 帧 smoke，不是最终商业成片。

## 11. 下一步工程节奏

下一节应优先把 smoke 产物升级为更接近抖音目标的正式链路：

1. 质检 smoke：人物是否正常、口型是否跟随音频、画面是否闪烁、场景是否保持。
2. 回到 `ai_virtual_host_seed` 阶段，用原始场景图生成更符合“同场景 + AI 虚拟美女主持人”的首帧。
3. 把成功的 safetensors 模型组合固化为该 KJ InfiniteTalk 工作流的执行策略，而不是写回原始 workflow。
4. 通过首帧质检后再跑 9:16 正式视频片段。
5. 把输出 mp4、prompt、workflow 副本、history、质检结果写入 deliverable，再交给客户机发布链路。

## 12. v2 首帧与视频 smoke

本轮继续推进“干净场景图 -> AI 虚拟美女主持人首帧 -> InfiniteTalk 视频”的闭环。

### 12.1 场景素材判断

最初抖音解析出来的 `douyin_frames/frame_004.jpg` 不是干净场景图，而是带多宫格、字幕和讲解头像的参考截图，不适合作为正式首帧输入。为保证同场景质量，本轮改用本地已有干净 KTV 场景图：

```text
D:\ai-operations-system\storage\digital_human_assets\ktv-backend-20260527\4551e9fc-3866-408e-8f7f-8d12ca961ccc.jpg
```

该素材已复制到 ComfyUI input：

```text
E:\ComfyUI_cu130\ComfyUI\input\ktv_clean_scene_for_ai_host.jpg
```

### 12.2 首帧工作流选择

首选的 `Qwan-Image-Edit+SAM3_人物图像遮罩替换.json` 更适合“已有角色图 + 已有人物遮罩替换”，不是最干净的空场景生成人物路线。排名第二的多视角 Qwen workflow 在当前运行时缺少 `easy getNode/easy setNode`，预检被阻断。

因此本轮实际采用稳定单图编辑候选：

```text
Qwen-Image-Edit_图生图_单图编辑(GGUF).json
```

执行脚本：

```powershell
.\.venv\Scripts\python.exe scripts\run_ai_virtual_host_seed_workflow.py --base-url http://127.0.0.1:8188
```

结果：

```json
{
  "status": "success",
  "seed_prompt_id": "af58824d-6b33-4e4d-ac76-72208bdbeb7d",
  "registered_seed": "E:\\ComfyUI_cu130\\ComfyUI\\input\\scene_ai_virtual_host_seed_v2.png"
}
```

v2 首帧质检结论：

1. 人物为成年虚拟女性主持人，不是外部真人肖像。
2. 脸部、手部、身体比例未见明显畸形。
3. 场景保持为蓝色灯光 KTV 包间。
4. 当前构图是中景/半身，不是正式目标里的全身或更开阔站位。

### 12.3 v2 视频 smoke

v2 首帧已接入上一节跑通的 InfiniteTalk 视频流，继续使用原始 workflow 的只读副本策略。

预检命令：

```powershell
.\.venv\Scripts\python.exe scripts\preflight_selected_comfyui_video_workflow.py `
  --run-id original_douyin_requirement_seed_v2_video_smoke `
  --frames 49 `
  --scale-to-length 640 `
  --scene-image-name scene_ai_virtual_host_seed_v2.png `
  --wan-model 'Wan\Wan2.1-I2V_14B_480p_fp8_e4m3fn_scaled_KJ.safetensors' `
  --multitalk-model 'Wan\Wan2_1-InfiniteTalk-Single_fp8_e4m3fn_scaled_KJ.safetensors' `
  --report-path deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_seed_v2_video_preflight.json
```

提交结果：

```json
{
  "status": "success",
  "video_prompt_id": "4ed5fe27-4179-4da2-bb3b-ea645329d1d3",
  "video": "E:\\ComfyUI_cu130\\ComfyUI\\output\\aiops\\original_douyin_requirement_seed_v2_video_smoke\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ_00001-audio.mp4",
  "width": 368,
  "height": 640,
  "frames": 49,
  "fps": 24,
  "duration_seconds": 2.041667
}
```

汇总报告：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_seed_v2_video_smoke_result.json
```

v2 视频 smoke 质检结论：

1. 视频真实产出 mp4，证明“首帧生成 -> 视频驱动 -> 合成输出”闭环可运行。
2. 人物整体正常，场景稳定，口播驱动能产生表情和口型变化。
3. 仍不是正式商业成片：时长仅 49 帧，分辨率为 smoke 级，人物构图偏半身。
4. 下一轮应把首帧 prompt 调成更开阔站位、完整身体比例、竖版商业构图，然后跑 6-12 秒正式片段。

## 13. 全身首帧补测记录

为接近最初抖音参考里的“同场景 + 虚拟美女数字人”目标，本轮补测了更开阔的 KTV 场景图：

```text
D:\ai-operations-system\storage\digital_human_assets\ktv-backend-20260527\72bc1fc4-996d-4551-b801-a8e8f4766fcc.jpg
```

该图是竖版包间场景，画面空间比 v2 输入更开阔，理论上更适合生成站立全身主持人。测试仍使用只读副本策略，原始 workflow 不被覆盖；提示词文件写入：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v3_fullbody_positive.txt
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v3_fullbody_negative.txt
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v4_fullbody_female_positive.txt
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v4_fullbody_female_negative.txt
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v5_fullbody_female_zh_positive.txt
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\prompts\v5_fullbody_female_zh_negative.txt
```

三次首帧补测结果：

| 尝试 | prompt_id | 输出文件 | 质检结论 |
|---|---|---|---|
| v3 | `34992341-6dfd-4e10-8b94-760b044c71db` | `E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed_v3.png` | 不合格：生成偏男性，且仍是半身构图。 |
| v4 | `b52b9eba-9e6f-49a0-bda9-4a4185109e4e` | `E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed_v4.png` | 不合格：仍偏男性，构图没有稳定变成全身女性主持人。 |
| v5 | `46e5ced2-1b9e-425a-b914-82247fd4603e` | `E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed_v5.png` | 不合格：变成女性，但仍偏近景/半身，并出现手部与花束遮挡，不适合进入正式视频链路。 |

客观结论：当前 `Qwen-Image-Edit_图生图_单图编辑(GGUF).json` 可以完成“场景图编辑出人物”的基础能力，但自动化 prompt 对“同场景、全身、女性、商业主持人站位”的约束不稳定。它不应被否定，正确用法是把它作为首帧生成/筛选环节：生成多张候选，人工或质检模型确认合格首帧后，再进入数字人视频流。

## 14. 全身种子 7 秒视频 smoke

由于 v3-v5 首帧均未达到进入视频阶段的质量，本轮使用当前已验证最好的全身虚拟女性 KTV 首帧继续测试视频链路：

```text
E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed.png
```

预检命令：

```powershell
.\.venv\Scripts\python.exe scripts\preflight_selected_comfyui_video_workflow.py `
  --run-id original_douyin_requirement_fullbody_6s_video_smoke `
  --frames 144 `
  --scale-to-length 640 `
  --scene-image-name scene_ai_virtual_host_seed.png `
  --wan-model 'Wan\Wan2.1-I2V_14B_480p_fp8_e4m3fn_scaled_KJ.safetensors' `
  --multitalk-model 'Wan\Wan2_1-InfiniteTalk-Single_fp8_e4m3fn_scaled_KJ.safetensors' `
  --report-path deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_preflight.json
```

提交与产出：

```json
{
  "status": "success",
  "video_prompt_id": "25884770-639e-4bcc-a72f-aa740d93b6b1",
  "video": "E:\\ComfyUI_cu130\\ComfyUI\\output\\aiops\\original_douyin_requirement_fullbody_6s_video_smoke\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ_00001-audio.mp4",
  "width": 368,
  "height": 640,
  "requested_frames": 144,
  "frames": 169,
  "fps": 24,
  "duration_seconds": 7.041667
}
```

记录文件：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_preflight.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_submit.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_history.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_smoke_result.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_fullbody_6s_video_contact.jpg
```

质检结论：

1. 视频真实产出 mp4，且长度已从 2 秒 smoke 推进到约 7.04 秒。
2. 抽帧显示人物为全身虚拟女性，场景整体稳定，有轻微手臂动作和口播驱动变化。
3. 该片段可作为“视频部分已跑通”的工程证明，但仍不是最终商业成片：分辨率为 smoke 级，人物美术质量与抖音参考仍有差距。
4. 下一步应补“可控首帧生成”能力，而不是继续使用单图编辑 workflow 盲试。建议路线是：先用姿态/深度/局部重绘/人物位置控制生成合格首帧，再进入当前已跑通的 InfiniteTalk 视频工作流。

## 15. 人工确认 Qwen 首帧进入数字人流

用户在 ComfyUI 中使用 `Qwen-Image-Edit_图生图_单图编辑(GGUF).json` 生成了一张更合格的虚拟女性 KTV 首帧。该图不是外部真人抠图，符合“直接 AI 一个虚拟美女”的项目约束。

原始输出：

```text
E:\ComfyUI_cu130\ComfyUI\output\ComfyUI_00006_.png
```

注册到 ComfyUI input 的稳定文件名：

```text
E:\ComfyUI_cu130\ComfyUI\input\operator_approved_qwen_image_edit_seed.png
```

预检命令：

```powershell
.\.venv\Scripts\python.exe scripts\preflight_selected_comfyui_video_workflow.py `
  --run-id original_douyin_requirement_operator_qwen_seed_video_smoke `
  --frames 144 `
  --scale-to-length 640 `
  --scene-image-name operator_approved_qwen_image_edit_seed.png `
  --wan-model 'Wan\Wan2.1-I2V_14B_480p_fp8_e4m3fn_scaled_KJ.safetensors' `
  --multitalk-model 'Wan\Wan2_1-InfiniteTalk-Single_fp8_e4m3fn_scaled_KJ.safetensors' `
  --report-path deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_preflight.json
```

执行过程记录：

1. 首次 runtime guard 使用 `.env` 中的 `host.docker.internal:8188` 读取 `/system_stats`，返回 502，未提交。
2. 直接验证 `http://127.0.0.1:8188/system_stats` 正常，能读取 RTX 5090 与 VRAM。
3. 已把当前服务器本地运行配置改为：

```env
COMFYUI_RUNTIME_BASE_URL=http://127.0.0.1:8188
COMFYUI_VIDEO_GPU_ENDPOINTS=default|http://127.0.0.1:8188|0
```

4. 队列中存在一个手工提交的阻塞任务 `733a8e41-a941-4712-9736-6dece13cfae5`，使用的是此前验证失败的 `Wan2.1_I2V_14B_480p_AniWan_New_Q5_K_M.gguf + Wan2_1-InfiniteTalk_Single_Q6_K.gguf` 组合。该任务长期占用运行位后被中断，正确的 safetensors 任务继续执行。

最终提交结果：

```json
{
  "status": "success",
  "video_prompt_id": "0b233082-6838-4783-814f-50da3bdd1076",
  "video": "E:\\ComfyUI_cu130\\ComfyUI\\output\\aiops\\original_douyin_requirement_operator_qwen_seed_video_smoke\\digital_human_i2v\\Wan2.1_I2V_InfiniteTalk__KJ_00001-audio.mp4",
  "width": 368,
  "height": 640,
  "requested_frames": 144,
  "frames": 169,
  "fps": 24,
  "duration_seconds": 7.041667
}
```

记录文件：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_preflight.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_submit.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_history.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_smoke_result.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_operator_qwen_seed_video_contact.jpg
```

质检结论：

1. 这一路线是当前最符合项目要求的实现方式：`Qwen Image Edit 首帧 -> 人工/模型质检确认 -> InfiniteTalk 数字人视频`。
2. 输出视频真实成功，场景稳定，虚拟女性主持人正常，口播视频流已跑通。
3. 当前首帧下半身被桌子遮挡，不是完整全身；手臂动作较小，适合 smoke 和口播数字人验证，不是最终商业成片。
4. 下一步应把“首帧候选生成 + 质检筛选 + 合格首帧入数字人流”固化到 Video Agent，而不是要求每次都从 workflow 里手工找图。

## 16. 商K目录全流程实跑

本轮按用户指定目录结构执行完整链路：

```text
E:\ComfyUI_cu130\ComfyUI\input\商k\场景
E:\ComfyUI_cu130\ComfyUI\input\商k\视频参考
E:\ComfyUI_cu130\ComfyUI\output\商k\首图生成
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成
```

输入素材：

```text
场景图：
E:\ComfyUI_cu130\ComfyUI\input\商k\场景\aiops_hq_20260527170712_scene_04_service_room_detail_00001.png

参考视频：
E:\ComfyUI_cu130\ComfyUI\input\商k\视频参考\video_我在这边你要往那边转啊#KTV正..._0.mp4
```

参考视频信息：

```json
{
  "duration_seconds": 15.0,
  "video": "1080x1920, 30fps, 450 frames",
  "audio": "aac, 14.976893s"
}
```

执行脚本：

```powershell
.\.venv\Scripts\python.exe scripts\run_shangk_full_pipeline.py `
  --run-id shangk_full_pipeline_current `
  --max-duration-seconds 15
```

脚本边界：

1. 自动从 `商k\场景` 选择最新场景图。
2. 自动从 `商k\视频参考` 选择最新参考视频。
3. 用 ffmpeg 抽取参考视频音频到：

```text
E:\ComfyUI_cu130\ComfyUI\input\商k\shangk_reference_audio.wav
```

4. 使用 `Qwen-Image-Edit_图生图_单图编辑(GGUF).json` 生成首图，输出到 `output\商k\首图生成`。
5. 将首图注册为数字人视频输入：

```text
E:\ComfyUI_cu130\ComfyUI\input\商k\shangk_approved_first_frame.png
```

6. 使用 `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json` 生成视频，输出到 `output\商k\视频生成`。
7. 原始 workflow 仍不覆盖，只写 `storage\comfyui_materialized_workflows` 下的每次运行副本。

首图 prompt：

```text
Use the supplied ShangK private-room scene as the exact background. Create a premium vertical commercial first frame for a high-end KTV/private club short video. Add one fictional adult AI female commercial lead inside the room, beautiful and elegant, confident nightlife host temperament, refined black evening outfit, natural face, normal hands, normal body proportions, standing or leaning naturally near the sofa/table area without blocking the key room features. Preserve the room layout, sofa, table, microphone, bottles, screen, neon wall lines, glossy floor reflections, dark luxury lighting, camera perspective, and 9:16 composition. The image should look like a polished Douyin commercial opening frame, not a selfie, not a collage, not a real-person cutout.
```

视频 prompt：

```text
Keep the approved AI female lead identity and the ShangK KTV room unchanged. Generate a stable vertical commercial short-video shot with a premium nightlife advertising feel. The subject reacts naturally to the reference audio, with subtle body turn, elegant shoulder movement, small hand gesture, slight head movement, confident gaze, and controlled camera-like motion. Preserve facial beauty, outfit, sofa, table, microphone, bottles, screen, neon lines, glossy reflections, and the original 9:16 framing. The shot should feel like a usable commercial scene segment, not only a static talking head.
```

产物：

```text
首图：
E:\ComfyUI_cu130\ComfyUI\output\商k\首图生成\shangk_first_frame_00001_.png

原始生成视频：
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\shangk_final_video_00001-audio.mp4

1080x1920 交付封装版：
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\shangk_final_video_1080x1920_delivery.mp4
```

交付版参数：

```json
{
  "width": 1080,
  "height": 1920,
  "fps": 24,
  "frames": 369,
  "duration_seconds": 15.375,
  "size_bytes": 5670619
}
```

报告文件：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_full_pipeline\shangk_full_pipeline_current_report.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_full_pipeline\shangk_full_pipeline_current_contact.jpg
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_full_pipeline\shangk_full_pipeline_current_delivery_contact.jpg
```

本轮还修复了 materializer 的一个真实问题：ComfyUI `object_info` 对 `LoadImage.image` 返回空动态列表时，之前会误判子目录图片路径非法，导致 `商k/场景/...png` 无法进入 API prompt。现在空动态列表会接受字符串文件名，支持 ComfyUI input 子目录素材。

质检结论：

1. 链路已完整跑通：参考视频抽音频 -> 场景替换首图 -> 数字人视频 -> 1080x1920 交付封装。
2. 首图质量可用，人物是 AI 虚拟女性，场景来自 `商k\场景`，没有使用真人抠图。
3. 视频抽帧显示人物、场景稳定，有手势和姿态变化，能作为当前阶段的商K项目样片。
4. 局限：InfiniteTalk 仍更适合“人物主导的商业镜头”，不是完整多镜头广告片；后续若要接近成熟抖音商业视频，需要加入镜头拆分、B-roll、转场、字幕和平台文案后期。

## 17. 参考视频动作分析纠偏

用户指出上一轮没有真正分析 `商k\视频参考` 内参考视频的视觉内容。该反馈成立：上一轮脚本只抽取了参考视频音频，没有把参考视频中的人物姿态、动作、道具、镜头感作为主约束，因此产物偏向音频驱动的坐姿人物镜头，不符合参考视频的核心视觉结构。

参考视频抽帧：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_full_pipeline\reference_video_contact_1fps.jpg
```

参考视频视觉要点：

1. 人物是站立姿态，不是坐姿。
2. 女生手持话筒，动作围绕唱歌/演唱展开。
3. 有轻微跳舞和肢体摆动，包括抬手、转身、摆胯、换重心。
4. 镜头是竖版全身/大半身舞台镜头，人物正对镜头，有表演感和镜头感。
5. 视频自带字幕，属于抖音/KTV 表演类短视频风格。

因此，正确的视频路由不应只走：

```text
Qwen 首图 -> InfiniteTalk 音频驱动
```

而应改成：

```text
参考视频视觉分析
-> 站立持麦虚拟女生首图
-> Wan2.2 Animate / 动作迁移 / 人物替换类 workflow
-> 保留或重建商K场景
-> 再进入字幕、音乐、封面、发布文案后期
```

本地可用的动作迁移候选包括：

```text
Wan2.2_Animate_SAM3_人物遮罩替换(15秒长视频).json
Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json
Wan2.2_Animate_SAM3_人物遮罩替换.json
Wan2.2_Animate_人物遮罩替换(KJ版).json
Wan2.2_Animate_MatAnyone2遮罩-人物迁移-动作迁移-长视频循环(KJ流).json
```

其中 `Wan2.2_Animate_SAM3_人物遮罩替换(15秒长视频).json` 与 `Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json` 更接近当前参考视频，因为它们显式包含视频加载、人物分割、姿态/面部检测、背景/人物遮罩、WanAnimate 生成与视频合成节点。

工程纠偏：

1. `run_shangk_full_pipeline.py` 当前产物应标注为“音频驱动商K样片”，不能标注为“参考动作复刻成片”。
2. 下一版脚本必须先生成 `reference_video_analysis`，至少包含站立/持麦/唱跳/镜头感/字幕/时长/帧率/主体位置。
3. 首图 prompt 必须明确“站立、手持话筒、舞台/商K镜头、全身或大半身”，不能让模型自然选择坐姿。
4. 视频 workflow 应优先路由到 Wan2.2 Animate 动作迁移类；InfiniteTalk 只作为需要口型/轻动作时的备选。
5. 如果要求“替换为商K场景”，动作迁移阶段还需要验证背景来源：有些人物替换流会保留参考视频背景，有些流可接入目标首图/背景视频。正式成片前必须把背景是否来自 `商k\场景` 作为质检项。

## 16. 15 秒唱歌跳舞视频 smoke

本轮用户明确要求生成一个 15 秒“人物在场景中唱歌跳舞”的视频。该目标不再按口播理解，而是按音乐唱跳镜头处理。

实现路线：

```text
全身 KTV 首帧 -> 原创 15 秒舞曲/合成唱声 -> InfiniteTalk 提示词调度动作控制 -> 15 秒 mp4
```

本轮没有下载版权不明音乐，而是在本地生成一段 15 秒原创合成舞曲，写入 ComfyUI input：

```text
E:\ComfyUI_cu130\ComfyUI\input\aiops_original_dance_song_15s.wav
```

首帧使用更适合全身唱跳的 KTV 虚拟女性图：

```text
E:\ComfyUI_cu130\ComfyUI\input\scene_ai_virtual_host_seed.png
```

使用 workflow：

```text
E:\ComfyUI_cu130\ComfyUI\user\default\workflows\5-数字人：图像语音对口型-唱歌-带货-对话\Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json
```

本轮实际提交 prompt：

```text
A fictional adult East Asian AI female singer-dancer performs a lively KTV dance-pop stage routine inside the same neon private room. She sings toward the camera with visible mouth movement while dancing to the beat: rhythmic body sway, step-touch footwork, shoulder turns, elegant arm waves, small hip movement, brief hand flourish, confident stage presence, full-body vertical framing, glossy black evening dress moving naturally. Preserve her face identity, beauty, outfit, body proportions, the KTV room layout, sofa, table, wall screens, neon reflections, blue and magenta lighting, and camera perspective. The camera stays mostly stable with a slight music-video push-in; energetic commercial KTV atmosphere, no scene change.
```

负面 prompt：

```text
static person, only talking, no dancing, distorted face, asymmetrical eyes, bad hands, extra fingers, extra limbs, broken body, broken legs, foot sliding, body melting, face identity drift, changed room layout, duplicated people, childlike appearance, real person cutout, watermark, subtitles, QR code, severe flicker, low quality, blurry, cropped head, cropped feet, camera jump, disfigured body, plastic skin
```

首次提交被资源门控拦截：360 帧任务需要约 15.7GB 可用显存，当时只有约 13.4GB。确认队列为空后调用 ComfyUI `/free` 释放已加载模型，显存恢复到约 32.2GB，再提交成功。

最终输出：

```json
{
  "status": "success",
  "video_prompt_id": "4f294a51-42ab-4837-921a-aeae5147415f",
  "video": "E:\\ComfyUI_cu130\\ComfyUI\\output\\aiops\\original_douyin_requirement_15s_sing_dance_smoke\\digital_human_sing_dance_i2v\\Wan2.1_I2V_InfiniteTalk_sing_dance_15s_00001-audio.mp4",
  "width": 368,
  "height": 640,
  "requested_frames": 360,
  "frames": 369,
  "fps": 24,
  "duration_seconds": 15.375
}
```

记录文件：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_15s_sing_dance_smoke_preflight.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_15s_sing_dance_smoke_submit.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_15s_sing_dance_smoke_history.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_15s_sing_dance_smoke_result.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\original_douyin_requirement_15s_sing_dance_smoke_contact.jpg
```

质检结论：

1. 15 秒视频已真实产出，音频、口型、人物轻舞蹈动作和 KTV 场景都存在。
2. 这是“无动作参考的视频 prompt 驱动唱跳 smoke”，动作以手臂、肩部、身体轻摆为主。
3. 如果目标是强舞蹈、抖音编舞或大幅动作，下一步应切换到 `Wan2.2 Animate`、`SteadyDancer` 或 `OneToAll/SCAIL`，并提供/生成舞蹈参考视频或姿态序列。
