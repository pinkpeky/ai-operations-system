# ComfyUI MuseTalk Server Runbook

Last updated: 2026-05-27

This runbook captures the production-server setup performed for the guarded ComfyUI and local digital-human workflow. It is intentionally operational: it records what is installed on the server, which repository scripts reproduce the setup, and how to verify that the AI Ops API can hand off a MuseTalk video job and ingest the generated delivery asset.

## Server Layout

- AI Ops repository: `D:\ai-operations-system`
- ComfyUI runtime: `E:\ComfyUI`
- ComfyUI Python: `E:\ComfyUI\venv\Scripts\python.exe`
- ComfyUI URL: `http://127.0.0.1:8188`
- Docker-to-host ComfyUI URL: `http://host.docker.internal:8188`
- ComfyUI logs:
  - `E:\ComfyUI\logs\comfyui_stdout.log`
  - `E:\ComfyUI\logs\comfyui_stderr.log`
- AI Ops API URL: `http://localhost:8000`

## Repository Assets

The following repository files make the server setup reproducible:

- `deployment/windows/start_comfyui_aiops.ps1`
  Starts `E:\ComfyUI` on `127.0.0.1:8188`, sets `FFMPEG_PATH`, and writes stdout/stderr logs under `E:\ComfyUI\logs`.
- `deployment/windows/register_comfyui_aiops_task.ps1`
  Registers the Windows startup task `AI Ops ComfyUI E Drive`. By default it copies the startup script to `E:\ComfyUI\start-comfyui-aiops.ps1` so the scheduled task is stable even if the repository moves.
- `deployment/windows/apply_comfyui_musetalk_server_fixes.ps1`
  Applies the MuseTalk Windows/PyTorch compatibility patch and the local `mmengine` checkpoint loader fix.
- `deployment/windows/verify_comfyui_musetalk_aiops.ps1`
  Verifies model files, ComfyUI health, required nodes, Ollama models, and AI Ops guarded runtime endpoints.
- `deployment/comfyui/musetalk_fsh_windows_compat.patch`
  Captures the custom-node patch applied to `ComfyUI-MuseTalk_FSH`.

## Runtime Configuration

The production server uses guarded ComfyUI runtime switches in `.env`:

```env
COMFYUI_RUNTIME_PROVIDER=guarded
COMFYUI_RUNTIME_ENABLED=true
COMFYUI_RUNTIME_ALLOW_NETWORK=true
COMFYUI_RUNTIME_BASE_URL=http://host.docker.internal:8188
COMFYUI_RUNTIME_ALLOWED_HOSTS=host.docker.internal,127.0.0.1,localhost
COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true
COMFYUI_RUNTIME_HEALTH_PATH=/system_stats
COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS=/system_stats
COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=true
COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS=/prompt,/history,/queue
COMFYUI_VIDEO_GPU_ENDPOINTS=default|http://host.docker.internal:8188|0
DIGITAL_HUMAN_PROVIDER=local_musetalk_liveportrait
DIGITAL_HUMAN_ENABLED=true
DIGITAL_HUMAN_ALLOW_EXTERNAL_API=false
```

Local model defaults are:

```env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434
LOCAL_LLM_MODEL=llama70b
LOCAL_EMBEDDING_MODEL=bge-m3
```

Restart the API after editing `.env`:

```powershell
docker compose up -d --force-recreate api
```

## Installed ComfyUI Components

ComfyUI was cloned fresh to `E:\ComfyUI` and runs with Python 3.12.10 and PyTorch `2.11.0+cu128`. The server detects RTX 5090 GPU capacity through `/system_stats`.

Installed custom nodes:

- `ComfyUI-VideoHelperSuite`
- `ComfyUI-Manager`
- `ComfyUI-AdvancedLivePortrait`
- `ComfyUI-MuseTalk_FSH`
- `ComfyUI-Impact-Pack`
- `ComfyUI-Impact-Subpack`

Required node names that should appear in `/object_info`:

- `VHS_VideoCombine`
- `AdvancedLivePortrait`
- `MuseTalk`
- `MuseTalkRealTime`
- `MuseTalkLoadVideo`
- `PreViewVideo`
- `CombineAudioVideo`
- `LoadAudio`

`MuseTalkLoadVideo` is intentionally added as a unique alias because modern ComfyUI also exposes an internal `LoadVideo` node. Without the alias, the workflow can connect a video output but not the audio output required by MuseTalk.

## MuseTalk Model Inventory

Required files under `E:\ComfyUI\custom_nodes\ComfyUI-MuseTalk_FSH\models`:

| Relative path | Expected size |
| --- | ---: |
| `musetalk\musetalk.json` | 748 |
| `musetalk\pytorch_model.bin` | 3,400,076,549 |
| `dwpose\dw-ll_ucoco_384.pth` | 406,878,486 |
| `face-parse-bisent\79999_iter.pth` | 53,289,463 |
| `face-parse-bisent\resnet18-5c106cde.pth` | 46,827,520 |
| `sd-vae-ft-mse\config.json` | 547 |
| `sd-vae-ft-mse\diffusion_pytorch_model.bin` | 334,707,217 |
| `whisper\tiny.pt` | 75,572,083 |

The large MuseTalk UNet weight was downloaded from ModelScope because Hugging Face direct download was throttled on the server:

```powershell
E:\ComfyUI\venv\Scripts\modelscope.exe download --model AI-ModelScope/MuseTalk --revision master --local_dir E:\ComfyUI\custom_nodes\ComfyUI-MuseTalk_FSH\models --max-workers 8 musetalk/pytorch_model.bin
```

## Windows Compatibility Fixes

The server applies the repository patch in `deployment/comfyui/musetalk_fsh_windows_compat.patch` plus a local `mmengine` checkpoint loader adjustment:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\apply_comfyui_musetalk_server_fixes.ps1 -ComfyRoot E:\ComfyUI
```

The fixes cover:

- `MuseTalkLoadVideo` alias for stable video+audio output.
- Final MuseTalk output muxes the generated silent lip-sync video with the input audio, producing a complete MP4 instead of a silent video.
- `torch.load(..., weights_only=False)` compatibility for legacy official model weights under PyTorch 2.6+ defaults.
- DWPose backbone scope changed from `mmdet` to `mmpose` to avoid the unavailable Windows `mmcv._ext` path for this workflow.
- `mmengine.runner.checkpoint.load_from_local` loads trusted local DWPose checkpoints with `weights_only=False`.

The patch assumes the model files are trusted and were downloaded from the official or mirrored MuseTalk/DWPose sources used during setup.

## Startup Task

Register or refresh the Windows startup task:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\register_comfyui_aiops_task.ps1 -ComfyRoot E:\ComfyUI
```

The expected task is:

- Name: `AI Ops ComfyUI E Drive`
- Trigger: At startup with one-minute delay
- Action: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File E:\ComfyUI\start-comfyui-aiops.ps1 -ComfyRoot E:\ComfyUI`

Manual start:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\start_comfyui_aiops.ps1 -ComfyRoot E:\ComfyUI
```

## Verification

Run the repository verification script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deployment\windows\verify_comfyui_musetalk_aiops.ps1 -ComfyRoot E:\ComfyUI -WorkspaceId video-smoke
```

Manual spot checks:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8188/system_stats | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri http://127.0.0.1:8188/object_info | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri http://localhost:8000/api/v1/health | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri http://localhost:8000/api/v1/comfyui-runtime/queue -Headers @{"X-Workspace-Id"="video-smoke"} | ConvertTo-Json -Depth 8
ollama list
```

Expected local Ollama models:

- `llama70b`
- `bge-m3`

## Full-Chain Validation Record

The server produced a real MuseTalk digital-human video from:

- input requirement: Chinese operations story script
- uploaded/placed material: demo avatar video under `E:\ComfyUI\input`
- generated voice: Windows SAPI `Microsoft Huihui Desktop`
- workflow: `MuseTalkLoadVideo -> MuseTalk -> PreViewVideo`

Final MP4:

```text
E:\ComfyUI\output\aiops_ops_story_avatar_aiops_ops_story_avatar.mp4
```

Validated media properties:

- duration: about 13.27 seconds
- video: H.264, 512 x 884, 15 fps
- audio: AAC

AI Ops persisted records from the validation:

- ComfyUI video job: `71ac53f3-62e1-4f73-a283-7c3c690ed138`
- ComfyUI runtime prompt: `7aeebb02-b671-413d-8e67-62d6e42d61f5`
- Digital human job: `8d8f9e14-096e-42c8-8777-3c06cbcb0f03`
- Delivery asset: `4c7e6f70-ad87-4d4c-b631-39b559189af7`
- Digital human status: `completed`
- Delivery status: `ready`

The test job still records `consent_required=true` and `consent_status=missing` because the demo source is operational validation material. Real customer production runs must use authorized portrait/material assets before publishing or commercial use.

## Known Non-Blocking Warnings

- `ComfyUI-Impact-Pack` reports SAM2 unavailable because `facebook/sam2` was not installed. This does not block MuseTalk digital-human generation.
- `mmcv-lite` can warn that `MultiScaleDeformableAttention` is unavailable. The MuseTalk/DWPose path used here avoids the full `mmcv._ext` dependency.
- The VAE loader may mention missing `diffusion_pytorch_model.safetensors` and fall back to the trusted `.bin` file. This is expected for the installed `sd-vae-ft-mse` layout.

## Troubleshooting

- If AI Ops cannot reach ComfyUI from Docker, check `COMFYUI_RUNTIME_BASE_URL=http://host.docker.internal:8188` and `COMFYUI_RUNTIME_ALLOWED_HOSTS=host.docker.internal,127.0.0.1,localhost`.
- If `/object_info` lacks `MuseTalkLoadVideo`, reapply `deployment/windows/apply_comfyui_musetalk_server_fixes.ps1` and restart ComfyUI.
- If MuseTalk fails with `weights_only=True`, reapply the compatibility fixes and verify the `mmengine` checkpoint loader patch.
- If MuseTalk fails with `No module named 'mmcv._ext'`, verify the DWPose config uses `_scope_='mmpose'`.
- If output videos are silent, verify `inference.py` contains the `subprocess.run` audio mux step and `ffmpeg` is available.
