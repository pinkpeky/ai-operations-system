# 商K首帧到视频 validated workflow

更新日期：2026-05-28

本文记录当前已经由人工样片验证可用的商K视频路线。结论很明确：在本服务器当前模型和工作流条件下，优先使用“高质量首帧图 + 参考音频 + Wan2.1 InfiniteTalk KJ”形成可交付视频闭环；Wan2.2 Animate/SteadyDancer 继续作为后续动作迁移探索，不作为当前优先交付路线。

## 1. 已验证样片

用户手动验证样片：

```text
E:\ComfyUI_cu130\ComfyUI\output\video\WanVideo_InfiniteTalk_00001-audio.mp4
```

样片属性：

```json
{
  "resolution": "720x1280",
  "fps": 16,
  "video_duration_seconds": 15.5625,
  "video_frames": 249,
  "audio_sample_rate": 16000,
  "audio_channels": 1
}
```

样片 contact sheet：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_reference_action\user_good_infinite_talk_contact.jpg
```

## 2. 从样片反查出的核心配置

该 mp4 内保存了 ComfyUI metadata，已抽取为模板：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\user_good_sample.prompt.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\user_good_sample.workflow.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\user_good_sample.summary.json
```

关键节点：

| 节点 | 类型 | 作用 |
|---|---|---|
| `284` | `LoadImage` | 读取首帧图 `shangk_standing_mic_first_frame.png` |
| `125` | `LoadAudio` | 读取参考音频 `shangk_reference_audio.wav` |
| `355` | `CR Prompt Text` | 动作提示词 |
| `317` | `WanVideoTextEncode` | 正负提示词编码 |
| `120` | `MultiTalkModelLoader` | `Wan\Wan2_1-InfiniteTalk_Single_Q6_K.gguf` |
| `122` | `WanVideoModelLoader` | `Wan\Wan2.1_I2V_14B_480p_AniWan_New_Q5_K_M.gguf` |
| `192` | `WanVideoImageToVideoMultiTalk` | 首帧图到 InfiniteTalk 视频 embedding |
| `194` | `MultiTalkWav2VecEmbeds` | 音频驱动 embedding |
| `128` | `WanVideoSampler` | 视频采样 |
| `131` | `VHS_VideoCombine` | 合成 mp4 并保存 metadata |

样片 prompt：

```text
对着观众唱歌并摇摆身体跳舞
```

样片核心采样参数：

```json
{
  "steps": 4,
  "cfg": 1.0,
  "shift": 11.0,
  "scheduler": "dpm++_sde",
  "denoise_strength": 1.0,
  "motion_frame": 9,
  "frame_window_size": 49,
  "fps": 16,
  "scale_to_length": 1280
}
```

## 3. 正式工程脚本

新增脚本：

```text
D:\ai-operations-system\scripts\run_shangk_infinite_talk_pipeline.py
```

职责：

1. 读取已验证样片抽取出的 API prompt 模板。
2. 复制或注册首帧图到 ComfyUI input 根目录。
3. 从商K参考视频提取 16k mono wav 音频，或直接使用指定音频。
4. 只修改本次运行需要变更的节点输入：首帧、音频、prompt、negative prompt、seed、fps、steps、输出前缀。
5. 调用 ComfyUI `/object_info` 做节点和 required input 预检。
6. 提交 ComfyUI `/prompt`。
7. 等待 history 完成，复制 raw mp4 到 `output\商k\视频生成`。
8. 生成 1080x1920 delivery mp4 和 contact sheet。
9. 写入本次运行 report。

默认命令：

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\run_shangk_infinite_talk_pipeline.py `
  --run-id shangk_infinite_talk_validated_v1
```

可调整 prompt：

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\run_shangk_infinite_talk_pipeline.py `
  --run-id shangk_infinite_talk_prompt_test_01 `
  --prompt "对着观众唱歌，轻微跳舞，右手拿麦克风，眼神看向镜头，身体自然摇摆"
```

默认输出：

```text
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\{run_id}_raw.mp4
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\{run_id}_delivery_1080x1920.mp4
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\{run_id}\report.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\{run_id}\contact.jpg
```

## 4. 与动作迁移路线的关系

当前目标是优先跑通可交付视频部分。基于实际测试：

- `Wan2.2_Animate_人物遮罩替换(KJ版)` 能产生动作，但容易带回参考视频背景、衣服和字幕，不适合作为“锁定首帧场景”的当前主线。
- 使用静态首帧作为背景约束时，Wan2.2 Animate 可能保留场景但动作弱，甚至人物不动。
- SteadyDancer 是更接近“舞蹈动作迁移”的路线，但导入工作流仍需处理 SetNode/GetNode、禁用节点、模型下拉值等问题，且尚未产出比 InfiniteTalk 更稳定的商K成片。
- 用户手动验证的 Wan2.1 InfiniteTalk KJ 路线已经能让首帧人物在同场景内唱歌、摆动、带音频，当前更适合作为第一条生产闭环。

因此当前优先级：

```text
Qwen Image Edit 生成高质量首帧
 -> 人工或自动质检首帧
 -> Wan2.1 InfiniteTalk KJ 生成唱歌/轻舞视频
 -> 1080x1920 delivery
 -> 后续社媒发布/数据回流
```

## 5. 源工作流保护

当前脚本不覆盖 ComfyUI 原始 workflow。已验证样片模板被复制到项目目录作为执行模板，本次运行只写：

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\{run_id}\prompt.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\{run_id}\workflow.json
```

ComfyUI 输出写入 `output\商k\视频生成`，不会反写 `E:\ComfyUI_cu130\ComfyUI\user\default\workflows` 下的原始节点图。

## 6. 脚本版运行结果

自动化脚本已在真实 ComfyUI 队列跑通：

```json
{
  "prompt_id": "62e1f8e5-3aa3-4215-a579-94015c59505e",
  "status": "success",
  "filename_prefix": "商k/视频生成/shangk_infinite_talk_validated_v1",
  "fps": 16,
  "delivery_resolution": "1080x1920",
  "duration_seconds": 15.552
}
```

产物：

```text
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\shangk_infinite_talk_validated_v1_raw.mp4
E:\ComfyUI_cu130\ComfyUI\output\商k\视频生成\shangk_infinite_talk_validated_v1_delivery_1080x1920.mp4
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\shangk_infinite_talk_validated_v1\report.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\shangk_infinite_talk_validated_v1\contact.jpg
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\runs\shangk_infinite_talk_validated_v1\delivery_contact.jpg
```

本次运行说明：ComfyUI 视频生成成功；脚本初版在最后写 `report.json` 时因 `Path` JSON 序列化失败报错，但视频、delivery、contact sheet 均已生成。该脚本问题已修复，并已补写本次 `report.json`。

## 7. 已完成验证

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe -m py_compile `
  scripts\run_shangk_infinite_talk_pipeline.py `
  scripts\run_shangk_steadydancer_pipeline.py `
  app\comfyui_runtime\workflow_materializer.py

D:\ai-operations-system\.venv\Scripts\python.exe -m pytest tests\test_comfyui_workflow_materializer.py -q
```

结果：

```text
13 passed
```
