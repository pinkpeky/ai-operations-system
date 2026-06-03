"""ComfyUI workflow materialization safety tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.comfyui_runtime.workflow_materializer import ComfyUIWorkflowMaterializer


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_materializer_patches_api_prompt_copy_without_overwriting_source(tmp_path: Path) -> None:
    source = tmp_path / "wan_api_workflow.json"
    source.write_text(
        json.dumps(
            {
                "1": {"class_type": "LoadImage", "inputs": {"image": "old.png"}},
                "2": {
                    "class_type": "WanVideoTextEncodeCached",
                    "inputs": {
                        "positive_prompt": "old positive",
                        "negative_prompt": "old negative",
                    },
                },
                "3": {
                    "class_type": "VHS_VideoCombine",
                    "inputs": {"filename_prefix": "old/prefix", "frame_rate": 16},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    before = _sha256(source)

    result = ComfyUIWorkflowMaterializer(output_root=tmp_path / "materialized").materialize(
        source_workflow_path=source,
        stage_key="digital_human_i2v",
        run_id="run-001",
        input_assets={"approved_keyframe_name": "scene_ai_host.png"},
        parameter_plan={
            "character_prompt": "fictional adult AI female KTV host",
            "scene_prompt": "same neon KTV room",
            "motion_prompt": "subtle presenter movement",
            "negative_prompt": "bad hands, warped room",
            "fps": 24,
        },
    )

    assert result.original_unchanged is True
    assert result.source_sha256_before == before
    assert result.source_sha256_after == before
    assert _sha256(source) == before
    assert result.materialized_workflow_path != result.source_workflow_path
    materialized = json.loads(Path(result.materialized_workflow_path).read_text(encoding="utf-8"))
    assert materialized["1"]["inputs"]["image"] == "scene_ai_host.png"
    assert "fictional adult AI female KTV host" in materialized["2"]["inputs"]["positive_prompt"]
    assert materialized["2"]["inputs"]["negative_prompt"] == "bad hands, warped room"
    assert materialized["3"]["inputs"]["filename_prefix"].startswith("aiops/run-001/digital_human_i2v/")
    assert materialized["3"]["inputs"]["frame_rate"] == 24.0
    assert result.injected_change_count >= 5
    assert result.materialization_policy["source_workflow_is_read_only"] is True


def test_materializer_patches_ui_workflow_widgets_and_allocates_unique_copy(tmp_path: Path) -> None:
    source = tmp_path / "ui_workflow.json"
    source.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": 317,
                        "type": "WanVideoTextEncode",
                        "inputs": [
                            {"name": "positive_prompt", "widget": {"name": "positive_prompt"}},
                            {"name": "negative_prompt", "widget": {"name": "negative_prompt"}},
                            {"name": "device", "widget": {"name": "device"}},
                        ],
                        "widgets_values": ["old positive", "old negative", "gpu"],
                    },
                    {
                        "id": 284,
                        "type": "LoadImage",
                        "inputs": [
                            {"name": "image", "widget": {"name": "image"}},
                            {"name": "upload", "widget": {"name": "upload"}},
                        ],
                        "widgets_values": ["old.png", "image"],
                    },
                    {
                        "id": 131,
                        "type": "VHS_VideoCombine",
                        "widgets_values": {
                            "frame_rate": 16,
                            "filename_prefix": "old/video",
                        },
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    before = _sha256(source)
    materializer = ComfyUIWorkflowMaterializer(output_root=tmp_path / "materialized")

    first = materializer.materialize(
        source_workflow_path=source,
        stage_key="digital_human_i2v",
        run_id="same-run",
        input_assets={"scene_image_name": "scene.png"},
        parameter_plan={
            "positive_prompt": "new presenter prompt",
            "negative_prompt": "new negative prompt",
            "fps": 24,
        },
    )
    second = materializer.materialize(
        source_workflow_path=source,
        stage_key="digital_human_i2v",
        run_id="same-run",
        input_assets={"scene_image_name": "scene.png"},
        parameter_plan={"positive_prompt": "another prompt", "negative_prompt": "new negative prompt"},
    )

    assert _sha256(source) == before
    assert first.original_unchanged is True
    assert second.original_unchanged is True
    assert first.materialized_workflow_path != second.materialized_workflow_path
    materialized = json.loads(Path(first.materialized_workflow_path).read_text(encoding="utf-8"))
    assert materialized["nodes"][0]["widgets_values"][0] == "new presenter prompt"
    assert materialized["nodes"][0]["widgets_values"][1] == "new negative prompt"
    assert materialized["nodes"][1]["widgets_values"][0] == "scene.png"
    assert materialized["nodes"][2]["widgets_values"]["frame_rate"] == 24.0
    assert materialized["nodes"][2]["widgets_values"]["filename_prefix"].startswith("aiops/same-run/digital_human_i2v/")


def test_materializer_supports_exact_node_overrides(tmp_path: Path) -> None:
    source = tmp_path / "qwen_ui_workflow.json"
    source.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": 6,
                        "type": "TextEncodeQwenImageEditPlus",
                        "inputs": [{"name": "prompt", "widget": {"name": "prompt"}}],
                        "widgets_values": ["old qwen edit prompt"],
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = ComfyUIWorkflowMaterializer(output_root=tmp_path / "materialized").materialize(
        source_workflow_path=source,
        stage_key="ai_virtual_host_seed",
        run_id="override-run",
        parameter_plan={"positive_prompt": "generic prompt"},
        node_overrides={"6": {"prompt": "exact Qwen edit instruction"}},
    )

    materialized = json.loads(Path(result.materialized_workflow_path).read_text(encoding="utf-8"))
    assert materialized["nodes"][0]["widgets_values"][0] == "exact Qwen edit instruction"
    assert result.injected_changes[0]["node_id"] == "6"


def test_ui_workflow_to_api_prompt_preserves_links_and_widget_inputs() -> None:
    workflow = {
        "nodes": [
            {"id": 99, "type": "MarkdownNote", "widgets_values": ["operator note"]},
            {
                "id": 1,
                "type": "LoadImage",
                "inputs": [
                    {"name": "image", "widget": {"name": "image"}},
                    {"name": "upload", "widget": {"name": "upload"}},
                ],
                "widgets_values": ["scene.png", "image"],
            },
            {
                "id": 2,
                "type": "VHS_VideoCombine",
                "inputs": [
                    {"name": "images", "link": 10},
                    {"name": "frame_rate", "widget": {"name": "frame_rate"}},
                    {"name": "filename_prefix", "widget": {"name": "filename_prefix"}},
                ],
                "widgets_values": [24, "old/output"],
            },
        ],
        "links": [[10, 1, 0, 2, 0, "IMAGE"]],
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert api_prompt["1"]["class_type"] == "LoadImage"
    assert api_prompt["1"]["inputs"]["image"] == "scene.png"
    assert api_prompt["2"]["inputs"]["images"] == ["1", 0]
    assert api_prompt["2"]["inputs"]["frame_rate"] == 24
    assert api_prompt["2"]["inputs"]["filename_prefix"] == "old/output"
    assert "99" not in api_prompt


def test_ui_workflow_to_api_prompt_resolves_set_get_nodes() -> None:
    workflow = {
        "nodes": [
            {
                "id": 1,
                "type": "LoadImage",
                "inputs": [{"name": "image", "widget": {"name": "image"}}],
                "widgets_values": ["scene.png"],
                "outputs": [{"name": "IMAGE", "links": [10]}],
            },
            {
                "id": 2,
                "type": "SetNode",
                "inputs": [{"name": "IMAGE", "link": 10}],
                "widgets_values": ["reference_image"],
                "outputs": [{"name": "*", "links": []}],
            },
            {
                "id": 3,
                "type": "GetNode",
                "widgets_values": ["reference_image"],
                "outputs": [{"name": "IMAGE", "links": [20]}],
            },
            {
                "id": 4,
                "type": "VHS_VideoCombine",
                "inputs": [
                    {"name": "images", "link": 20},
                    {"name": "frame_rate", "widget": {"name": "frame_rate"}},
                    {"name": "filename_prefix", "widget": {"name": "filename_prefix"}},
                ],
                "widgets_values": [16, "old/output"],
            },
        ],
        "links": [
            [10, 1, 0, 2, 0, "IMAGE"],
            [20, 3, 0, 4, 0, "IMAGE"],
        ],
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert set(api_prompt) == {"1", "4"}
    assert api_prompt["4"]["inputs"]["images"] == ["1", 0]


def test_ui_workflow_to_api_prompt_resolves_direct_setnode_outputs() -> None:
    workflow = {
        "nodes": [
            {
                "id": 1,
                "type": "LoadImage",
                "inputs": [{"name": "image", "widget": {"name": "image"}}],
                "widgets_values": ["scene.png"],
                "outputs": [{"name": "IMAGE", "links": [10]}],
            },
            {
                "id": 2,
                "type": "SetNode",
                "inputs": [{"name": "IMAGE", "link": 10}],
                "widgets_values": ["poses"],
                "outputs": [{"name": "IMAGE", "links": [20]}],
            },
            {
                "id": 3,
                "type": "VHS_VideoCombine",
                "inputs": [{"name": "images", "link": 20}],
            },
        ],
        "links": [
            [10, 1, 0, 2, 0, "IMAGE"],
            [20, 2, 0, 3, 0, "IMAGE"],
        ],
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert set(api_prompt) == {"1", "3"}
    assert api_prompt["3"]["inputs"]["images"] == ["1", 0]


def test_ui_workflow_to_api_prompt_drops_links_from_disabled_nodes() -> None:
    workflow = {
        "nodes": [
            {
                "id": 1,
                "type": "DisabledOptionalSource",
                "mode": 4,
                "outputs": [{"name": "ARGS", "links": [10]}],
            },
            {
                "id": 2,
                "type": "ModelLoader",
                "inputs": [{"name": "compile_args", "link": 10}],
            },
        ],
        "links": [[10, 1, 0, 2, 0, "ARGS"]],
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert set(api_prompt) == {"2"}
    assert "compile_args" not in api_prompt["2"]["inputs"]


def test_ui_workflow_to_api_prompt_skips_disabled_nodes() -> None:
    workflow = {
        "nodes": [
            {
                "id": 1,
                "type": "DisabledLoader",
                "mode": 4,
                "inputs": [{"name": "required_image"}],
                "widgets_values": [],
            },
            {
                "id": 2,
                "type": "LoadImage",
                "inputs": [{"name": "image", "widget": {"name": "image"}}],
                "widgets_values": ["scene.png"],
            },
        ]
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert set(api_prompt) == {"2"}


def test_ui_workflow_to_api_prompt_skips_rgthree_ui_nodes() -> None:
    workflow = {
        "nodes": [
            {"id": 1, "type": "Fast Groups Muter (rgthree)", "widgets_values": {}},
            {"id": 2, "type": "Label (rgthree)", "widgets_values": {}},
            {
                "id": 3,
                "type": "LoadImage",
                "inputs": [{"name": "image", "widget": {"name": "image"}}],
                "widgets_values": ["scene.png"],
            },
        ]
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow)

    assert set(api_prompt) == {"3"}


def test_ui_workflow_to_api_prompt_preserves_upload_subfolder_paths_with_object_info() -> None:
    workflow = {
        "nodes": [
            {
                "id": 1,
                "type": "LoadImage",
                "inputs": [
                    {"name": "image", "widget": {"name": "image"}},
                    {"name": "upload", "widget": {"name": "upload"}},
                ],
                "widgets_values": ["商k/场景/room.png", "image"],
            },
        ]
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(
        workflow,
        object_info={
            "LoadImage": {
                "input": {
                    "required": {
                        "image": [["root_only.png"], {"image_upload": True}],
                    }
                }
            }
        },
    )

    preflight = ComfyUIWorkflowMaterializer().preflight_api_prompt(
        api_prompt,
        object_info={
            "LoadImage": {
                "input": {
                    "required": {
                        "image": [["root_only.png"], {"image_upload": True}],
                    }
                }
            }
        },
    )

    assert api_prompt["1"]["inputs"]["image"] == "商k/场景/room.png"
    assert preflight["prompt_ready"] is True


def test_materialize_api_prompt_writes_prompt_and_keeps_source_read_only(tmp_path: Path) -> None:
    source = tmp_path / "linked_ui_workflow.json"
    source.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": 1,
                        "type": "LoadImage",
                        "inputs": [
                            {"name": "image", "widget": {"name": "image"}},
                            {"name": "upload", "widget": {"name": "upload"}},
                        ],
                        "widgets_values": ["old.png", "image"],
                    },
                    {
                        "id": 2,
                        "type": "VHS_VideoCombine",
                        "inputs": [
                            {"name": "images", "link": 20},
                            {"name": "frame_rate", "widget": {"name": "frame_rate"}},
                            {"name": "filename_prefix", "widget": {"name": "filename_prefix"}},
                        ],
                        "widgets_values": [16, "old/output"],
                    },
                ],
                "links": [[20, 1, 0, 2, 0, "IMAGE"]],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    before = _sha256(source)

    result = ComfyUIWorkflowMaterializer(output_root=tmp_path / "materialized").materialize_api_prompt(
        source_workflow_path=source,
        stage_key="digital_human_i2v",
        run_id="api-run",
        input_assets={"scene_image_name": "scene_ai_virtual_host_seed.png"},
        parameter_plan={"fps": 24},
        object_info={
            "LoadImage": {"input": {"required": {"image": {}, "upload": {}}}},
            "VHS_VideoCombine": {
                "input": {"required": {"images": {}, "frame_rate": {}, "filename_prefix": {}}}
            },
        },
    )

    assert result.prompt_ready is True
    assert result.materialization.original_unchanged is True
    assert _sha256(source) == before
    assert result.api_prompt_node_count == 2
    api_prompt = json.loads(Path(result.api_prompt_path).read_text(encoding="utf-8"))
    assert api_prompt["1"]["inputs"]["image"] == "scene_ai_virtual_host_seed.png"
    assert api_prompt["2"]["inputs"]["images"] == ["1", 0]
    assert api_prompt["2"]["inputs"]["frame_rate"] == 24.0
    assert api_prompt["2"]["inputs"]["filename_prefix"].startswith("aiops/api-run/digital_human_i2v/")


def test_preflight_reports_missing_nodes_and_required_inputs_without_false_pair_links() -> None:
    api_prompt = {
        "1": {"class_type": "KnownNode", "inputs": {"size_pair": [1024, 1024]}},
        "2": {"class_type": "MissingNode", "inputs": {"image": ["404", 0]}},
    }

    preflight = ComfyUIWorkflowMaterializer().preflight_api_prompt(
        api_prompt,
        object_info={"KnownNode": {"input": {"required": {"required_text": {}}}}},
    )

    assert preflight["missing_node_types"] == ["MissingNode"]
    reasons = {item["reason"] for item in preflight["unresolved_inputs"]}
    assert "required_input_missing" in reasons
    assert "linked_source_node_missing" in reasons
    assert all(item.get("input_name") != "size_pair" for item in preflight["unresolved_inputs"])


def test_type_aware_ui_conversion_skips_seed_control_widget_values() -> None:
    workflow = {
        "nodes": [
            {
                "id": 128,
                "type": "WanVideoSampler",
                "inputs": [
                    {"name": "steps", "type": "INT", "widget": {"name": "steps"}},
                    {"name": "seed", "type": "INT", "widget": {"name": "seed"}},
                    {"name": "force_offload", "type": "BOOLEAN", "widget": {"name": "force_offload"}},
                    {"name": "scheduler", "type": "COMBO", "widget": {"name": "scheduler"}},
                    {"name": "riflex_freq_index", "type": "INT", "widget": {"name": "riflex_freq_index"}},
                ],
                "widgets_values": [4, 123456, "randomize", True, "dpm++_sde", 0],
            }
        ]
    }
    object_info = {
        "WanVideoSampler": {
            "input": {
                "required": {
                    "steps": ["INT"],
                    "seed": ["INT"],
                    "force_offload": ["BOOLEAN"],
                    "scheduler": [["unipc", "dpm++_sde"]],
                    "riflex_freq_index": ["INT"],
                }
            }
        }
    }

    api_prompt = ComfyUIWorkflowMaterializer().to_api_prompt(workflow, object_info=object_info)

    assert api_prompt["128"]["inputs"] == {
        "steps": 4,
        "seed": 123456,
        "force_offload": True,
        "scheduler": "dpm++_sde",
        "riflex_freq_index": 0,
    }
    assert ComfyUIWorkflowMaterializer().preflight_api_prompt(api_prompt, object_info=object_info)["prompt_ready"] is True


def test_preflight_reports_invalid_widget_value_types() -> None:
    api_prompt = {"128": {"class_type": "WanVideoSampler", "inputs": {"scheduler": True}}}
    object_info = {"WanVideoSampler": {"input": {"required": {"scheduler": [["unipc", "dpm++_sde"]]}}}}

    preflight = ComfyUIWorkflowMaterializer().preflight_api_prompt(api_prompt, object_info=object_info)

    assert preflight["prompt_ready"] is False
    assert preflight["unresolved_inputs"][0]["reason"] == "input_value_type_invalid"
    assert preflight["unresolved_inputs"][0]["input_name"] == "scheduler"
