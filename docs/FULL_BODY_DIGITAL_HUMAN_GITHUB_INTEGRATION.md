# 全身数字人 GitHub 方案接入记录

更新时间：2026-05-27

## 目标

本次接入的目标不是继续做素材拼接，也不是头像口播数字人，而是把视频链路升级为：

1. 主 agent 根据运营主题生成剧本、镜头、人物动作和场景约束。
2. 视频子 agent 读取用户素材，抽取人物身份、全身姿态、人脸参考和 KTV 场景参考。
3. 生成链路输出连续、真实风格、人物一致的商务 KTV 宣发视频。

## 已采用主线

### ComfyUI-WanVideoWrapper

来源：https://github.com/kijai/ComfyUI-WanVideoWrapper

用途：

- 接入 WanVideo / WanAnimate / S2V / Stand-In 相关节点。
- 承载全身人物动画生成，而不是只做头像口播。
- 当前服务器 ComfyUI 已加载该节点包。

安装位置：

- `E:\ComfyUI\custom_nodes\ComfyUI-WanVideoWrapper`

关键节点已验证：

- `WanVideoModelLoader`
- `WanVideoSampler`
- `WanVideoVAELoader`
- `WanVideoTextEncodeCached`
- `WanVideoAnimateEmbeds`
- `WanVideoAddS2VEmbeds`
- `WanVideoAddStandInLatent`

### ComfyUI-WanAnimatePreprocess

来源：https://github.com/kijai/ComfyUI-WanAnimatePreprocess

用途：

- 从用户素材中抽取人物姿态和人脸参考。
- 为 WanAnimate 提供全身动作控制输入。

安装位置：

- `E:\ComfyUI\custom_nodes\ComfyUI-WanAnimatePreprocess`

关键节点已验证：

- `OnnxDetectionModelLoader`
- `PoseAndFaceDetection`
- `DrawViTPose`

## 已下载模型与权重

### WanAnimate 主模型

来源：https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled

本机位置：

- `E:\ComfyUI\models\diffusion_models\WanVideo\2_2\Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors`

大小：

- 18,401,760,586 bytes

### LightX2V 加速 LoRA

来源：https://huggingface.co/Kijai/WanVideo_comfy

本机位置：

- `E:\ComfyUI\models\loras\WanVideo\Lightx2v\lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`

大小：

- 738,005,744 bytes

### WanAnimate relight LoRA

来源：https://huggingface.co/Kijai/WanVideo_comfy

本机位置：

- `E:\ComfyUI\models\loras\WanVideo\WanAnimate_relight_lora_fp16.safetensors`

大小：

- 1,436,672,440 bytes

### 姿态与检测模型

来源：

- https://huggingface.co/Wan-AI/Wan2.2-Animate-14B
- https://huggingface.co/Kijai/vitpose_comfy

本机位置：

- `E:\ComfyUI\models\detection\yolov10m.onnx`
- `E:\ComfyUI\models\detection\vitpose_h_wholebody_model.onnx`
- `E:\ComfyUI\models\detection\vitpose_h_wholebody_data.bin`

大小：

- `yolov10m.onnx`: 61,659,339 bytes
- `vitpose_h_wholebody_model.onnx`: 420,252 bytes
- `vitpose_h_wholebody_data.bin`: 2,548,958,740 bytes

### WanVideoWrapper 专用文本编码器与 VAE

来源：https://huggingface.co/Kijai/WanVideo_comfy

本机位置：

- `E:\ComfyUI\models\text_encoders\umt5-xxl-enc-bf16.safetensors`
- `E:\ComfyUI\models\vae\Wan2_1_VAE_bf16.safetensors`

大小：

- `umt5-xxl-enc-bf16.safetensors`: 11,361,845,464 bytes
- `Wan2_1_VAE_bf16.safetensors`: 253,806,278 bytes

说明：

- `WanVideoTextEncodeCached` 不支持当前原生 Wan 使用的 `umt5_xxl_fp8_e4m3fn_scaled.safetensors`。
- 因此必须补齐 `umt5-xxl-enc-bf16.safetensors`，否则 WanAnimate 生成会在文本编码节点失败。

## 冒烟测试结果

ComfyUI 运行地址：

- `http://127.0.0.1:8188`

测试素材：

- `ktv_v4_scene_person_source.mp4`

测试流程：

1. `VHS_LoadVideo` 读取人物素材。
2. `OnnxDetectionModelLoader` 加载 ViTPose 与 YOLO。
3. `PoseAndFaceDetection` 抽取全身姿态和人脸。
4. `DrawViTPose` 输出姿态图。
5. `SaveImage` 保存输出。

输出文件：

- `E:\ComfyUI\output\aiops_wananimate_pose_smoke_00001_.png`
- `E:\ComfyUI\output\aiops_wananimate_pose_smoke_00002_.png`
- `E:\ComfyUI\output\aiops_wananimate_pose_smoke_00003_.png`
- `E:\ComfyUI\output\aiops_wananimate_pose_smoke_00004_.png`
- `E:\ComfyUI\output\aiops_wananimate_pose_smoke_00005_.png`
- `E:\ComfyUI\output\aiops_wananimate_face_smoke_00001_.png`
- `E:\ComfyUI\output\aiops_wananimate_face_smoke_00002_.png`
- `E:\ComfyUI\output\aiops_wananimate_face_smoke_00003_.png`
- `E:\ComfyUI\output\aiops_wananimate_face_smoke_00004_.png`
- `E:\ComfyUI\output\aiops_wananimate_face_smoke_00005_.png`

结论：

- ComfyUI 已能从用户人物素材中抽取姿态和人脸参考。
- 这条链路可以作为全身数字人生成的基础，不再只依赖头像口播。
- 第一次 ONNX 冷启动约 57 秒，后续同类检测会明显更快。

## 全身生成闭环测试

测试流程：

1. 使用 `ref_04_host_from_video.png` 作为全身人物参考。
2. 使用 `ktv_v4_scene_person_source.mp4` 抽取人物姿态和人脸 crop。
3. 使用 `WanVideoAnimateEmbeds` 合成 ref / pose / face / clip vision 条件。
4. 使用 `Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ` + `WanAnimate_relight_lora_fp16` + `LightX2V` 生成短视频。
5. 使用 `WanVideoDecode` 和 `VHS_VideoCombine` 输出 mp4。

输出文件：

- `E:\ComfyUI\output\aiops_wananimate_fullbody_smoke_00001.mp4`
- `E:\ComfyUI\output\aiops_wananimate_fullbody_smoke_contact.jpg`

输出规格：

- 832x480
- 17 frames
- 8 fps
- 2.125 seconds
- H.264 mp4

结论：

- 全身数字人生成闭环已经跑通。
- 当前短测已经不是素材拼接，而是由 WanAnimate 重新生成的全身人物镜头。
- 身份一致性仍未达到“与原照片完全一致”的最终标准，下一步需要继续加强身份锁定：优先使用 Stand-In latent、更多正脸/侧脸参考、mask/background 分离，以及更严格的质量筛选。

## 候选项目评估

### Stand-In

来源：

- https://github.com/WeChatCV/Stand-In
- https://github.com/WeChatCV/Stand-In_Preprocessor_ComfyUI

定位：

- 身份保持视频生成增强。
- 适合后续用于主角脸部一致性增强。

当前状态：

- 已克隆到 `E:\aiops_external_tools`。
- 暂不直接装入生产 ComfyUI，避免引入未验证依赖破坏现有环境。
- WanVideoWrapper 已提供 `WanVideoAddStandInLatent` 节点，后续优先走 wrapper 内置方式接入。

### MusePose

来源：https://github.com/TMElyralab/MusePose

定位：

- 姿态驱动虚拟人。

当前状态：

- 已克隆到 `E:\aiops_external_tools`。
- 暂不装入生产环境，因为它更像独立老栈工程，依赖与当前 Python 3.12 / PyTorch 2.11 / CUDA 12.8 环境不匹配风险较高。

### EchoMimicV2

来源：https://github.com/antgroup/echomimic_v2

定位：

- 音频驱动半身人物动画。

当前状态：

- 已克隆到 `E:\aiops_external_tools`。
- 暂不作为主线，因为用户要求是全身数字人、真实场景、连续镜头；它更适合作为半身表达或口型增强备选。

## 下一步接入方向

1. 用主 agent 生成完整 KTV 宣发片导演计划：故事、镜头、旁白、动作、素材绑定、负面约束。
2. 用视频子 agent 将素材分为：主角身份图、全身姿态视频、走廊/包间/厅内背景、招牌/门外环境。
3. 用 WanAnimate 生成全身人物镜头，使用用户素材提取的 pose、face 和 background 作为控制条件。
4. 口播声音暂不走默认 AI 味 TTS，需要接入更自然的声音策略：真人参考音色、慢速语气、环境声混合、后期压缩和空间混响。
5. 如需要进一步增强身份一致性，再补 Stand-In 参考 latent 或专门身份保持权重。
