"""LLM-backed creative planning for digital human video jobs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import re
from typing import Any

from app.agents.llm_client import LLMClient
from app.models.digital_human import DigitalHumanAsset
from app.schemas.llm import LLMRequest, LLMResponse


class DigitalHumanCreativePlanner:
    """Turn a business goal and materials into a director-grade video plan."""

    def __init__(self, *, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def generate_plan(
        self,
        *,
        objective: str,
        script: str,
        avatar_asset: DigitalHumanAsset | None,
        material_assets: Sequence[DigitalHumanAsset],
        reference_assets: Sequence[DigitalHumanAsset],
        target_channels: Sequence[str],
        voice_profile: Mapping[str, object],
        aspect_ratio: str,
        duration_seconds: float | None,
        planning_context: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Ask the configured LLM for story, character, shot, and quality plans."""

        if self._prefer_fast_seed_planning(planning_context):
            seed_direction = await self._generate_seed_direction(
                objective=objective,
                script=script,
                target_channels=target_channels,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration_seconds,
            )
            response = LLMResponse(
                provider=str(getattr(getattr(self.llm_client, "provider", None), "provider_name", "unknown")),
                model=str(getattr(getattr(self.llm_client, "provider", None), "model", "unknown")),
                content=seed_direction,
                usage={},
                metadata={"fallback_mode": "fast_seed_planning", "seed_direction": seed_direction},
            )
            plan = self._normalize_plan(
                None,
                response=response,
                objective=objective,
                script=seed_direction or script,
                avatar_asset=avatar_asset,
                material_assets=material_assets,
                reference_assets=reference_assets,
                duration_seconds=duration_seconds,
            )
            if seed_direction:
                intent = plan.get("production_intent") if isinstance(plan.get("production_intent"), dict) else {}
                plan["production_intent"] = {
                    **intent,
                    "narrative_angle": seed_direction,
                }
                plan["llm_seed_direction"] = seed_direction
                if isinstance(plan.get("llm_planning"), dict):
                    plan["llm_planning"]["status"] = "generated_seed_direction"
            return plan

        request = LLMRequest(
            system_prompt=self._system_prompt(),
            user_prompt=self._user_prompt(
                objective=objective,
                script=script,
                avatar_asset=avatar_asset,
                material_assets=material_assets,
                reference_assets=reference_assets,
                target_channels=target_channels,
                voice_profile=voice_profile,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration_seconds,
                planning_context=planning_context,
            ),
            temperature=0.35,
            max_tokens=2200,
        )
        try:
            response = await self.llm_client.generate(request)
        except Exception as exc:
            seed_direction = await self._generate_seed_direction(
                objective=objective,
                script=script,
                target_channels=target_channels,
                aspect_ratio=aspect_ratio,
                duration_seconds=duration_seconds,
            )
            response = LLMResponse(
                provider=str(getattr(getattr(self.llm_client, "provider", None), "provider_name", "unknown")),
                model=str(getattr(getattr(self.llm_client, "provider", None), "model", "unknown")),
                content="",
                usage={},
                metadata={
                    "fallback_reason": str(exc),
                    "fallback_mode": "llm_generation_failed",
                    "seed_direction": seed_direction,
                },
            )
            plan = self._normalize_plan(
                None,
                response=response,
                objective=objective,
                script=seed_direction or script,
                avatar_asset=avatar_asset,
                material_assets=material_assets,
                reference_assets=reference_assets,
                duration_seconds=duration_seconds,
            )
            if seed_direction:
                intent = plan.get("production_intent") if isinstance(plan.get("production_intent"), dict) else {}
                plan["production_intent"] = {
                    **intent,
                    "narrative_angle": seed_direction,
                }
                plan["llm_seed_direction"] = seed_direction
            return plan
        parsed = self._parse_json_object(response.content)
        return self._normalize_plan(
            parsed,
            response=response,
            objective=objective,
            script=script,
            avatar_asset=avatar_asset,
            material_assets=material_assets,
            reference_assets=reference_assets,
            duration_seconds=duration_seconds,
        )

    def _system_prompt(self) -> str:
        return (
            "You are an executive creative director and video production planner for premium short-form commercial videos. "
            "Return one strict JSON object only. Do not wrap it in Markdown. Plan for a coherent, high-quality, character-consistent AI video, "
            "not a raw montage. Materials are references for venue, lighting, products, and identity continuity; the output should be newly generated "
            "and directed. The plan must be specific enough for ComfyUI/Wan I2V/T2V/MuseTalk/voice/ffmpeg orchestration."
        )

    def _prefer_fast_seed_planning(self, planning_context: Mapping[str, object] | None) -> bool:
        if not isinstance(planning_context, Mapping):
            return False
        route_decision = planning_context.get("route_decision")
        if isinstance(route_decision, Mapping) and bool(route_decision.get("prefer_fast_seed_planning")):
            return True
        return bool(planning_context.get("prefer_fast_seed_planning"))

    async def _generate_seed_direction(
        self,
        *,
        objective: str,
        script: str,
        target_channels: Sequence[str],
        aspect_ratio: str,
        duration_seconds: float | None,
    ) -> str:
        """Ask the LLM for a short creative direction when full JSON planning times out."""

        try:
            response = await self.llm_client.generate(
                LLMRequest(
                    system_prompt=(
                        "You are a senior creative director. Return one concise paragraph only. "
                        "No Markdown, no bullets, no JSON."
                    ),
                    user_prompt=(
                        "Give a concrete creative direction for a realistic premium short video. "
                        "Mention story, camera language, host identity, natural voice, and how uploaded materials should be used as references.\n"
                        f"Objective: {objective[:800]}\n"
                        f"Script brief: {script[:600]}\n"
                        f"Channels: {list(target_channels)}\n"
                        f"Aspect ratio: {aspect_ratio}; duration seconds: {duration_seconds or 'auto'}"
                    ),
                    temperature=0.3,
                    max_tokens=160,
                )
            )
            return response.content.strip()[:1200]
        except Exception:
            return ""

    def _user_prompt(
        self,
        *,
        objective: str,
        script: str,
        avatar_asset: DigitalHumanAsset | None,
        material_assets: Sequence[DigitalHumanAsset],
        reference_assets: Sequence[DigitalHumanAsset],
        target_channels: Sequence[str],
        voice_profile: Mapping[str, object],
        aspect_ratio: str,
        duration_seconds: float | None,
        planning_context: Mapping[str, object] | None,
    ) -> str:
        payload = {
            "objective": objective,
            "initial_script_or_operator_brief": script,
            "avatar_asset": self._asset_summary(avatar_asset) if avatar_asset else None,
            "material_asset_count": len(material_assets),
            "material_assets": [self._asset_summary(asset) for asset in material_assets[:8]],
            "omitted_material_asset_count": max(0, len(material_assets) - 8),
            "reference_assets": [self._asset_summary(asset) for asset in reference_assets],
            "target_channels": list(target_channels),
            "voice_profile": dict(voice_profile),
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration_seconds,
            "planning_context": dict(planning_context or {}),
            "required_json_schema": {
                "production_intent": {
                    "positioning": "string",
                    "target_audience": "string",
                    "narrative_angle": "string",
                    "value_proposition": "string",
                },
                "character_bible": {
                    "identity_role": "string",
                    "personality": "string",
                    "visual_identity": "string",
                    "wardrobe": "string",
                    "continuity_rules": ["string"],
                },
                "voiceover": {
                    "final_script": "string",
                    "tone": "string",
                    "pacing": "string",
                    "ai_voice_avoidance": ["string"],
                },
                "story_beats": ["string"],
                "shot_plan": [
                    {
                        "shot_id": "S01",
                        "duration_seconds": 3.0,
                        "scene_goal": "string",
                        "camera": "string",
                        "visual_prompt": "string",
                        "negative_prompt": "string",
                        "reference_asset_usage": "string",
                        "character_continuity": "string",
                        "audio_line": "string",
                        "quality_checks": ["string"],
                    }
                ],
                "asset_strategy": {
                    "material_reference_policy": "string",
                    "generated_scene_policy": "string",
                    "no_raw_montage_rule": "string",
                },
                "comfyui_plan": {
                    "recommended_template": "string",
                    "model_family": "string",
                    "resolution": "string",
                    "fps": 24,
                    "generation_passes": ["string"],
                },
                "quality_gates": ["string"],
                "risk_notes": ["string"],
                "approval_checklist": ["string"],
            },
            "planning_limits": {
                "shot_count": "Return 6 concise shots unless the brief explicitly needs fewer.",
                "prompt_length": "Keep each visual_prompt below 80 Chinese characters or 60 English words.",
                "voiceover_length": "Keep final_script suitable for the requested duration.",
            },
        }
        return (
            "Create the production plan in Chinese unless asset names require another language. "
            "The user requires a coherent video with a unified person, real premium scenes, professional camera design, and non-robotic voice. "
            "Use the following structured brief:\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

    def _normalize_plan(
        self,
        parsed: Mapping[str, Any] | None,
        *,
        response: LLMResponse,
        objective: str,
        script: str,
        avatar_asset: DigitalHumanAsset | None,
        material_assets: Sequence[DigitalHumanAsset],
        reference_assets: Sequence[DigitalHumanAsset],
        duration_seconds: float | None,
    ) -> dict[str, Any]:
        plan = dict(parsed or {})
        plan.setdefault(
            "production_intent",
            {
                "positioning": objective,
                "target_audience": "commercial short video viewers",
                "narrative_angle": "operator-led premium service story",
                "value_proposition": objective,
            },
        )
        plan.setdefault(
            "character_bible",
            {
                "identity_role": "brand operator / digital host",
                "personality": "confident, natural, professional",
                "visual_identity": self._asset_summary(avatar_asset).get("name") if avatar_asset else "authorized avatar",
                "wardrobe": "consistent with provided portrait or operator-approved wardrobe",
                "continuity_rules": [
                    "Keep the same face identity across all avatar shots.",
                    "Keep wardrobe, hairstyle, and body proportions stable.",
                    "Do not replace the host with a different person between shots.",
                ],
            },
        )
        plan.setdefault(
            "voiceover",
            {
                "final_script": script,
                "tone": "natural business vlog, calm and human",
                "pacing": "medium-slow with short pauses",
                "ai_voice_avoidance": ["avoid sales-announcer cadence", "avoid flat rhythm", "avoid exaggerated emotion"],
            },
        )
        plan.setdefault("story_beats", self._fallback_story_beats(objective=objective))
        plan["shot_plan"] = self._normalize_shot_plan(
            plan.get("shot_plan"),
            objective=objective,
            script=script,
            material_assets=material_assets,
            reference_assets=reference_assets,
            duration_seconds=duration_seconds,
        )
        plan.setdefault(
            "asset_strategy",
            {
                "material_reference_policy": "Use uploaded materials as spatial, lighting, product, and identity references instead of raw montage filler.",
                "generated_scene_policy": "Generate coherent new shots that preserve reference venue details and maintain one host identity.",
                "no_raw_montage_rule": "Every shot must have a story function, camera intention, and quality checks.",
            },
        )
        plan.setdefault(
            "comfyui_plan",
            {
                "recommended_template": "wan-i2v-reference-avatar",
                "model_family": "Wan I2V/T2V plus local digital-human lip-sync",
                "resolution": "1080x1920 target after preview validation",
                "fps": 24,
                "generation_passes": ["character lock", "scene generation", "lip sync", "quality review", "final compose"],
            },
        )
        plan.setdefault(
            "quality_gates",
            [
                "The host identity remains consistent across generated and lip-sync shots.",
                "The video contains a clear story arc, not unrelated clips.",
                "Reference materials influence scene layout, lighting, and mood.",
                "Voiceover sounds like a normal operator speaking, not a generic ad read.",
            ],
        )
        plan.setdefault("risk_notes", [])
        plan.setdefault("approval_checklist", [])
        plan["llm_planning"] = {
            "status": "generated" if parsed else "generated_unstructured_fallback",
            "provider": response.provider,
            "model": response.model,
            "usage": response.usage,
            "metadata": response.metadata,
            "raw_response_excerpt": response.content[:2000],
        }
        return plan

    def _normalize_shot_plan(
        self,
        value: Any,
        *,
        objective: str,
        script: str,
        material_assets: Sequence[DigitalHumanAsset],
        reference_assets: Sequence[DigitalHumanAsset],
        duration_seconds: float | None,
    ) -> list[dict[str, Any]]:
        shots = value if isinstance(value, list) else []
        normalized: list[dict[str, Any]] = []
        for index, raw_shot in enumerate(shots[:12], start=1):
            if not isinstance(raw_shot, Mapping):
                continue
            normalized.append(self._shot_record(index=index, raw_shot=raw_shot))
        if normalized:
            return normalized

        total = float(duration_seconds or 30.0)
        default_duration = round(max(2.0, total / 6.0), 2)
        material_names = ", ".join(asset.name for asset in [*material_assets, *reference_assets][:4]) or "uploaded venue/material references"
        fallback_goals = [
            "establish the premium venue and business atmosphere",
            "introduce the unified digital host as the operator",
            "show the service details and room environment",
            "show customer reception flow and emotional value",
            "deliver the core proof and trust statement",
            "close with a clear booking or visit invitation",
        ]
        return [
            {
                "shot_id": f"S{index:02d}",
                "duration_seconds": default_duration,
                "scene_goal": goal,
                "camera": "cinematic vertical camera movement with stable composition",
                "visual_prompt": f"{objective}; use {material_names} as reference; coherent premium realistic commercial video",
                "negative_prompt": "raw montage, identity drift, deformed face, inconsistent outfit, low resolution, text artifacts, flicker",
                "reference_asset_usage": "Use materials as reference for venue layout, lighting, and mood; do not simply splice them.",
                "character_continuity": "Same host identity, same wardrobe logic, same age and facial features across the shot.",
                "audio_line": script if index == 2 else "",
                "quality_checks": ["identity_consistency", "scene_continuity", "camera_intent", "premium_realism"],
            }
            for index, goal in enumerate(fallback_goals, start=1)
        ]

    def _shot_record(self, *, index: int, raw_shot: Mapping[str, Any]) -> dict[str, Any]:
        shot_id = str(raw_shot.get("shot_id") or f"S{index:02d}").strip()[:32]
        duration = raw_shot.get("duration_seconds")
        try:
            duration_seconds = max(0.5, min(float(duration), 30.0))
        except (TypeError, ValueError):
            duration_seconds = 3.0
        return {
            "shot_id": shot_id or f"S{index:02d}",
            "duration_seconds": duration_seconds,
            "scene_goal": str(raw_shot.get("scene_goal") or "planned story shot").strip(),
            "camera": str(raw_shot.get("camera") or "stable cinematic vertical camera").strip(),
            "visual_prompt": str(raw_shot.get("visual_prompt") or "").strip(),
            "negative_prompt": str(raw_shot.get("negative_prompt") or "").strip(),
            "reference_asset_usage": str(raw_shot.get("reference_asset_usage") or "").strip(),
            "character_continuity": str(raw_shot.get("character_continuity") or "").strip(),
            "audio_line": str(raw_shot.get("audio_line") or "").strip(),
            "quality_checks": [str(item) for item in raw_shot.get("quality_checks", []) if str(item).strip()]
            if isinstance(raw_shot.get("quality_checks"), list)
            else [],
        }

    def _fallback_story_beats(self, *, objective: str) -> list[str]:
        return [
            f"Open with the premium atmosphere behind {objective}.",
            "Introduce the operator/host and the concrete service standard.",
            "Show venue, service flow, and trust proof through generated scenes.",
            "Close with a clear promise and action.",
        ]

    def _parse_json_object(self, content: str) -> Mapping[str, Any] | None:
        text = str(content or "").strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return parsed if isinstance(parsed, Mapping) else None

    def _asset_summary(self, asset: DigitalHumanAsset) -> dict[str, Any]:
        return {
            "asset_id": str(asset.id),
            "asset_type": asset.asset_type,
            "name": asset.name,
            "file_name": asset.file_name,
            "mime_type": asset.mime_type,
            "source_uri": asset.source_uri,
            "consent_status": asset.consent_status,
            "usage_scope": asset.usage_scope,
            "metadata": asset.asset_metadata or {},
        }
