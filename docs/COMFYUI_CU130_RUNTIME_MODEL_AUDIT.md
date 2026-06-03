# ComfyUI_cu130 Runtime Model Audit

Generated at: `2026-05-28T10:54:38`

## Runtime

- ComfyUI root: `E:\ComfyUI_cu130\ComfyUI`
- Base URL: `http://127.0.0.1:8188`
- Queue running: `0`
- Queue pending: `0`
- ComfyUI version: `0.21.1`
- PyTorch: `2.9.1+cu130`

## Models

- Model file count: `341`
- Total model size: `950.47 GB`

| Directory | Files | Size |
|---|---:|---:|
| `diffusion_models` | 47 | 534.99 GB |
| `text_encoders` | 17 | 111.66 GB |
| `loras` | 94 | 69.13 GB |
| `checkpoints` | 3 | 21.29 GB |
| `HeartMuLa` | 6 | 20.85 GB |
| `model_patches` | 4 | 17.68 GB |
| `controlnet` | 15 | 14.45 GB |
| `audiodit` | 2 | 14.29 GB |
| `IndexTTS-2` | 14 | 13.5 GB |
| `clip_vision` | 6 | 13.11 GB |
| `Qwen3-TTS-Models` | 6 | 12.64 GB |
| `SDPose_OOD` | 10 | 9.87 GB |
| `LLM` | 2 | 9.73 GB |
| `inpaint` | 15 | 9.41 GB |
| `whisper` | 3 | 8.63 GB |
| `SEEDVR2` | 3 | 8.06 GB |
| `Qwen3-ASR` | 4 | 7.83 GB |
| `sams` | 3 | 6.71 GB |
| `sam3` | 2 | 6.48 GB |
| `diffusers` | 4 | 6.46 GB |
| `detection` | 7 | 6.01 GB |
| `vae` | 14 | 5.54 GB |
| `clip` | 2 | 4.79 GB |
| `stt` | 2 | 4.38 GB |
| `rembg` | 5 | 3.21 GB |
| `annotator` | 7 | 1.86 GB |
| `wav2vec2` | 4 | 1.47 GB |
| `transformers` | 2 | 1.24 GB |
| `latent_upscale_models` | 1 | 0.93 GB |
| `grounding-dino` | 1 | 0.87 GB |
| `onnx` | 5 | 0.84 GB |
| `depthanything` | 1 | 0.62 GB |
| `sam2` | 2 | 0.45 GB |
| `background_removal` | 1 | 0.41 GB |
| `ESRGAN` | 4 | 0.25 GB |
| `ultralytics` | 10 | 0.24 GB |
| `lama` | 1 | 0.19 GB |
| `upscale_models` | 3 | 0.19 GB |
| `yolo` | 2 | 0.11 GB |
| `RealESRGAN` | 2 | 0.08 GB |

## Video Analysis Capability Matrix

| Capability | Nodes | Models | Conclusion |
|---|---|---|---|
| `video_frame_extraction` | yes | yes | `ready_for_minimal_validation` |
| `asr_audio_to_text` | yes | yes | `ready_for_minimal_validation` |
| `vlm_keyframe_understanding` | yes | yes | `ready_for_minimal_validation` |
| `subject_segmentation` | yes | yes | `ready_for_minimal_validation` |
| `depth_spatial_analysis` | yes | yes | `ready_for_minimal_validation` |
| `ocr_screen_text` | no | no | `not_a_primary_comfyui_capability` |
| `wan_digital_human_generation` | yes | yes | `models_present_but_requires_generation_validation` |

## Workflow Inventory

- Workflow count: `114`

### By Category

- 0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印: 19
- 1-语音生成：音声设计-克隆-多人对话: 6
- 2-音乐生成：歌词生成音乐: 4
- 3-图像生成：文生图-图像编辑: 40
- 4-视频生成：单图-双图-多图: 22
- 5-数字人：图像语音对口型-唱歌-带货-对话: 7
- 6-动作迁移：人物替换-动作模仿迁移: 16

### By Capability

- asr: 2
- digital_human: 10
- general: 3
- image_generation: 40
- image_to_video: 16
- motion_transfer: 19
- music: 4
- post_processing: 21
- segmentation: 15
- tts: 6
- video_analysis: 22
- vlm_prompting: 2

## Operational Conclusion

- The model download is now materially complete for the current ComfyUI_cu130 bundle.
- Minimal video analysis can be validated with frame extraction, ASR, VLM/keyframe captioning, segmentation, and depth workflows.
- OCR is still not a primary ComfyUI capability in this runtime; use an independent OCR/video-analysis service when screen text matters.
- Digital-human and WanAnimate workflows have model coverage, but they still require controlled generation validation before production use.
- Agent workflow selection should use this audit as capability evidence, not as proof that every workflow has passed prompt execution.

## High-Value Workflow Status

| Workflow | Capabilities | Node Status | Model refs found/missing |
|---|---|---|---:|
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/birefnet_图像移除背景.json` | video_analysis, segmentation, post_processing | `ok` | 1/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/ControlNet_aux_常用样例.json` | video_analysis, post_processing | `ok` | 0/1 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/MatAnyone2_视频遮罩.json` | video_analysis, segmentation, post_processing | `ok` | 1/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/sam3_图像视频-提示词遮罩分割.json` | video_analysis, segmentation, post_processing | `ok` | 0/1 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/sam3_图像视频_通过点遮罩分割.json` | video_analysis, segmentation, post_processing | `ok` | 1/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/utility-depthAnything-v2-relative-video-深度图.json` | video_analysis, post_processing | `ok` | 1/1 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/utility-lineart-video-线稿转换.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/加载图片合成视频.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/加载本地latent解码.json` | video_analysis, post_processing | `ok` | 1/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/双图像或视频合并显示.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/图像嵌入文字描述.json` | video_analysis, vlm_prompting, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/多视频合成分屏展示.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/截取视频每一帧.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/手动按分镜视频截取.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/视频-音频分离.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/视频倒放.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/视频转gif动图图片.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/音频人声分离.json` | video_analysis, post_processing | `ok` | 0/0 |
| `0-基础处理：图像合并-音频分离-视频截取合并-图像视频放大-去水印/音频转MP3格式.json` | video_analysis, post_processing | `ok` | 0/0 |
| `1-语音生成：音声设计-克隆-多人对话/Qwen3-ASR-Subtitle语音转字幕.json` | video_analysis, asr, tts | `ok` | 0/0 |
| `1-语音生成：音声设计-克隆-多人对话/Qwen3-ASR-语音转文字.json` | video_analysis, asr, tts | `ok` | 0/0 |
| `3-图像生成：文生图-图像编辑/Qwen/Qwan-Image-Edit+SAM3_人物图像遮罩替换.json` | image_generation, segmentation | `ok` | 7/0 |
| `3-图像生成：文生图-图像编辑/Qwen/Qwan-Image-Edit+SAM3_服装遮罩替换.json` | image_generation, segmentation | `ok` | 7/0 |
| `3-图像生成：文生图-图像编辑/Qwen/Qwen-Image-Edit_人物百搭秀与终极姿势控制(GGUF).json` | image_generation, motion_transfer | `ok` | 6/1 |
| `3-图像生成：文生图-图像编辑/Z-Image/Z-Image+Qwen3.5提示词反推_文生图.json` | vlm_prompting, image_generation | `ok` | 6/0 |
| `3-图像生成：文生图-图像编辑/Z-Image/Z-Image-Tubro_人物姿势控制.json` | image_generation, motion_transfer | `ok` | 4/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/HunYuan-Video-1.5-AIO_图生视频.json` | image_to_video | `ok` | 4/0 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX-2.3-文生视频数字人.json` | digital_human | `ok` | 8/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX2.3-图生视频-双人对话(KJ优化版) .json` | image_to_video | `ok` | 8/1 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX2.3-图生视频-双人对话-宠物对话(KJ优化版) .json` | image_to_video | `ok` | 8/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX2.3-音频数字人(单采样极速版).json` | digital_human | `ok` | 12/1 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX2.3-音频数字人(双采样高清版) .json` | digital_human | `ok` | 11/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX_2.3-动作迁移双重控制.json` | motion_transfer | `ok` | 13/3 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX_2.3_flf2v_lora专场优化_首尾帧图生视频(官流).json` | image_to_video | `ok` | 9/1 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX_2.3_flf2v_Lora转场优化_多帧帧图生视频(kj节点) .json` | image_to_video | `ok` | 8/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/LTX2.3/LTX_2.3_i2v_图生视频(官流).json` | image_to_video | `ok` | 9/4 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.1_I2V_图生视频(官流).json` | image_to_video | `ok` | 6/1 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_FMLF_多帧首尾帧.json` | image_to_video | `ok` | 10/0 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_REMIX_PainterI2V_图生视频动态加强.json` | image_to_video | `ok` | 7/0 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_REMIX_首尾帧.json` | image_to_video | `missing executable node` | 10/1 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_图生视频(官方模板).json` | image_to_video | `ok` | 11/2 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_图生视频(官流GGUF版).json` | image_to_video | `ok` | 11/0 |
| `4-视频生成：单图-双图-多图/4-视频生成：单图-双图-多图/Wan2.2/Wan2.2_I2V_首尾帧 (GGUF版).json` | image_to_video | `missing executable node` | 10/1 |
| `4-视频生成：单图-双图-多图/HunYuan-Video-1.5-AIO_图生视频.json` | image_to_video | `ok` | 4/0 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_I2V_InfiniteTalk_rCM_数字人对口型多动态(KJ版).json` | image_to_video, digital_human | `ok` | 9/1 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json` | image_to_video, digital_human | `ok` | 7/0 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_infinitetalk_音频驱动的全身视频配音-单人(官流).json` | digital_human | `ok` | 7/2 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_infinitetalk_音频驱动视频配音-单人for循环长视频(官流).json` | digital_human | `ok` | 7/2 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_infinitetalk_音频驱动视频配音-双人for循环长视频(官流).json` | digital_human | `ok` | 7/2 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.1_V2V_InfiniteTalk_视频对口型(KJ流).json` | digital_human | `ok` | 8/1 |
| `5-数字人：图像语音对口型-唱歌-带货-对话/Wan2.2-s2v视频对口型.json` | digital_human | `ok` | 7/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_OneToAll_人物姿势控制.json` | motion_transfer | `ok` | 6/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_OneToAll_人物姿势控制单人20s(KJ版).json` | motion_transfer | `ok` | 8/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_SCAIL_人物姿势控制 (20s).json` | motion_transfer | `ok` | 10/1 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_SCAIL_人物姿势控制.json` | motion_transfer | `ok` | 10/1 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_SCAIL_单人多人动作迁移-Q版动漫人物宠物.json` | motion_transfer | `ok` | 10/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.1_SteadDancer_动作迁移（支持动漫人GGUF版).json` | motion_transfer | `ok` | 6/1 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_MatAnyone2遮罩-人物迁移-动作迁移-长视频循环(KJ流).json` | video_analysis, motion_transfer, segmentation | `ok` | 11/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_onnx_人物遮罩替换.json` | motion_transfer, segmentation | `ok` | 11/1 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_SAM2_人物替换.json` | motion_transfer, segmentation | `ok` | 8/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_SAM3-人物迁移-动作迁移-长视频循环(KJ流).json` | motion_transfer, segmentation | `ok` | 12/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_SAM3_人物遮罩替换(15秒长视频).json` | motion_transfer, segmentation | `ok` | 11/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_SAM3_人物遮罩替换.json` | motion_transfer, segmentation | `ok` | 11/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_Sec_人物迁移_动作迁移_长视频循环(KJ流).json` | motion_transfer | `ok` | 11/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_人物遮罩替换(KJ版).json` | motion_transfer, segmentation | `ok` | 12/0 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_人物遮罩替换(官流).json` | motion_transfer, segmentation | `ok` | 13/1 |
| `6-动作迁移：人物替换-动作模仿迁移/Wan2.2_Animate_人物遮罩替换(官流整理).json` | motion_transfer, segmentation | `ok` | 12/2 |
