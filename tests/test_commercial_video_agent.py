"""Commercial video specialist Agent tests."""

from __future__ import annotations

from app.commercial_operations.video_agent import CommercialVideoAgent


def test_video_agent_selects_cu130_workflows_for_original_scene_to_ai_host_requirement() -> None:
    agent = CommercialVideoAgent()

    payload = agent.plan(
        operation={
            "id": "operation-video-1",
            "workspace_id": "workspace-video",
            "title": "Douyin KTV AI virtual host video",
            "objective": "Use one KTV scene image to generate a same-scene video with a fictional AI female host.",
        },
        request_context={
            "channel": "short_video",
            "target_channels": ["douyin"],
            "style": "KTV commercial short video",
            "scene_image_uri": "file:///D:/ai-operations-system/douyin_frames/frame_004.jpg",
            "source_video_uri": "file:///D:/ai-operations-system/douyin_7575632283172932870.mp4",
            "needs_ai_virtual_person": True,
            "allow_real_person_cutout": False,
            "aspect_ratio": "9:16",
            "duration_seconds": 12,
            "metadata": {"reference_video_intent": "structure_learning"},
        },
        rag_context={"used_retrieval": False, "rag_result_count": 0, "query": "KTV Douyin digital human video"},
    )

    source = payload["video_agent_plan"]["source_understanding"]
    assert source["primary_character_source"] == "ai_generated_fictional_host"
    assert source["allow_real_person_cutout"] is False
    assert source["has_scene_image"] is True
    assert source["has_reference_video"] is True

    runtime = payload["runtime_evidence"]
    assert runtime["runtime_audit_available"] is True
    assert runtime["workflow_candidate_count"] >= 100
    assert runtime["workflow_capability_counts"]["image_to_video"] >= 1
    assert runtime["workflow_capability_counts"]["digital_human"] >= 1

    selection = payload["workflow_selection"]["selected_by_stage"]
    assert selection["reference_video_analysis"]["status"] == "candidate_selected"
    assert selection["ai_virtual_host_seed"]["selected"][0]["workflow_name"]
    assert "InfiniteTalk" in selection["digital_human_i2v"]["selected"][0]["workflow_name"]

    package = payload["execution_package"]
    assert package["status"] == "ready_for_review"
    assert package["readiness"]["blocking_conditions"] == []
    assert "no_real_person_portrait_cutout_unless_operator_overrides" in package["forbidden_actions"]
    assert package["parameter_plan"]["width"] == 1080
    assert package["parameter_plan"]["height"] == 1920


def test_video_agent_blocks_scene_image_route_without_scene_material() -> None:
    agent = CommercialVideoAgent()

    payload = agent.plan(
        operation={"id": "operation-video-2", "workspace_id": "workspace-video", "objective": "KTV video"},
        request_context={
            "channel": "short_video",
            "needs_ai_virtual_person": True,
            "allow_real_person_cutout": False,
            "metadata": {},
        },
        rag_context={"used_retrieval": False, "rag_result_count": 0},
    )

    package = payload["execution_package"]
    assert package["status"] == "blocked"
    assert "scene_image_required_for_scene_to_ai_virtual_host_video" in package["readiness"]["blocking_conditions"]
    assert package["workflow_stages"]["motion_transfer"]["status"] == "skipped"
