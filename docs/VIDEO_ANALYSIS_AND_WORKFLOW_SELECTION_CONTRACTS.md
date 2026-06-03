# 视频解析与 ComfyUI 工作流选型契约

更新日期：2026-05-28

本文档用于把“参考视频解析、运营脚本编排、ComfyUI 工作流自动选择、客户机发布、社媒数据回流”串成可实现的工程协议。它不是某一个 KTV 项目的 prompt，而是后续所有项目共用的 Agent/RAG/执行层契约。

## 当前结论

当前工程已经具备三类基础：

1. 本地大模型已接入为文本规划层，现有 `app/agents/providers/local_provider.py` 走 Ollama 文本生成接口，适合做脚本、策略、选流和复盘分析。
2. 数字人链路已有 LLM creative planner、shot execution plan 和 ComfyUI handoff 雏形，适合继续扩展成“按镜头生成执行包”。
3. 商业运营模块已经有 deliverable、execution request、monitoring observation、optimization decision，适合作为发布和数据回流闭环的主业务对象。
4. `E:\ComfyUI_cu130\ComfyUI` 模型下载已经完成主体核验：运行时审计识别 340 个可执行模型文件、约 950GB，114 个工作流，视频抽帧、ASR、VLM、SAM2/SAM3、DepthAnything、Wan/InfiniteTalk 均具备最小验证条件。

当前缺口也要明确：

1. 本地 LLM Provider 目前不是视频视觉解析模型，不能直接把视频帧/视频文件喂给 `llama70b` 得到视觉理解。
2. 视频解析需要新增独立服务：抽帧、音频提取、ASR、OCR、VLM 图像理解、镜头分段、LLM 汇总。ComfyUI 可以承担其中一部分解析能力，但不应成为唯一解析入口。
3. ComfyUI 工作流已整理成 RAG 文档，最新自动审计版为 `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl`，Agent 可先用它做候选选流，再进入素材级运行验证。

## 总体链路

```mermaid
flowchart LR
    A["用户/客户上传素材"] --> B["视频解析服务"]
    B --> C["运营目标理解"]
    C --> D["RAG 召回业务知识与工作流知识"]
    D --> E["主 Agent 制定内容计划"]
    E --> F["工作流选择与参数填充"]
    F --> G["ComfyUI 执行包"]
    G --> H["成品/候选成品"]
    H --> I["客户机审核与发布队列"]
    I --> J["OpenClaw/Playwright 发布"]
    J --> K["社媒数据回流"]
    K --> L["效果分析与优化决策"]
    L --> C
```

## 1. 视频解析服务契约

### VideoAnalysisRequest

```json
{
  "operation_id": "uuid",
  "workspace_id": "default",
  "source_asset_id": "uuid",
  "source_uri": "file:///path/to/video.mp4",
  "project_type": "ktv | local_life | ecommerce | education | brand | other",
  "analysis_goal": "学习参考视频的结构、卖点、镜头和可复用生产方式",
  "target_platforms": ["douyin"],
  "sampling_profile": "fast | balanced | deep",
  "metadata": {
    "operator_note": "客户想复刻同类型效果，但人物要 AI 生成"
  }
}
```

### VideoAnalysisResult

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "source_asset": {
    "asset_id": "uuid",
    "duration_seconds": 18.6,
    "fps": 30,
    "resolution": "1080x1920",
    "language": "zh"
  },
  "scene_summary": "视频展示夜场包厢环境，由虚拟女主持口播介绍服务亮点。",
  "shot_segments": [],
  "frame_samples": [],
  "audio_transcript": {},
  "subtitle_ocr": {},
  "visual_style": {},
  "editing_pattern": {},
  "hook_analysis": {},
  "cta_analysis": {},
  "brand_safety": {},
  "replicable_content_formula": {},
  "workflow_hints": [],
  "rag_payload": {}
}
```

### FrameSample

每个关键帧要输出可被 Agent 检索和推理的结构化信息：

```json
{
  "timestamp_seconds": 2.4,
  "image_asset_id": "uuid",
  "visual_caption": "蓝紫色灯光的 KTV 包厢，沙发、茶几和大屏幕清晰可见。",
  "scene_type": "indoor_private_room",
  "people_count": 1,
  "detected_objects": ["sofa", "table", "screen", "stage_light"],
  "composition": {
    "shot_size": "full_body",
    "camera_angle": "eye_level",
    "subject_position": "center"
  },
  "lighting": "neon_blue_low_key",
  "quality_flags": ["low_noise", "face_visible"]
}
```

### ShotSegment

```json
{
  "start_seconds": 0.0,
  "end_seconds": 4.2,
  "dominant_scene": "KTV 包厢全景",
  "action": "主持人站立口播，轻微手势",
  "camera_motion": "static",
  "transition": "hard_cut",
  "audio_text": "今天带你看一家适合商务招待的空间...",
  "subtitle_text": "商务招待 / 私密包厢 / 氛围灯光",
  "workflow_relevance": [
    "digital_human_lip_sync",
    "scene_consistent_i2v",
    "short_video_cutting"
  ]
}
```

### 解析模块拆分

| 模块 | 输入 | 输出 | 可用能力 |
|---|---|---|---|
| 抽帧 | 视频 | 关键帧图片、时间戳 | ffmpeg / ComfyUI 截帧流 |
| 音频提取 | 视频 | wav/mp3 | ffmpeg / ComfyUI 音频分离流 |
| ASR | 音频 | 文案、字幕时间轴 | Qwen3-ASR / Whisper 工作流或独立 ASR 服务 |
| OCR | 关键帧 | 画面文字 | PaddleOCR、RapidOCR 或 VLM |
| VLM | 关键帧 | 场景、人物、物体、风格描述 | QwenVL、SmolVLM、OllamaVision、JoyCaption 节点或外部视觉模型 |
| 分镜归纳 | 帧/字幕/ASR | shot_segments | LLM 文本规划 |
| 运营拆解 | 全部解析结果 | hook、卖点、CTA、复刻公式 | LLM 文本规划 |

## 2. ComfyUI 工作流 RAG 文档结构

`docs/COMFYUI_CU130_WORKFLOW_GUIDE.md` 是人读版说明。入库时建议把每个工作流拆成独立 chunk，并带上以下 metadata。

```json
{
  "knowledge_type": "comfyui_workflow",
  "workflow_id": "wan22_animate_sam3_subject_replace",
  "workflow_name": "Wan2.2_Animate_SAM3_人物遮罩替换.json",
  "workflow_path": "E:/ComfyUI_cu130/ComfyUI/user/default/workflows/...",
  "category": "motion_transfer",
  "capabilities": [
    "subject_replacement",
    "motion_transfer",
    "scene_consistency",
    "short_video_generation"
  ],
  "input_contract": {
    "required": ["reference_person_image", "motion_video"],
    "optional": ["mask_video", "style_prompt", "negative_prompt"],
    "aspect_ratios": ["9:16", "16:9", "1:1"]
  },
  "output_contract": {
    "primary": "video",
    "secondary": ["preview_video", "mask_preview"],
    "recommended_review": ["face_quality", "hand_quality", "background_stability"]
  },
  "model_requirements": [
    "Wan2.2 Animate",
    "SAM3",
    "VAE",
    "CLIP/T5 text encoder"
  ],
  "best_for": [
    "参考视频有人物动作，需要替换为 AI 虚拟人物",
    "客户希望复刻同场景动作节奏"
  ],
  "not_for": [
    "只需要生成口播音频",
    "没有动作参考视频且只做静态海报"
  ],
  "quality_risks": [
    "手部畸形",
    "脸部身份漂移",
    "遮罩边缘闪烁"
  ],
  "selection_keywords": [
    "动作迁移",
    "人物替换",
    "参考视频",
    "同场景数字人"
  ],
  "project_types": ["ktv", "local_life", "brand", "ecommerce"]
}
```

## 3. Agent 选流决策契约

主 Agent 不应该直接写 ComfyUI 节点，而应该输出一个可审核、可回放、可失败降级的选流决策。

```json
{
  "operation_id": "uuid",
  "content_mode": "digital_human_video",
  "operation_goal": "生成抖音竖屏商用短视频，虚拟美女主持在客户场景中口播介绍服务。",
  "source_understanding": {
    "has_reference_video": true,
    "has_scene_image": true,
    "has_person_image": false,
    "needs_ai_virtual_person": true,
    "needs_lip_sync": true,
    "needs_motion_transfer": false
  },
  "selected_workflows": [
    {
      "rank": 1,
      "workflow_id": "wan21_i2v_infinitetalk_prompt_control",
      "workflow_name": "Wan2.1_I2V_InfiniteTalk_提示词调度动作控制图生视频数字人(KJ版).json",
      "reason": "适合单张人物/场景图生成口播数字人，并用音频驱动口型。",
      "required_inputs": ["ai_person_image", "voice_audio", "scene_reference", "prompt"],
      "parameter_plan": {
        "aspect_ratio": "9:16",
        "fps": 24,
        "duration_seconds": 6,
        "character_prompt": "成年虚拟女主持，商务气质，自然站姿，真实比例",
        "scene_prompt": "客户提供的室内商业场景，保持灯光和空间结构"
      },
      "risk_flags": ["需要先生成合格虚拟人物首帧", "口型和手部需要质检"],
      "fallback_workflow_id": "wan22_s2v_lip_sync"
    }
  ],
  "rejected_workflows": [
    {
      "workflow_id": "birefnet_background_remove",
      "reason": "本需求不要求找真人画像抠图放入场景。"
    }
  ],
  "human_review_required": true
}
```

## 4. ComfyUI 执行包契约

选流后再生成可交给 ComfyUI Runtime 的执行包。执行包必须和原始 workflow JSON 分离，避免 Agent 直接改坏节点图。

```json
{
  "execution_plan_id": "uuid",
  "workflow_id": "wan21_i2v_infinitetalk_prompt_control",
  "workflow_path": "E:/ComfyUI_cu130/ComfyUI/user/default/workflows/...",
  "runtime_provider": "comfyui_cu130",
  "input_assets": {
    "scene_reference": "asset://scene_001",
    "ai_person_image": "asset://virtual_host_001",
    "voice_audio": "asset://voice_001"
  },
  "parameter_overrides": {
    "positive_prompt": "真实商业空间中的成年虚拟女主持，自然表情，完整身体比例，蓝紫色氛围灯光",
    "negative_prompt": "畸形手，扭曲脸，过度磨皮，塑料感，儿童化，低清晰度",
    "width": 1080,
    "height": 1920,
    "fps": 24,
    "frames": 144
  },
  "expected_outputs": [
    {
      "slot": "primary_video",
      "type": "video",
      "format": "mp4"
    }
  ],
  "quality_gates": [
    "人物必须是成年女性虚拟主持人",
    "脸部五官正常，身体比例正常",
    "背景不能明显崩坏或跳变",
    "口型与音频基本同步",
    "不得出现真实未授权人物身份"
  ],
  "fallback_plan": {
    "if_face_bad": "重新生成 ai_person_image 首帧",
    "if_lip_sync_bad": "切换 S2V/InfiniteTalk 备选流",
    "if_background_bad": "减少运动幅度或改用场景重绘后再 I2V"
  }
}
```

## 5. 客户机发布包契约

成品通过审核后，才进入客户机发布队列。发布包面向 OpenClaw/Playwright，不应该直接混入 ComfyUI 参数。

```json
{
  "publish_package_id": "uuid",
  "operation_id": "uuid",
  "deliverable_id": "uuid",
  "platform": "douyin",
  "account_ref": "customer_account_alias",
  "asset_ids": ["asset://final_video_001"],
  "caption": "今晚的商务招待空间，氛围感和私密性都到位。",
  "hashtags": ["商务招待", "本地生活", "KTV"],
  "schedule_time": "2026-05-28T21:00:00+08:00",
  "approval_status": "approved",
  "browser_execution": {
    "executor": "openclaw_playwright",
    "mode": "reviewed_post",
    "requires_logged_in_session": true,
    "allow_auto_publish": false
  },
  "safety_checks": [
    "客户已确认发布账号",
    "素材版权和肖像权已确认",
    "文案无禁词",
    "发布时间已确认"
  ]
}
```

## 6. 社媒数据回流契约

发布后回流的数据要能支撑下一轮优化，而不是只保存截图。

```json
{
  "publish_id": "uuid",
  "platform": "douyin",
  "post_url": "https://...",
  "collected_at": "2026-05-29T10:00:00+08:00",
  "metrics": {
    "impressions": 12000,
    "plays": 8600,
    "completion_rate": 0.31,
    "likes": 260,
    "comments": 34,
    "shares": 19,
    "follows": 8,
    "inquiries": 3
  },
  "audience_signals": {
    "top_comment_topics": ["价格", "位置", "包厢环境"],
    "negative_feedback": ["人物不够真实", "口播有点像广告"],
    "high_interest_segments": ["前 3 秒场景展示", "价格权益段落"]
  },
  "comparison_baseline": {
    "previous_publish_id": "uuid",
    "metric_delta": {
      "completion_rate": 0.06,
      "inquiries": 2
    }
  }
}
```

## 7. 优化决策契约

```json
{
  "optimization_decision_id": "uuid",
  "operation_id": "uuid",
  "hypothesis": "用户对真实环境更敏感，下一版应减少虚拟人物全身镜头，增加包厢细节和权益字幕。",
  "evidence": [
    "高兴趣片段集中在前 3 秒环境展示",
    "评论询问价格和位置",
    "负反馈提到人物不够真实"
  ],
  "next_content_brief": {
    "hook": "先展示真实空间和价格权益，再让虚拟主持人补充说明",
    "script_adjustments": ["减少空泛形容词", "增加到店路径和套餐信息"],
    "shot_adjustments": ["环境 B-roll 占比提高到 60%", "数字人镜头控制在半身"]
  },
  "workflow_adjustments": [
    {
      "target": "comfyui_workflow_selection",
      "change": "优先使用环境图生视频和半身口播流，降低全身动作迁移权重"
    }
  ],
  "publishing_adjustments": [
    {
      "target": "caption",
      "change": "标题加入价格/位置/适合场景"
    }
  ]
}
```

## 8. 推荐开发顺序

1. 先实现视频解析服务的最小闭环：ffmpeg 抽帧、音频提取、ASR、关键帧 VLM、LLM 汇总。
2. 把 `COMFYUI_CU130_WORKFLOW_GUIDE.md` 拆成 workflow 级 RAG chunk，metadata 使用本文第 2 节结构。
3. 扩展 `CommercialVideoMainAgent`：输入 video analysis result + RAG result，输出第 3 节选流决策。
4. 新增 workflow execution package 生成器：把选流结果转成第 4 节执行包。
5. 将执行包挂接到现有 `CommercialOperationComfyUIExecutionPlan` 或 `WorkflowTemplateRun`，保留人工审核门。
6. 成品通过审核后进入 deliverable 和 execution request，再由客户机 OpenClaw/Playwright 执行发布。
7. 发布数据回流写入 monitoring observation，再生成 optimization decision，形成下一轮 brief。

## 9. 对当前需求的落地判断

对于“参考一个抖音视频，生成同类商业短视频，并且人物是 AI 虚拟美女而不是抠真人图”这个需求，Agent 的正确判断应该是：

1. 参考视频只用于解析镜头、节奏、场景、文案结构和运营目的。
2. 人物素材应由 AI 生成一个合格的成年虚拟女主持首帧，再进入数字人口播或图生视频链路。
3. 如果有动作参考视频，才进入动作迁移/人物替换；如果只有场景图，则优先走场景一致的 I2V + InfiniteTalk/S2V。
4. 质量门必须先检查人物是否正常、是否符合“商业虚拟主持人”审美，再谈视频生成。
