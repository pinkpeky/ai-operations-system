# Commercial KTV ComfyUI Video Workflow

Last updated: 2026-05-28

This workflow reproduces the Douyin-style "commercial KTV video one-click production" pattern on the current server. The important idea is not only "make a picture move"; it is two related digital-human workflows:

- Scene-only mode: one KTV room image becomes a same-scene video with a generated virtual host/model.
- Person-in-scene mode: an image that already contains a person turns that person into a digital human with subtle motion, hosting, singing, or speaking.

The current script implements the shared rendering and assembly layer. The seed-image layer can be supplied manually today, and can later be generated locally once the image fusion/inpainting model stack is added.

## Current Server Fit

- ComfyUI root: `E:\ComfyUI_cu130\ComfyUI`
- API: `http://127.0.0.1:8188`
- Installed video path: Wan2.2 / WanVideoWrapper / VideoHelperSuite / LTX2.3 / InfiniteTalk
- Current audit: 340 executable model files, about 950GB, and 114 imported workflows.
- Current output path: `E:\ComfyUI_cu130\ComfyUI\output`

The current local model inventory is strong for image generation, image editing, image-to-video, full-body/video animation, ASR, VLM-assisted keyframe understanding, segmentation, and depth. Production should still treat the fused vertical poster or first frame as a reviewed seed image before long video generation.

## Validated InfiniteTalk Route

As of 2026-05-28, the strongest verified route for the current ShangK requirement is:

```text
approved first frame with AI woman in the real room
 -> reference audio extracted from the ShangK video
 -> Wan2.1 InfiniteTalk KJ
 -> 720x1280 raw mp4
 -> 1080x1920 delivery mp4
```

The user-validated sample is:

```text
E:\ComfyUI_cu130\ComfyUI\output\video\WanVideo_InfiniteTalk_00001-audio.mp4
```

Its embedded ComfyUI metadata has been extracted into:

```text
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\user_good_sample.prompt.json
D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\shangk_infinite_talk\user_good_sample.workflow.json
```

The reusable runner is:

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\run_shangk_infinite_talk_pipeline.py `
  --run-id shangk_infinite_talk_validated_v1
```

Detailed notes are in `docs/SHANGK_INFINITE_TALK_VALIDATED_WORKFLOW.md`.

## Two Core Modes

### 1. Scene-Only To Virtual Human

Input:

- One clean KTV room / corridor / table / door image.
- Optional role description: host, singer, service staff, boss, model.

Target output:

- Same room composition and lighting.
- A newly generated virtual person appears naturally in the scene.
- The person has small controllable motion: breathing, hand gesture, mic-holding, slight turn, camera push-in.

Recommended technical chain:

```text
scene photo
 -> image fusion / inpainting: add virtual person into the same room
 -> Wan I2V: animate the fused frame
 -> subtitles / voice / music / CTA assembly
```

Current server status:

- Wan I2V and video assembly are ready.
- The server has ComfyUI cloud image-edit nodes such as Flux Kontext, but they require Comfy login/API authorization before execution.
- The missing local-only piece is a strong image fusion/inpainting stack, such as SDXL/Flux plus identity/person control. Without that, Wan I2V alone can animate the room, but it is not stable enough to create a new person in an empty room.

### 2. Person-In-Scene To Digital Human

Input:

- A KTV scene image that already contains a person, or a generated seed image with a person placed in the room.
- Optional voiceover or role line.

Target output:

- Keep the same person, clothes, room, and lighting.
- Add subtle digital-human motion.
- For talking-head segments, use MuseTalk/LivePortrait style lip-sync.
- For full-body host/model clips, use Wan I2V/WanAnimate style motion.

Recommended technical chain:

```text
person-in-scene image
 -> identity/face/body consistency check
 -> Wan I2V or WanAnimate
 -> optional MuseTalk/LivePortrait for lip-sync shots
 -> subtitles / voice / music / CTA assembly
```

Current server status:

- Wan I2V, WanAnimate, MuseTalk, AdvancedLivePortrait, and FFmpeg are installed.
- This is the stronger mode on the current server, because the person already exists in the image.

## Production Shape

1. Prepare authorized assets.
   - KTV room photos
   - Host/model photos with consent
   - Brand text, CTA, address, phone, QR code
   - Optional voiceover file

2. Create seed images.
   - Aspect ratio: 9:16
   - Recommended resolution: 720x1280 or higher
   - For scene-only mode, this seed image is the result of adding a virtual person into the original scene.
   - For person-in-scene mode, this seed image is the source image with the person already present.
   - Avoid embedded text inside the seed image unless it is part of a real sign. Final subtitles are added later.

3. Fill the batch CSV.
   - Customer template: `deployment/comfyui/commercial_ktv_workflow/sample_manifest.csv`
   - Server demo with existing ComfyUI input images: `deployment/comfyui/commercial_ktv_workflow/demo_manifest_existing_inputs.csv`
   - Required columns: `shot_id`, `seed_image`, `prompt`
   - Optional columns: `duration`, `seed`, `title`

4. Run readiness check.

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\commercial_ktv_workflow.py doctor
```

Scene-only AI seed generation, once the Comfy image-edit node is authorized:

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\commercial_ktv_workflow.py scene-ai-seed `
  --scene-image D:\流程测试\场景素材\4.jpg `
  --output D:\流程测试\_aiops_scene_ai_virtual_beauty_seed.png
```

On the current server this command submits correctly, but the Flux Kontext node returns `Unauthorized: Please login first to use this node.` until Comfy is logged in or an equivalent local inpainting model is installed.

5. Render and assemble.

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\commercial_ktv_workflow.py render `
  --manifest D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\sample_manifest.csv `
  --label ktv_demo
```

Immediate server demo:

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\commercial_ktv_workflow.py render `
  --manifest D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\demo_manifest_existing_inputs.csv `
  --label ktv_existing_inputs_demo
```

Optional voiceover:

```powershell
D:\ai-operations-system\.venv\Scripts\python.exe D:\ai-operations-system\scripts\commercial_ktv_workflow.py render `
  --manifest D:\path\to\manifest.csv `
  --voiceover D:\path\to\voiceover.wav `
  --label customer_a_round_01
```

Outputs are written under `D:\aiops_production_runs\commercial_ktv_<label>_<timestamp>`:

- `commercial_ktv_final.mp4`
- `contact_sheet.jpg`
- per-shot ComfyUI prompt JSON
- per-shot ComfyUI history JSON
- `run_manifest.json`

## Prompt Pattern

Use one prompt per shot. Keep motion small and controllable:

```text
realistic Chinese female KTV host standing in a luxury private room,
natural smile, holding microphone, subtle breathing and gentle hand movement,
neon cyan magenta lighting, premium social media promo video,
stable face and body, preserve input room layout, no text, no watermark
```

Good shot types:

- opening room atmosphere
- host/model appearance
- fruit plate and microphone detail
- big screen / lighting / sofa pan
- final CTA room pullback

Avoid:

- large walking movements
- fast dancing
- complex hand gestures
- text generation inside ComfyUI
- multiple faces in one seed image unless needed

## Mode-Specific Prompt Examples

Scene-only fused seed prompt:

```text
Use the input KTV private room as the exact background. Add one realistic Chinese female host standing near the table, holding a microphone, black elegant outfit, natural smile, neon magenta and cyan light matching the room, realistic photography, full body, integrated shadows, no text, no watermark.
```

Person-in-scene animation prompt:

```text
Preserve the exact person, face, clothes, room layout and lighting from the input image. The host gently breathes, slightly turns toward camera, naturally holds the microphone, subtle handheld phone camera push-in, realistic premium KTV promotional video, stable face and body, no text, no watermark.
```

Talking digital-human prompt:

```text
Keep the host identity and room unchanged. Natural speaking expression, small head movement, clean lip sync, calm confident business reception tone, no exaggerated gestures, no face drift, no text, no watermark.
```

## One-Click Operation Standard

For an operator, "one click" means:

1. Put seed images into a customer folder.
2. Edit one CSV.
3. Run the render command.
4. Review `contact_sheet.jpg`.
5. Publish or rerun only failed shots.

This keeps the expensive GPU step deterministic and auditable while still giving the same commercial result: fast batch KTV promo video creation with consistent style and lower production cost.

## Upgrade Path

To make the scene-only seed image layer fully local, add a dedicated image-generation/fusion model stack:

- SDXL/Flux checkpoint
- inpainting / regional prompt workflow
- person segmentation
- IP-Adapter / InstantID style identity control when a fixed virtual host is needed
- background relighting workflow
- local seed-image workflow JSON

After that, this same script can consume generated seed images without changing the video and assembly stages.
