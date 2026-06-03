# ComfyUI_cu130 工作流 RAG 文档生成摘要

Collection: `comfyui_cu130_workflows`
Document count: `53`

## 按分类统计

- 动作迁移：人物替换、动作模仿: 16
- 基础处理: 19
- 数字人：口型、唱歌、带货、对话: 7
- 视频生成: 1
- 语音生成: 6
- 音乐生成: 4

## 按能力统计

- asr: 2
- depth_control: 2
- digital_human_lip_sync: 7
- general_comfyui_workflow: 3
- image_to_video: 3
- motion_transfer: 16
- music_generation: 6
- post_processing: 8
- subject_segmentation: 14
- tts: 7
- video_analysis: 5

## 入库建议

逐行读取 `cu130_workflow_rag_documents.jsonl`，对每行调用现有 RAG ingest：

```json
{"text": "...", "metadata": {...}, "source_id": "...", "source_name": "...", "source_type": "comfyui_workflow", "collection_name": "comfyui_cu130_workflows"}
```

这些条目只负责工作流选型知识，不代表模型已经下载完成或工作流已经通过运行验证。
