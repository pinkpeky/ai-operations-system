from __future__ import annotations

import json
from pathlib import Path


OUT = Path(r"D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow\comfyui_ui_virtual_host_sdxl_to_wan_workflow.json")


def node(node_id, node_type, pos, widgets=None):
    return {
        "id": node_id,
        "type": node_type,
        "pos": pos,
        "size": [320, 120],
        "flags": {},
        "order": node_id,
        "mode": 0,
        "inputs": [],
        "outputs": [],
        "properties": {"Node name for S&R": node_type},
        "widgets_values": widgets or [],
    }


nodes = [
    node(1, "LoadImage", [40, 120], ["scene_4_480x832.jpg"]),
    node(2, "LoadImageMask", [40, 320], ["scene_virtual_host_mask.png", "red"]),
    node(3, "DiffusersLoader", [420, 60], ["sdxl_inpaint_1_0_files"]),
    node(
        4,
        "CLIPTextEncode",
        [800, 40],
        [
            "photorealistic fictional AI female KTV host standing naturally inside the exact same luxury private KTV room, full body, elegant black fitted dress, holding a microphone, business reception style, confident gentle smile, matching blue and magenta club lighting, realistic shadows on the floor, correct perspective and scale, commercial photography, high detail face, natural hands, preserve the original room layout"
        ],
    ),
    node(
        5,
        "CLIPTextEncode",
        [800, 250],
        [
            "low quality, blurry, flicker, jitter, distorted face, bad hands, extra fingers, extra limbs, duplicate person, warped room, changed layout, text, logo, watermark, cartoon, anime, plastic skin, overexposed, oversaturated"
        ],
    ),
    node(6, "InpaintModelConditioning", [1180, 160], [True]),
    node(7, "KSampler", [1540, 160], [2026052742, "fixed", 32, 7.0, "dpmpp_2m", "karras", 1.0]),
    node(8, "VAEDecode", [1900, 160], []),
    node(9, "SaveImage", [2260, 60], ["aiops_virtual_host_sdxl_inpaint"]),
    node(10, "WanVideoVAELoader", [2260, 280], ["wan2.2_vae.safetensors", "bf16", False, False]),
    node(11, "WanVideoEncode", [2620, 280], [False, 272, 272, 144, 128, 0.018, 0.94]),
    node(12, "WanVideoEmptyEmbeds", [2980, 280], [480, 832, 33]),
    node(
        13,
        "WanVideoTextEncodeCached",
        [2980, 40],
        [
            "umt5-xxl-enc-bf16.safetensors",
            "bf16",
            "A fictional AI female KTV host in the same luxury private room gently moves, slight breathing, subtle hand gesture with microphone, stable face, stable outfit, cinematic commercial lighting.",
            "low quality, blurry, flicker, jitter, distorted face, bad hands, extra fingers, extra limbs, duplicate person, warped room, changed layout, text, logo, watermark, cartoon, anime, plastic skin, overexposed, oversaturated",
            "disabled",
            True,
            "gpu",
        ],
    ),
    node(14, "WanVideoBlockSwap", [3340, 470], [18, False, False, True, 0, 1, False]),
    node(
        15,
        "WanVideoModelLoader",
        [3700, 280],
        [r"Wan2.2\wan2.2_ti2v_5B_fp16.safetensors", "fp16_fast", "disabled", "offload_device", "sdpa", "default"],
    ),
    node(16, "WanVideoEasyCache", [3700, 470], [0.015, 8, -1, "offload_device"]),
    node(17, "WanVideoSLG", [3700, 620], ["7,8,9", 0.1, 0.7]),
    node(18, "WanVideoSampler", [4060, 280], [24, 4.5, 8.0, 2026052741, True, "flowmatch_pusa", 0, 1.0, False, "comfy", 0, -1, False]),
    node(19, "WanVideoDecode", [4420, 280], [True, 272, 272, 144, 128, "default"]),
    node(20, "VHS_VideoCombine", [4780, 280], [16, 0, "aiops_virtual_host_wan_i2v", "video/h264-mp4", "yuv420p", 19, True, False, False, True]),
]

links = [
    [1, 3, 0, 4, 1, "CLIP"],
    [2, 3, 0, 5, 1, "CLIP"],
    [3, 4, 0, 6, 0, "CONDITIONING"],
    [4, 5, 0, 6, 1, "CONDITIONING"],
    [5, 3, 2, 6, 2, "VAE"],
    [6, 1, 0, 6, 3, "IMAGE"],
    [7, 2, 0, 6, 4, "MASK"],
    [8, 3, 0, 7, 0, "MODEL"],
    [9, 6, 0, 7, 1, "CONDITIONING"],
    [10, 6, 1, 7, 2, "CONDITIONING"],
    [11, 6, 2, 7, 3, "LATENT"],
    [12, 7, 0, 8, 0, "LATENT"],
    [13, 3, 2, 8, 1, "VAE"],
    [14, 8, 0, 9, 0, "IMAGE"],
    [15, 3, 2, 10, 0, "VAE"],
    [16, 8, 0, 11, 1, "IMAGE"],
    [17, 10, 0, 11, 0, "VAE"],
    [18, 11, 0, 12, 3, "LATENT"],
    [19, 14, 0, 15, 5, "WANVIDEOBLOCKSWAP"],
    [20, 15, 0, 18, 0, "MODEL"],
    [21, 12, 0, 18, 1, "WANVIDIMAGE_EMBEDS"],
    [22, 13, 0, 18, 2, "WANVIDTEXT_EMBEDS"],
    [23, 16, 0, 18, 8, "WANVIDEOCACHEARGS"],
    [24, 17, 0, 18, 9, "WANVIDEOSLGARGS"],
    [25, 10, 0, 19, 0, "VAE"],
    [26, 18, 0, 19, 1, "LATENT"],
    [27, 19, 0, 20, 0, "IMAGE"],
]

node_by_id = {n["id"]: n for n in nodes}
for link_id, src, src_slot, dst, dst_slot, typ in links:
    node_by_id[src]["outputs"].append({"name": typ, "type": typ, "links": [link_id], "slot_index": src_slot})
    node_by_id[dst]["inputs"].append({"name": typ, "type": typ, "link": link_id})

workflow = {
    "last_node_id": max(node_by_id),
    "last_link_id": max(link[0] for link in links),
    "nodes": nodes,
    "links": links,
    "groups": [
        {"title": "1. 场景图生成 AI 虚拟美女关键帧", "bounding": [20, 20, 2260, 650], "color": "#3f789e", "font_size": 24},
        {"title": "2. Wan I2V 把关键帧生成短视频", "bounding": [2240, 220, 2880, 650], "color": "#8e6f3e", "font_size": 24},
    ],
    "config": {},
    "extra": {"ds": {"scale": 0.55, "offset": [60, 60]}},
    "version": 0.4,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(OUT)
