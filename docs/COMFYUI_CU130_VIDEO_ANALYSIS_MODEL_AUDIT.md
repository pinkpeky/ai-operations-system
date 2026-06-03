# ComfyUI_cu130 视频解析能力与模型状态核查

更新日期：2026-05-28

本文档记录 `E:\ComfyUI_cu130\ComfyUI` 在模型下载完成后的真实核查结果。旧结论“模型目录基本为空”已失效。

## 当前结论

ComfyUI_cu130 当前已经具备视频解析最小闭环所需的模型与节点基础：

- 视频读取/截帧：可用。
- ASR 语音转文字：Qwen3-ASR 与 Whisper 模型均已存在，可进入最小运行验证。
- 关键帧视觉理解：QwenVL / OllamaVision / SmolVLM / JoyCaption 相关节点存在，`qwen_2.5_vl_7b_fp8_scaled.safetensors`、Qwen3.5 GGUF 与 mmproj 模型存在，可进入最小运行验证。
- 主体/人物分割：SAM2、SAM3、基础 SAM、人物检测/分割模型存在，可进入最小运行验证。
- 深度/空间理解：DepthAnything V2 模型和节点存在，可进入最小运行验证。
- OCR：未发现明确 PaddleOCR/RapidOCR/EasyOCR 类节点与模型，不应把 ComfyUI 作为 OCR 主能力。

因此：当前可以说“ComfyUI_cu130 具备视频解析最小验证条件”，但还不能说“每个视频解析工作流都已通过运行验证”。下一步必须用本地短视频跑最小链路。

## 运行时状态

当前 API：

```text
http://127.0.0.1:8188
```

运行时信息：

- ComfyUI version: `0.21.1`
- PyTorch: `2.9.1+cu130`
- GPU: `NVIDIA GeForce RTX 5090`
- Queue running: `0`
- Queue pending: `0`

完整模型/节点/工作流审计见：

- `docs/COMFYUI_CU130_RUNTIME_MODEL_AUDIT.md`
- `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_model_audit.json`
- `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl`

## 视频解析能力矩阵

| 能力 | 节点状态 | 模型状态 | 结论 |
|---|---|---|---|
| 视频读取/截帧 | `LoadVideo`、`VHS_LoadVideo` 等存在 | 不依赖大模型 | 可验证 |
| ASR 语音转文字 | `Qwen3ASRTranscriber`、`AILab_Qwen3ASR`、Whisper 节点存在 | `Qwen3-ASR`、`whisper` 模型存在 | 可验证 |
| 关键帧视觉理解 | QwenVL、OllamaVision、SmolVLM、JoyCaption 节点存在 | QwenVL/Qwen3.5 相关模型存在 | 可验证 |
| 主体/人物分割 | SAM2/SAM3/SAM 节点存在 | SAM2、SAM3、SAM、YOLO/person-seg 模型存在 | 可验证 |
| 深度/空间理解 | DepthAnything / VideoDepthAnything 节点存在 | DepthAnything V2 模型存在 | 可验证 |
| OCR 文字识别 | 未确认明确 OCR 节点 | 未确认 OCR 模型 | 不作为主能力 |
| Wan/数字人生成 | WanVideo、WanAnimate、InfiniteTalk 生态存在 | Wan2.1/Wan2.2/InfiniteTalk/S2V 模型存在 | 模型具备，需生成验证 |

## 对系统架构的判断

视频解析仍不建议完全绑定在 ComfyUI 内部。更稳的生产架构是：

1. 独立视频解析服务负责标准化 `VideoAnalysisResult`：ffmpeg 抽帧、提音频、ASR、OCR/VLM、LLM 汇总。
2. ComfyUI 作为强生成工具，同时作为可选解析工具：当 QwenVL/ASR/SAM/Depth 工作流跑通时可调用。
3. 主 agent 只消费统一的 `VideoAnalysisResult`，不关心结果来自 ComfyUI、OllamaVision、QwenVL、Whisper 还是其他服务。

这样 ComfyUI 节点失效、显存不足、某个工作流不兼容时，不会阻塞整个商业运营闭环。

## 最小验证顺序

不要直接跑 15 秒或长视频大工作流。建议按下面顺序验证：

1. `LoadVideo` / VideoHelperSuite：读取一段 3-5 秒本地视频并抽帧。
2. Qwen3-ASR 或 Whisper：把同一视频音频转成文本。
3. QwenVL / OllamaVision / JoyCaption：对 3-5 张关键帧输出画面描述。
4. SAM3/SAM2：对人物或主要物体生成 mask。
5. DepthAnything：生成深度图。
6. 将以上结果合并为 `VideoAnalysisResult` JSON，交给主 agent 做脚本编排和 ComfyUI 工作流选择。

只有第 1-3 步跑通，才可以说“视频解析最小闭环已具备”；第 4-5 步属于增强理解和后续生成辅助。
