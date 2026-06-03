"""Materialize ComfyUI workflow copies without mutating source workflows."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATERIALIZED_WORKFLOW_ROOT = PROJECT_ROOT / "storage" / "comfyui_materialized_workflows"


@dataclass(frozen=True)
class WorkflowMaterializationResult:
    """Result metadata for one source-safe workflow materialization."""

    source_workflow_path: str
    materialized_workflow_path: str
    graph_format: str
    source_sha256_before: str
    source_sha256_after: str
    materialized_sha256: str
    original_unchanged: bool
    injected_change_count: int
    injected_changes: list[dict[str, Any]]
    materialization_policy: dict[str, Any]


@dataclass(frozen=True)
class WorkflowPromptBuildResult:
    """A materialized workflow plus the API prompt derived from it."""

    materialization: WorkflowMaterializationResult
    api_prompt_path: str
    api_prompt_sha256: str
    api_prompt_node_count: int
    missing_node_types: list[str]
    unresolved_inputs: list[dict[str, Any]]
    prompt_ready: bool


class ComfyUIWorkflowMaterializer:
    """Create per-run ComfyUI workflow copies with injected prompt parameters.

    The source workflow is treated as immutable. All edits happen on an in-memory
    deep copy that is written under ``output_root``.
    """

    def __init__(self, output_root: Path = DEFAULT_MATERIALIZED_WORKFLOW_ROOT) -> None:
        self.output_root = output_root

    def materialize(
        self,
        *,
        source_workflow_path: str | Path,
        parameter_plan: Mapping[str, Any],
        stage_key: str,
        run_id: str | None = None,
        input_assets: Mapping[str, Any] | None = None,
        node_overrides: Mapping[str, Mapping[str, Any]] | None = None,
        output_prefix: str | None = None,
        output_root: str | Path | None = None,
    ) -> WorkflowMaterializationResult:
        source_path = Path(source_workflow_path).resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Source ComfyUI workflow not found: {source_path}")

        target_root = Path(output_root).resolve() if output_root else self.output_root.resolve()
        source_hash_before = _sha256_file(source_path)
        workflow = json.loads(source_path.read_text(encoding="utf-8"))
        graph = copy.deepcopy(workflow)
        graph_format = self._graph_format(graph)
        changes: list[dict[str, Any]] = []

        plan = dict(parameter_plan or {})
        assets = dict(input_assets or {})
        clean_run_id = _safe_slug(run_id or uuid4().hex[:12])
        clean_stage = _safe_slug(stage_key)
        clean_prefix = output_prefix or f"aiops/{clean_run_id}/{clean_stage}/{_safe_slug(source_path.stem)}"

        if graph_format == "api_prompt":
            self._patch_api_prompt(
                graph=graph,
                parameter_plan=plan,
                input_assets=assets,
                node_overrides=dict(node_overrides or {}),
                output_prefix=clean_prefix,
                changes=changes,
            )
        elif graph_format == "ui_workflow":
            self._patch_ui_workflow(
                graph=graph,
                parameter_plan=plan,
                input_assets=assets,
                node_overrides=dict(node_overrides or {}),
                output_prefix=clean_prefix,
                changes=changes,
            )
        else:
            raise ValueError("Unsupported ComfyUI workflow format; expected API prompt or UI workflow JSON.")

        target_dir = target_root / clean_run_id / clean_stage
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = _unique_path(target_dir / f"{_safe_slug(source_path.stem)}.materialized.json")
        if target_path.resolve() == source_path:
            raise ValueError("Refusing to materialize workflow over the source workflow path.")
        target_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

        source_hash_after = _sha256_file(source_path)
        materialized_hash = _sha256_file(target_path)
        return WorkflowMaterializationResult(
            source_workflow_path=str(source_path),
            materialized_workflow_path=str(target_path),
            graph_format=graph_format,
            source_sha256_before=source_hash_before,
            source_sha256_after=source_hash_after,
            materialized_sha256=materialized_hash,
            original_unchanged=source_hash_before == source_hash_after,
            injected_change_count=len(changes),
            injected_changes=changes,
            materialization_policy={
                "source_workflow_is_read_only": True,
                "writes_only_materialized_copy": True,
                "refuses_source_path_overwrite": True,
                "materialized_at": datetime.now(UTC).isoformat(),
                "output_root": str(target_root),
                "run_id": clean_run_id,
                "stage_key": clean_stage,
            },
        )

    def materialize_api_prompt(
        self,
        *,
        source_workflow_path: str | Path,
        parameter_plan: Mapping[str, Any],
        stage_key: str,
        run_id: str | None = None,
        input_assets: Mapping[str, Any] | None = None,
        node_overrides: Mapping[str, Mapping[str, Any]] | None = None,
        output_prefix: str | None = None,
        output_root: str | Path | None = None,
        object_info: Mapping[str, Any] | None = None,
    ) -> WorkflowPromptBuildResult:
        materialization = self.materialize(
            source_workflow_path=source_workflow_path,
            parameter_plan=parameter_plan,
            stage_key=stage_key,
            run_id=run_id,
            input_assets=input_assets,
            node_overrides=node_overrides,
            output_prefix=output_prefix,
            output_root=output_root,
        )
        materialized_path = Path(materialization.materialized_workflow_path)
        workflow = json.loads(materialized_path.read_text(encoding="utf-8"))
        api_prompt = self.to_api_prompt(workflow, object_info=object_info)
        preflight = self.preflight_api_prompt(api_prompt, object_info=object_info)
        api_prompt_path = materialized_path.with_suffix(".api_prompt.json")
        api_prompt_path = _unique_path(api_prompt_path)
        api_prompt_path.write_text(json.dumps(api_prompt, ensure_ascii=False, indent=2), encoding="utf-8")
        return WorkflowPromptBuildResult(
            materialization=materialization,
            api_prompt_path=str(api_prompt_path),
            api_prompt_sha256=_sha256_file(api_prompt_path),
            api_prompt_node_count=len(api_prompt),
            missing_node_types=preflight["missing_node_types"],
            unresolved_inputs=preflight["unresolved_inputs"],
            prompt_ready=not preflight["missing_node_types"] and not preflight["unresolved_inputs"],
        )

    def to_api_prompt(self, workflow: Mapping[str, Any], *, object_info: Mapping[str, Any] | None = None) -> dict[str, Any]:
        graph_format = self._graph_format(workflow)
        if graph_format == "api_prompt":
            return copy.deepcopy(dict(workflow))
        if graph_format != "ui_workflow":
            raise ValueError("Unsupported ComfyUI workflow format; expected API prompt or UI workflow JSON.")
        return self._ui_workflow_to_api_prompt(dict(workflow), object_info=object_info)

    def preflight_api_prompt(
        self,
        api_prompt: Mapping[str, Any],
        *,
        object_info: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        node_ids = {str(node_id) for node_id in api_prompt.keys()}
        missing_node_types: list[str] = []
        unresolved_inputs: list[dict[str, Any]] = []
        object_info_map = dict(object_info or {})

        for node_id, node in api_prompt.items():
            if not isinstance(node, Mapping):
                unresolved_inputs.append({"node_id": str(node_id), "reason": "node_payload_is_not_mapping"})
                continue
            node_type = str(node.get("class_type") or "")
            inputs = node.get("inputs")
            if not node_type:
                unresolved_inputs.append({"node_id": str(node_id), "reason": "missing_class_type"})
                continue
            if object_info is not None and node_type not in object_info_map:
                missing_node_types.append(node_type)
            if not isinstance(inputs, Mapping):
                unresolved_inputs.append({"node_id": str(node_id), "node_type": node_type, "reason": "missing_inputs"})
                continue
            for input_name, value in inputs.items():
                if _is_prompt_link(value):
                    if str(value[0]) not in node_ids:
                        unresolved_inputs.append(
                            {
                                "node_id": str(node_id),
                                "node_type": node_type,
                                "input_name": str(input_name),
                                "reason": "linked_source_node_missing",
                                "source_node_id": str(value[0]),
                            }
                        )
            if object_info is not None:
                object_info_item = object_info_map.get(node_type)
                for input_name, value in inputs.items():
                    if _is_prompt_link(value):
                        continue
                    input_config = _object_info_input_config(object_info_item, str(input_name))
                    if input_config is not None and not _value_matches_input_config(value, input_config):
                        unresolved_inputs.append(
                            {
                                "node_id": str(node_id),
                                "node_type": node_type,
                                "input_name": str(input_name),
                                "reason": "input_value_type_invalid",
                                "expected": _input_config_preview(input_config),
                                "actual_preview": _preview(value),
                            }
                        )
                required = _object_info_required_inputs(object_info_map.get(node_type))
                for input_name in required:
                    if input_name not in inputs:
                        unresolved_inputs.append(
                            {
                                "node_id": str(node_id),
                                "node_type": node_type,
                                "input_name": input_name,
                                "reason": "required_input_missing",
                            }
                        )
        return {
            "missing_node_types": sorted(set(missing_node_types)),
            "unresolved_inputs": unresolved_inputs,
            "node_count": len(api_prompt),
            "prompt_ready": not missing_node_types and not unresolved_inputs,
        }

    def _ui_workflow_to_api_prompt(
        self,
        graph: dict[str, Any],
        *,
        object_info: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        link_map = self._ui_workflow_link_map(graph)
        object_info_map = dict(object_info or {})
        api_prompt: dict[str, Any] = {}
        for node in graph.get("nodes", []) or []:
            if not isinstance(node, dict):
                continue
            if _is_disabled_ui_node(node):
                continue
            node_id = str(node.get("id") or "")
            node_type = str(node.get("type") or "")
            if not node_id or not node_type:
                continue
            if _is_ui_only_node_type(node_type):
                continue
            inputs: dict[str, Any] = {}
            widget_values = self._widget_value_map(node, object_info_item=object_info_map.get(node_type))
            for raw_input in node.get("inputs", []) or []:
                if not isinstance(raw_input, dict):
                    continue
                name = str(raw_input.get("name") or "")
                if not name:
                    continue
                link_id = raw_input.get("link")
                if link_id is not None and link_id in link_map:
                    source_id, source_slot = link_map[link_id]
                    inputs[name] = [str(source_id), int(source_slot)]
                    continue
                if name in widget_values:
                    inputs[name] = widget_values[name]
            for name, value in widget_values.items():
                inputs.setdefault(name, value)
            api_prompt[node_id] = {"class_type": node_type, "inputs": inputs}
        return api_prompt

    @staticmethod
    def _ui_workflow_link_map(graph: Mapping[str, Any]) -> dict[Any, tuple[str, int]]:
        """Build a UI link map and inline Use Everywhere Set/Get reroutes.

        Some imported ComfyUI workflows use front-end-only SetNode/GetNode
        nodes. The backend API does not execute those nodes, so we rewrite
        links from every GetNode output to the upstream node stored by its
        matching SetNode.
        """

        link_map = ComfyUIWorkflowMaterializer._link_map(list(graph.get("links", []) or []))
        nodes = [node for node in graph.get("nodes", []) or [] if isinstance(node, dict)]
        nodes_by_id = {str(node.get("id")): node for node in nodes if node.get("id") is not None}
        disabled_node_ids = {
            str(node.get("id")) for node in nodes if node.get("id") is not None and _is_disabled_ui_node(node)
        }
        for link in graph.get("links", []) or []:
            if isinstance(link, list) and len(link) >= 2 and str(link[1]) in disabled_node_ids:
                link_map.pop(link[0], None)
        set_sources: dict[str, tuple[str, int]] = {}

        for node in nodes:
            if _is_disabled_ui_node(node):
                continue
            if str(node.get("type") or "").strip().lower() != "setnode":
                continue
            variable_name = _virtual_reroute_name(node)
            source_ref = _first_input_source_ref(node, link_map)
            if variable_name and source_ref is not None:
                set_sources[variable_name] = source_ref

        changed = True
        while changed:
            changed = False
            for node in nodes:
                if _is_disabled_ui_node(node):
                    continue
                node_type = str(node.get("type") or "").strip().lower()
                if node_type == "getnode":
                    variable_name = _virtual_reroute_name(node)
                    source_ref = set_sources.get(variable_name)
                    if source_ref is None:
                        continue
                    resolved = _resolve_virtual_source(source_ref, set_sources, link_map, nodes_by_id)
                    for link_id in _output_link_ids(node):
                        if link_map.get(link_id) != resolved:
                            link_map[link_id] = resolved
                            changed = True
                elif node_type == "setnode":
                    source_ref = _first_input_source_ref(node, link_map)
                    if source_ref is None:
                        continue
                    resolved = _resolve_virtual_source(source_ref, set_sources, link_map, nodes_by_id)
                    for link_id in _output_link_ids(node):
                        if link_map.get(link_id) != resolved:
                            link_map[link_id] = resolved
                            changed = True
                elif node_type == "reroute":
                    source_ref = _first_input_source_ref(node, link_map)
                    if source_ref is None:
                        continue
                    resolved = _resolve_virtual_source(source_ref, set_sources, link_map, nodes_by_id)
                    for link_id in _output_link_ids(node):
                        if link_map.get(link_id) != resolved:
                            link_map[link_id] = resolved
                            changed = True
        return link_map

    @staticmethod
    def _link_map(links: list[Any]) -> dict[Any, tuple[str, int]]:
        link_map: dict[Any, tuple[str, int]] = {}
        for link in links:
            if not isinstance(link, list) or len(link) < 4:
                continue
            link_id, source_node_id, source_slot = link[0], link[1], link[2]
            try:
                source_slot_int = int(source_slot)
            except (TypeError, ValueError):
                source_slot_int = 0
            link_map[link_id] = (str(source_node_id), source_slot_int)
        return link_map

    def _widget_value_map(self, node: dict[str, Any], *, object_info_item: Any = None) -> dict[str, Any]:
        widgets = node.get("widgets_values")
        if isinstance(widgets, dict):
            return {str(key): value for key, value in widgets.items() if key != "videopreview"}
        if not isinstance(widgets, list):
            return {}
        names = self._widget_names(node)
        if object_info_item is not None:
            return _type_aware_widget_value_map(names=names, widgets=widgets, object_info_item=object_info_item)
        values: dict[str, Any] = {}
        for index, name in enumerate(names):
            if index < len(widgets):
                values[name] = widgets[index]
        return values

    def _patch_api_prompt(
        self,
        *,
        graph: dict[str, Any],
        parameter_plan: dict[str, Any],
        input_assets: dict[str, Any],
        node_overrides: dict[str, Mapping[str, Any]],
        output_prefix: str,
        changes: list[dict[str, Any]],
    ) -> None:
        for node_id, node in graph.items():
            if not isinstance(node, dict):
                continue
            class_type = str(node.get("class_type") or "")
            inputs = node.get("inputs")
            if not isinstance(inputs, dict):
                continue
            self._patch_input_mapping(
                node_id=str(node_id),
                node_type=class_type,
                inputs=inputs,
                parameter_plan=parameter_plan,
                input_assets=input_assets,
                node_overrides=dict(node_overrides.get(str(node_id), {})),
                output_prefix=output_prefix,
                changes=changes,
            )

    def _patch_ui_workflow(
        self,
        *,
        graph: dict[str, Any],
        parameter_plan: dict[str, Any],
        input_assets: dict[str, Any],
        node_overrides: dict[str, Mapping[str, Any]],
        output_prefix: str,
        changes: list[dict[str, Any]],
    ) -> None:
        for node in graph.get("nodes", []):
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id") or "")
            node_type = str(node.get("type") or "")
            widgets = node.get("widgets_values")
            if isinstance(widgets, dict):
                self._patch_input_mapping(
                    node_id=node_id,
                    node_type=node_type,
                    inputs=widgets,
                    parameter_plan=parameter_plan,
                    input_assets=input_assets,
                    node_overrides=dict(node_overrides.get(node_id, {})),
                    output_prefix=output_prefix,
                    changes=changes,
                    location="widgets_values",
                )
            elif isinstance(widgets, list):
                widget_names = self._widget_names(node)
                self._patch_widget_list(
                    node_id=node_id,
                    node_type=node_type,
                    widgets=widgets,
                    widget_names=widget_names,
                    parameter_plan=parameter_plan,
                    input_assets=input_assets,
                    node_overrides=dict(node_overrides.get(node_id, {})),
                    output_prefix=output_prefix,
                    changes=changes,
                )

    def _patch_input_mapping(
        self,
        *,
        node_id: str,
        node_type: str,
        inputs: dict[str, Any],
        parameter_plan: dict[str, Any],
        input_assets: dict[str, Any],
        node_overrides: dict[str, Any],
        output_prefix: str,
        changes: list[dict[str, Any]],
        location: str = "inputs",
    ) -> None:
        patch_values = self._default_patch_values(
            node_type=node_type,
            parameter_plan=parameter_plan,
            input_assets=input_assets,
            output_prefix=output_prefix,
        )
        patch_values.update(node_overrides)
        for key, new_value in patch_values.items():
            if key not in inputs:
                continue
            old_value = inputs.get(key)
            if old_value == new_value:
                continue
            inputs[key] = new_value
            changes.append(_change(node_id, node_type, key, old_value, new_value, location))
            if key in {"video", "image"} and isinstance(inputs.get("videopreview"), dict):
                self._patch_preview_filename(
                    node_id=node_id,
                    node_type=node_type,
                    preview=inputs["videopreview"],
                    filename=str(new_value),
                    changes=changes,
                    location=location,
                )

    def _patch_widget_list(
        self,
        *,
        node_id: str,
        node_type: str,
        widgets: list[Any],
        widget_names: list[str],
        parameter_plan: dict[str, Any],
        input_assets: dict[str, Any],
        node_overrides: dict[str, Any],
        output_prefix: str,
        changes: list[dict[str, Any]],
    ) -> None:
        patch_values = self._default_patch_values(
            node_type=node_type,
            parameter_plan=parameter_plan,
            input_assets=input_assets,
            output_prefix=output_prefix,
        )
        patch_values.update(node_overrides)
        for index, name in enumerate(widget_names):
            if index >= len(widgets) or name not in patch_values:
                continue
            old_value = widgets[index]
            new_value = patch_values[name]
            if old_value == new_value:
                continue
            widgets[index] = new_value
            changes.append(_change(node_id, node_type, name, old_value, new_value, f"widgets_values[{index}]"))

    def _default_patch_values(
        self,
        *,
        node_type: str,
        parameter_plan: dict[str, Any],
        input_assets: dict[str, Any],
        output_prefix: str,
    ) -> dict[str, Any]:
        positive = _positive_prompt(parameter_plan)
        negative = str(parameter_plan.get("negative_prompt") or "").strip()
        width = _int_or_none(parameter_plan.get("width"))
        height = _int_or_none(parameter_plan.get("height"))
        frames = _int_or_none(parameter_plan.get("frames"))
        fps = _float_or_none(parameter_plan.get("fps"))
        scene_image = _first_text(
            input_assets.get("approved_keyframe_name"),
            input_assets.get("scene_image_name"),
            input_assets.get("image_name"),
        )
        video_name = _first_text(input_assets.get("reference_video_name"), input_assets.get("source_video_name"))
        audio_name = _first_text(input_assets.get("voice_audio_name"), input_assets.get("audio_name"))

        values: dict[str, Any] = {}
        lower_type = node_type.lower()
        if positive:
            values.update(
                {
                    "positive_prompt": positive,
                    "prompt": positive,
                }
            )
            if _text_node_wants_positive(lower_type):
                values["text"] = positive
        if negative:
            values["negative_prompt"] = negative
        if scene_image and "loadimage" in lower_type:
            values["image"] = scene_image
        if video_name and ("loadvideo" in lower_type or "vhs_loadvideo" in lower_type):
            values["video"] = video_name
        if audio_name and ("audio" in lower_type or "wav" in lower_type):
            values.update({"audio": audio_name, "audio_file": audio_name, "wav": audio_name, "file": audio_name})
        if width is not None:
            values.update({"width": width, "custom_width": width})
        if height is not None:
            values.update({"height": height, "custom_height": height})
        if frames is not None:
            values.update({"frames": frames, "num_frames": frames, "frame_count": frames})
        if fps is not None:
            values.update({"fps": fps, "frame_rate": fps, "force_rate": fps})
        if "save" in lower_type or "combine" in lower_type or "video" in lower_type:
            values["filename_prefix"] = output_prefix
        return values

    @staticmethod
    def _widget_names(node: dict[str, Any]) -> list[str]:
        names: list[str] = []
        for item in node.get("inputs", []) or []:
            if not isinstance(item, dict):
                continue
            widget = item.get("widget")
            if isinstance(widget, dict) and widget.get("name"):
                names.append(str(widget["name"]))
        return names

    @staticmethod
    def _patch_preview_filename(
        *,
        node_id: str,
        node_type: str,
        preview: dict[str, Any],
        filename: str,
        changes: list[dict[str, Any]],
        location: str,
    ) -> None:
        params = preview.get("params")
        if not isinstance(params, dict) or "filename" not in params:
            return
        old_value = params["filename"]
        if old_value == filename:
            return
        params["filename"] = filename
        changes.append(_change(node_id, node_type, "videopreview.params.filename", old_value, filename, location))

    @staticmethod
    def _graph_format(graph: Any) -> str:
        if isinstance(graph, dict) and isinstance(graph.get("nodes"), list):
            return "ui_workflow"
        if isinstance(graph, dict) and all(
            isinstance(value, dict) and "class_type" in value
            for value in graph.values()
        ):
            return "api_prompt"
        return "unknown"


def _positive_prompt(parameter_plan: Mapping[str, Any]) -> str:
    explicit = str(parameter_plan.get("positive_prompt") or "").strip()
    if explicit:
        return explicit
    parts = [
        parameter_plan.get("character_prompt"),
        parameter_plan.get("scene_prompt"),
        parameter_plan.get("motion_prompt"),
    ]
    return " ".join(str(part).strip() for part in parts if str(part or "").strip())


def _text_node_wants_positive(lower_type: str) -> bool:
    if any(token in lower_type for token in ("negative", "反向", "负向")):
        return False
    return any(token in lower_type for token in ("text", "prompt", "clip", "qwen"))


def _safe_slug(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    clean = clean.strip("._")
    return clean[:120] or "workflow"


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not allocate a unique materialized workflow path under {path.parent}")


def _change(
    node_id: str,
    node_type: str,
    input_name: str,
    old_value: Any,
    new_value: Any,
    location: str,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "input_name": input_name,
        "location": location,
        "old_preview": _preview(old_value),
        "new_preview": _preview(new_value),
    }


def _preview(value: Any) -> Any:
    if isinstance(value, str):
        return value[:240]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:240]


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        clean = str(value).strip()
        if clean:
            return clean
    return None


def _int_or_none(value: Any) -> int | None:
    try:
        if value is None:
            return None
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _object_info_required_inputs(object_info_item: Any) -> list[str]:
    if not isinstance(object_info_item, Mapping):
        return []
    input_info = object_info_item.get("input")
    if not isinstance(input_info, Mapping):
        return []
    required = input_info.get("required")
    if not isinstance(required, Mapping):
        return []
    return [str(key) for key in required.keys()]


def _object_info_input_config(object_info_item: Any, input_name: str) -> Any:
    if not isinstance(object_info_item, Mapping):
        return None
    input_info = object_info_item.get("input")
    if not isinstance(input_info, Mapping):
        return None
    for section_name in ("required", "optional"):
        section = input_info.get(section_name)
        if isinstance(section, Mapping) and input_name in section:
            return section[input_name]
    return None


def _type_aware_widget_value_map(
    *,
    names: list[str],
    widgets: list[Any],
    object_info_item: Any,
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    widget_index = 0
    for name in names:
        input_config = _object_info_input_config(object_info_item, name)
        if input_config is None:
            if widget_index < len(widgets):
                values[name] = widgets[widget_index]
                widget_index += 1
            continue
        while widget_index < len(widgets) and not _value_matches_input_config(widgets[widget_index], input_config):
            widget_index += 1
        if widget_index < len(widgets):
            values[name] = widgets[widget_index]
            widget_index += 1
    return values


def _value_matches_input_config(value: Any, input_config: Any) -> bool:
    if value is None:
        return True
    if _is_prompt_link(value):
        return True
    if not isinstance(input_config, list) or not input_config:
        return True
    expected = input_config[0]
    if isinstance(expected, list):
        if not expected:
            return isinstance(value, str)
        if value in expected:
            return True
        return isinstance(value, str) and _combo_config_allows_file_path(input_config)
    if not isinstance(expected, str):
        return True
    normalized = expected.upper()
    if normalized == "INT":
        return isinstance(value, int) and not isinstance(value, bool)
    if normalized == "FLOAT":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if normalized == "BOOLEAN":
        return isinstance(value, bool)
    if normalized in {"STRING", "IMAGEUPLOAD", "AUDIOUPLOAD"}:
        return isinstance(value, str)
    return True


def _combo_config_allows_file_path(input_config: Any) -> bool:
    if not isinstance(input_config, list):
        return False
    for item in input_config[1:]:
        if not isinstance(item, Mapping):
            continue
        if any(str(key).endswith("_upload") and bool(value) for key, value in item.items()):
            return True
    return False


def _input_config_preview(input_config: Any) -> Any:
    if isinstance(input_config, list) and input_config:
        first = input_config[0]
        if isinstance(first, list):
            return first[:20]
        return first
    return _preview(input_config)


def _is_prompt_link(value: Any) -> bool:
    """Return true for ComfyUI API prompt links such as ["12", 0]."""

    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and bool(value[0].strip())
        and isinstance(value[1], int)
    )


def _is_ui_only_node_type(node_type: str) -> bool:
    return node_type.strip().lower() in {
        "note",
        "markdownnote",
        "getnode",
        "setnode",
        "reroute",
        "fast groups bypasser (rgthree)",
        "fast groups muter (rgthree)",
        "label (rgthree)",
    }


def _is_disabled_ui_node(node: Mapping[str, Any]) -> bool:
    return node.get("mode") == 4


def _virtual_reroute_name(node: Mapping[str, Any]) -> str | None:
    widgets = node.get("widgets_values")
    if isinstance(widgets, list) and widgets:
        value = str(widgets[0]).strip()
        return value or None
    if isinstance(widgets, Mapping):
        for key in ("name", "key", "value"):
            value = str(widgets.get(key) or "").strip()
            if value:
                return value
    return None


def _first_input_source_ref(
    node: Mapping[str, Any],
    link_map: Mapping[Any, tuple[str, int]],
) -> tuple[str, int] | None:
    for raw_input in node.get("inputs", []) or []:
        if not isinstance(raw_input, Mapping):
            continue
        link_id = raw_input.get("link")
        if link_id is not None and link_id in link_map:
            return link_map[link_id]
    return None


def _output_link_ids(node: Mapping[str, Any]) -> list[Any]:
    link_ids: list[Any] = []
    for output in node.get("outputs", []) or []:
        if not isinstance(output, Mapping):
            continue
        links = output.get("links")
        if isinstance(links, list):
            link_ids.extend(link_id for link_id in links if link_id is not None)
    return link_ids


def _resolve_virtual_source(
    source_ref: tuple[str, int],
    set_sources: Mapping[str, tuple[str, int]],
    link_map: Mapping[Any, tuple[str, int]],
    nodes_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[str, int]:
    current = source_ref
    seen: set[tuple[str, int]] = set()
    for _ in range(100):
        if current in seen:
            return current
        seen.add(current)
        node = nodes_by_id.get(str(current[0]))
        if node is None:
            return current
        node_type = str(node.get("type") or "").strip().lower()
        if node_type == "getnode":
            variable_name = _virtual_reroute_name(node)
            next_ref = set_sources.get(variable_name)
        elif node_type == "setnode":
            next_ref = _first_input_source_ref(node, link_map)
        elif node_type == "reroute":
            next_ref = _first_input_source_ref(node, link_map)
        else:
            return current
        if next_ref is None:
            return current
        current = next_ref
    return current
