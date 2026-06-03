# ComfyUI_cu130 工作流说明书

更新日期：2026-05-28

本文档基于 `E:\ComfyUI_cu130\ComfyUI\user\default\workflows` 下已导入的工作流整理。模型下载完成后，运行时审计共识别 114 个 JSON 工作流，分为基础处理、语音、音乐、图像生成/图像编辑、图生视频、数字人口型、动作迁移七大类。完整自动审计见 `docs/COMFYUI_CU130_RUNTIME_MODEL_AUDIT.md`。

本文档定位为 RAG 知识文档，只描述每个 ComfyUI 工作流的能力、输入输出、依赖和适用项目。它不绑定 KTV 单一项目，也不承担具体客户执行方案。Agent 后续应通过检索本文档，自动判断某个运营任务应该选择哪个工作流。

新工程的插件生态已经比较完整：`WanVideoWrapper`、`WanAnimatePreprocess`、`IPAdapter`、`SAM2/SAM3`、`KJNodes`、`controlnet_aux`、`InfiniteTalk`、`VideoHelperSuite`、`Qwen/TTS/ASR`、补帧和放大工具都已存在。当前模型库已经完成主体下载，按可执行模型文件口径约 340 个、约 950GB。仍需区分两件事：模型存在不等于工作流已跑通；每个主线工作流还需要用目标素材做最小运行验证。

## Agent 选择原则

针对任意商业运营项目，Agent 不应直接写节点，而应先判断任务类型，再选择工作流：

1. 视频解析/素材理解：选择截帧、ASR、Image2Prompt、QwenVL、SAM、Depth 等基础处理流。
2. 数字人口播：选择 `InfiniteTalk`、`S2V`、音频驱动口型类工作流。
3. 人物替换/动作迁移：选择 `Wan2.2 Animate`、SAM2/SAM3、KJ 长视频流。
4. 图生视频/补充镜头：选择 Hunyuan、Wan I2V、单图/多图视频工作流。
5. 声音/BGM：选择 Qwen TTS、Index TTS、LongCat TTS、ACE-Step、HeartMula。
6. 发布前处理：选择分屏对比、视频合并、音频分离、转码、放大、补帧工具流。

如果项目是商 K/KTV 数字人视频，优先验证顺序可为：

1. `Wan2.2_Animate_SAM3_人物遮罩替换.json`
2. `Wan2.2_Animate_人物遮罩替换(KJ版).json`
3. `Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json`
4. `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json`

## 关键模型

这些是高频工作流常见依赖。当前审计已能在模型目录中看到主体模型或等价模型，下一步是运行验证：

- `Wan\Wan2.2_Animate_14B_Q6_K.gguf`
- `Wan\Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors`
- `Wan\Wan2.2-Fun-A14B-InP-Fusion-Elite.safetensors`
- `Wan\WAN22_MoCap_fullbodyCOPY_ED.safetensors`
- `Wan\FullDynamic_Ultimate_Fusion_Elite.safetensors`
- `Wan\lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`
- `Wan2_1_VAE_bf16.safetensors`
- `clip_vision_h.safetensors`
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- `umt5-xxl-enc-fp8_e4m3fn.safetensors`
- `sam3.pt` / `sam3.1_multiplex_fp16.safetensors`
- `sam2_hiera_base_plus.safetensors`
- `vitpose_h_wholebody_model.onnx`
- `yolov10m.onnx`
- `wav2vec2-chinese-base_fp16.safetensors`
- `Wan2_1-InfiniTetalk-Single_fp16.safetensors`

## 0. 基础处理

这些工作流不是最终成片主流程，但会在数字人视频生产里频繁使用。

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `birefnet_图像移除背景.json` | 用 BiRefNet 做图像主体抠图/去背景。 | 图片 | 透明图、遮罩预览 | 适合人物参考图清理、素材抠图。 |
| `ControlNet_aux_常用样例.json` | ControlNet 预处理示例，主要生成深度、姿态等控制图。 | 图片 | 控制图/预览图 | 可为后续动作、空间约束提供控制输入。 |
| `MatAnyone2_视频遮罩.json` | 视频遮罩分割，偏人物/主体视频遮罩。 | 视频 | 遮罩视频、预览视频 | 适合人物替换前的主体分离。 |
| `sam3_图像视频-提示词遮罩分割.json` | 通过文本提示词做 SAM3 图像/视频分割。 | 图片或视频、提示词 | 遮罩、带透明通道结果 | 适合快速找出人物、桌子、沙发等区域。 |
| `sam3_图像视频_通过点遮罩分割.json` | 通过点选方式做 SAM3 图像/视频分割。 | 图片或视频、点选区域 | 遮罩、分割预览 | 适合人工精修人物或场景区域。 |
| `utility-depthAnything-v2-relative-video-深度图.json` | 用 DepthAnything V2 生成视频深度图。 | 视频 | 深度视频 | 可辅助空间感、景深、动作控制。 |
| `utility-lineart-video-线稿转换.json` | 视频转线稿。 | 视频 | 线稿视频 | 更偏风格化或 ControlNet 线稿控制。 |
| `加载图片合成视频.json` | 把图片序列或图片素材合成视频。 | 图片/图片序列 | 视频 | 用于静态素材快速生成预览视频。 |
| `加载本地latent解码.json` | 读取本地 latent 并用 VAE 解码。 | latent | 图片/视频帧 | 调试或恢复中间结果。 |
| `双图像或视频合并显示.json` | 两路图片/视频并排合并预览。 | 图片或视频 | 对比视频/图 | 适合前后效果对比。 |
| `图像嵌入文字描述.json` | 将图片和文字说明组合展示。 | 图片、文本 | 带说明图 | 适合整理素材或报告图。 |
| `多视频合成分屏展示.json` | 多视频拼成分屏。 | 多个视频 | 分屏视频 | 适合多候选结果横评。 |
| `截取视频每一帧.json` | 把视频拆成帧。 | 视频 | 帧图片 | 用于动作参考、质检、抽关键帧。 |
| `手动按分镜视频截取.json` | 按分镜手动截取视频片段。 | 视频、时间段 | 分镜片段/图片/音频 | 适合从参考视频中取动作或镜头。 |
| `视频-音频分离.json` | 从视频中分离音频。 | 视频 | 音频 | 适合提取口播、BGM、参考音频。 |
| `视频倒放.json` | 视频倒放。 | 视频 | 倒放视频 | 辅助工具。 |
| `视频转gif动图图片.json` | 视频转 GIF 或动图。 | 视频 | GIF/动图 | 适合预览和快速分享。 |
| `音频人声分离.json` | 人声/伴奏分离。 | 音频 | 人声、伴奏 | 适合保留口播、替换 BGM。 |
| `音频转MP3格式.json` | 音频格式转换。 | 音频 | MP3 | 交付和兼容处理。 |

## 1. 语音生成

这些工作流负责旁白、配音、字幕和音色克隆。

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `index-TTS2-情绪控制-音频参考-文本控制-克隆-多人对话.json` | Index-TTS2 情绪和音色控制，支持参考音频和多人对话。 | 文本、参考音频 | 语音 | 适合生成正式口播，但需听感筛选。 |
| `LongCat-AudioDIT-TTS-音色克隆-对人对话.json` | LongCat TTS 音色克隆和对话生成。 | 文本、参考音频 | 语音 | 可做多角色对话型短视频。 |
| `Qwen3-ASR-Subtitle语音转字幕.json` | 语音转字幕。 | 音频/视频音频 | 字幕文本 | 用于自动字幕和口播校对。 |
| `Qwen3-ASR-语音转文字.json` | 语音识别转文字。 | 音频 | 文本 | 用于提取参考视频文案。 |
| `Qwen3-TTS_多角色对话.json` | Qwen3 TTS 多角色对话。 | 多角色台词 | 多段语音 | 适合剧情化介绍。 |
| `Qwen3-TTS_语音设计+语音克隆.json` | Qwen3 TTS 音色设计和克隆。 | 文本、音色描述/参考 | 语音 | 适合建立固定虚拟主持人音色。 |

## 2. 音乐生成

这些工作流适合补充 BGM 或歌曲类内容。

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `ace_step1_5_xl_sft_50Step高质量音乐生成.json` | ACE-Step 高质量音乐生成。 | 歌词/风格提示 | 音乐 | 质量优先，速度较慢。 |
| `ace_step1_5_xl_turbo_8Step极速音乐生成.json` | ACE-Step 快速音乐生成。 | 歌词/风格提示 | 音乐 | 适合快速预览。 |
| `ace_step_1.5+Qwen3.5_自动歌词音乐生成.json` | Qwen 生成歌词，再用 ACE-Step 生成音乐。 | 主题/风格 | 歌词、音乐 | 适合一键生成商 K 宣传 BGM 或歌曲。 |
| `HeartMula_生成音乐.json` | HeartMula 音乐生成。 | 音乐提示词 | 音乐 | 可作为备选 BGM 路线。 |

## 3. 图像生成：文生图、图像编辑、角色/商品图

模型完成后，该分类当前新增为最大的一组，共 40 个工作流，主要覆盖 Qwen-Image、Z-Image、Flux2 Klein、ERNIE/Firered 图像编辑、局部重绘、服装/商品迁移、角色多视角、漫画转真人、姿势控制和提示词反推。

对全局项目的价值：

- 生成“虚拟美女主持人”首帧或参考图，而不是从外部找人物照片。
- 生成商 K、门店、本地生活、电商等项目所需的封面、KV、分镜首帧、商品图和人物多视角参考。
- 给后续 `Wan I2V`、`InfiniteTalk`、`WanAnimate` 提供更稳定的角色图、场景图和遮罩前素材。

这 40 个图像工作流没有在本文逐个手写展开，原因是它们更适合作为 RAG 自动选流知识。当前已生成完整 RAG 条目：

```text
deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl
```

Agent 选流时，应优先按能力标签检索：`image_generation`、`segmentation`、`vlm_prompting`、`motion_transfer`，再结合项目目标判断是否作为视频主流程前置素材生成步骤。

## 4. 视频生成

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `HunYuan-Video-1.5-AIO_图生视频.json` | 通用图生视频。 | 单图/提示词 | 视频 | 可生成补充镜头，但不是人物替换主线。 |

## 5. 数字人：口型、唱歌、带货、对话

这些工作流主要解决“图片/视频人物 + 音频 = 会说话/唱歌的数字人”。

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `Wan2.1_I2V_InfiniteTalk_rCM_数字人对口型多动态(KJ版).json` | KJ 版 InfiniteTalk，多动态口型视频。 | 人物图、音频、提示词 | 口型视频 | 适合口播/带货短视频。 |
| `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json` | 图生视频数字人，音频驱动口型，并可用提示词调度动作。 | 人物图、音频、提示词 | 口型+动作视频 | 推荐用于虚拟美女主持人口播。 |
| `Wan2.1_infinitetalk_音频驱动的全身视频配音-单人(官流).json` | 官方单人全身音频驱动口型。 | 人物图、音频 | 单人口型视频 | 更标准，适合单人主播。 |
| `Wan2.1_infinitetalk_音频驱动视频配音-单人for循环长视频(官流).json` | 官方单人长视频循环版本。 | 人物图、音频 | 长口型视频 | 适合较长讲解。 |
| `Wan2.1_infinitetalk_音频驱动视频配音-双人for循环长视频(官流).json` | 官方双人长视频口型。 | 双人物图、音频 | 双人口型视频 | 暂不是本项目主线。 |
| `Wan2.1_V2V_InfiniteTalk_视频对口型(KJ流).json` | 视频到视频口型驱动。 | 原视频、音频 | 新口型视频 | 当已有人物视频时使用。 |
| `Wan2.2-s2v视频对口型.json` | Wan2.2 S2V 视频对口型。 | 视频/音频 | 口型视频 | 可作为 InfiniteTalk 的备选。 |

## 6. 动作迁移：人物替换、动作模仿

这是与“抖音视频同类效果”最相关的一组。核心逻辑通常是：参考人物图 + 动作视频 + 人物遮罩/姿态/脸部条件 + WanAnimate = 新人物动作视频。

| 工作流 | 作用 | 输入 | 输出 | 项目价值 |
|---|---|---|---|---|
| `Wan2.1_OneToAll_人物姿势控制.json` | OneToAll 姿势控制。 | 参考人物、姿态/动作 | 姿势控制视频 | 可做单人姿态迁移。 |
| `Wan2.1_OneToAll_人物姿势控制单人20s(KJ版).json` | KJ 版单人 20 秒姿势控制。 | 参考人物、动作 | 20 秒视频 | 适合较长单人动作预览。 |
| `Wan2.1_SCAIL_人物姿势控制 (20s).json` | SCAIL 20 秒姿势控制。 | 参考人物、姿态 | 20 秒视频 | 备选动作控制路线。 |
| `Wan2.1_SCAIL_人物姿势控制.json` | SCAIL 标准姿势控制。 | 参考人物、姿态 | 视频 | 备选动作控制路线。 |
| `Wan2.1_SCAIL_单人多人动作迁移-Q版动漫人物宠物.json` | 支持单人/多人/动漫/宠物动作迁移。 | 多类型参考、动作 | 视频 | 偏泛化，不是商 K 真人主线。 |
| `Wan2.1_SteadDancer_动作迁移（支持动漫人GGUF版).json` | SteadDancer 动作迁移。 | 参考人物、舞蹈动作 | 动作视频 | 适合舞蹈/大幅动作。 |
| `Wan2.2_Animate_MatAnyone2遮罩-人物迁移-动作迁移-长视频循环(KJ流).json` | MatAnyone2 遮罩 + Wan2.2 Animate 长视频 KJ 流。 | 参考人物、动作视频、遮罩 | 长动作迁移视频 | 高价值，适合成熟主线。 |
| `Wan2.2_Animate_onnx_人物遮罩替换.json` | ONNX 姿态/检测 + Wan2.2 Animate 人物遮罩替换。 | 参考人物、动作视频 | 人物替换视频 | 高价值，依赖 ONNX 检测模型。 |
| `Wan2.2_Animate_SAM2_人物替换.json` | SAM2 人物分割 + Wan2.2 Animate。 | 参考人物、动作视频 | 人物替换视频 | SAM3 未就绪时的推荐备选。 |
| `Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json` | SAM3 + Wan2.2 Animate 长视频 KJ 流。 | 参考人物、动作视频、SAM3 遮罩 | 长动作迁移视频 | 最接近成熟批量生产路线。 |
| `Wan2.2_Animate_SAM3_人物遮罩替换(15秒长视频).json` | SAM3 人物遮罩替换，15 秒长视频版。 | 参考人物、动作视频 | 15 秒视频 | 适合抖音短视频段落。 |
| `Wan2.2_Animate_SAM3_人物遮罩替换.json` | SAM3 人物遮罩替换标准版。 | 参考人物、动作视频 | 人物替换视频 | 推荐第一优先验证。 |
| `Wan2.2_Animate_Sec_人物迁移_动作迁移_长视频循环(KJ流).json` | SeC 分割 + Wan2.2 Animate 长视频 KJ 流。 | 参考人物、动作视频 | 长动作迁移视频 | SAM 路线不稳时的备选分割路线。 |
| `Wan2.2_Animate_人物遮罩替换(KJ版).json` | KJ 整理版 Wan2.2 Animate 人物遮罩替换。 | 参考人物、动作视频、遮罩 | 人物替换视频 | 推荐主线之一，节点结构更适合本机环境。 |
| `Wan2.2_Animate_人物遮罩替换(官流).json` | ComfyOrg 官方 Wan2.2 Animate 人物遮罩替换。 | 参考人物、动作视频 | 人物替换视频 | 标准官方路线，适合对照验证。 |
| `Wan2.2_Animate_人物遮罩替换(官流整理).json` | 官方工作流整理版。 | 参考人物、动作视频 | 人物替换视频 | 比原官流更便于阅读和修改。 |

## 对当前项目的实际用法

如果目标是“像抖音示例一样，从商 K 场景/人物参考做数字人视频”，建议这样组合：

1. 用 `sam3_图像视频_通过点遮罩分割.json` 或 `MatAnyone2_视频遮罩.json` 准备遮罩。
2. 用 `Wan2.2_Animate_SAM3_人物遮罩替换.json` 做第一版人物替换。
3. 如果需要更长镜头，换 `Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json`。
4. 如果要数字人口播，接 `Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json`。
5. 用基础处理里的截帧、分屏、音频分离、MP3 转换工作流做质检和交付。

## 后续验证 checklist

- 打开推荐主线 workflow，确认所有红色缺失节点消失。
- 确认模型下拉框里能看到关键模型。
- 用一张高质量虚拟美女参考图和一个短动作视频先跑 3-5 秒。
- 通过后再替换成商 K 场景素材和正式动作参考。
- 对每次输出保存 contact sheet，检查脸、手、脚、服装、遮罩边缘和场景融合。
