"""Workflow Template Registry services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.models.enums import (
    AgentMemorySnapshotType,
    OutputArtifactSourceType,
    OutputArtifactType,
    WorkflowRunStatus,
    WorkflowTemplateRunStatus,
    WorkflowTemplateStatus,
    WorkflowTemplateVersionValidationStatus,
)
from app.models.workflow import WorkflowGraph, WorkflowGraphEdge, WorkflowGraphNode, WorkflowTemplate, WorkflowTemplateRun, WorkflowTemplateVersion
from app.services.output_artifact_service import OutputArtifactService
from app.workflow.planner import WorkflowExecutionPlanner
from app.workflow.services import WorkflowGraphService, WorkflowStateService
from app.workflow.template_definitions import BUILTIN_WORKFLOW_TEMPLATES


SUPPORTED_NODE_TYPES = {
    "playbook_step",
    "approval_gate",
    "tool_call",
    "artifact_transform",
    "conditional_router",
    "delay",
    "retry",
    "workflow_checkpoint",
    "memory_snapshot",
    "no_op",
}


@dataclass(slots=True)
class TemplateRunResult:
    template: WorkflowTemplate
    version: WorkflowTemplateVersion
    run: WorkflowTemplateRun
    workflow_run_id: UUID | None
    success: bool
    summary: str


class WorkflowTemplateCompatibilityService:
    """Checks whether a template version can run on the current foundation runtime."""

    def check(
        self,
        *,
        graph_definition: dict[str, Any],
        entry_node: str,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        risk_level: str = "low",
    ) -> dict[str, Any]:
        nodes = self._nodes_from_definition(graph_definition)
        edges = self._edges_from_definition(graph_definition)
        errors: list[str] = []
        warnings: list[str] = []
        missing_capabilities: list[str] = []

        for node in nodes:
            node_type = str(node.node_type)
            if node_type not in SUPPORTED_NODE_TYPES:
                errors.append(f"unsupported node_type: {node_type}")
                missing_capabilities.append(f"node_type:{node_type}")
        if risk_level not in {"low", "medium", "high"}:
            errors.append(f"unsupported risk_level: {risk_level}")
        if input_schema is not None and not isinstance(input_schema, dict):
            errors.append("input_schema must be an object")
        if output_schema is not None and not isinstance(output_schema, dict):
            errors.append("output_schema must be an object")

        planner_result = WorkflowExecutionPlanner().validate_graph(nodes=nodes, edges=edges, entry_node=entry_node)
        errors.extend(planner_result.errors)
        if risk_level in {"medium", "high"}:
            warnings.append("Template requires approval-aware execution; review_first is recommended.")
        if any(node.node_type == "tool_call" and (node.configuration or {}).get("tool") == "openclaw_tool" for node in nodes):
            warnings.append("OpenClaw execution is mock/placeholder only.")

        return {
            "compatible": not errors,
            "warnings": sorted(set(warnings)),
            "errors": sorted(set(errors)),
            "missing_capabilities": sorted(set(missing_capabilities)),
            "validation_status": WorkflowTemplateVersionValidationStatus.VALID.value
            if not errors
            else WorkflowTemplateVersionValidationStatus.INVALID.value,
        }

    def _nodes_from_definition(self, graph_definition: dict[str, Any]) -> list[WorkflowGraphNode]:
        return [
            WorkflowGraphNode(
                workspace_id="template-validation",
                workflow_graph_id=UUID("00000000-0000-0000-0000-000000000000"),
                node_key=str(item["node_key"]),
                node_type=str(item.get("node_type") or "no_op"),
                execution_mode=str(item.get("execution_mode") or "sync"),
                configuration=item.get("configuration") if isinstance(item.get("configuration"), dict) else {},
                retry_policy=item.get("retry_policy") if isinstance(item.get("retry_policy"), dict) else {},
                timeout_seconds=item.get("timeout_seconds"),
                node_metadata=item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            )
            for item in graph_definition.get("nodes", [])
            if isinstance(item, dict) and item.get("node_key")
        ]

    def _edges_from_definition(self, graph_definition: dict[str, Any]) -> list[WorkflowGraphEdge]:
        return [
            WorkflowGraphEdge(
                workspace_id="template-validation",
                workflow_graph_id=UUID("00000000-0000-0000-0000-000000000000"),
                source_node_key=str(item["source_node_key"]),
                target_node_key=str(item["target_node_key"]),
                edge_type=str(item.get("edge_type") or "success"),
                condition_expression=item.get("condition_expression"),
                priority=int(item.get("priority", 100)),
                edge_metadata=item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
            )
            for item in graph_definition.get("edges", [])
            if isinstance(item, dict) and item.get("source_node_key") and item.get("target_node_key")
        ]


class WorkflowTemplateRegistryService:
    """Workspace-scoped template registry, versioning, import/export, and run service."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.compatibility = WorkflowTemplateCompatibilityService()

    async def list_templates(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
        seed_builtins: bool = True,
    ) -> list[WorkflowTemplate]:
        if seed_builtins:
            await self.ensure_builtin_templates(workspace_id=workspace_id)
            await self.session.commit()
        statement = (
            select(WorkflowTemplate)
            .options(selectinload(WorkflowTemplate.versions))
            .where(WorkflowTemplate.workspace_id == workspace_id)
        )
        if status is not None:
            statement = statement.where(WorkflowTemplate.status == status)
        if category is not None:
            statement = statement.where(WorkflowTemplate.category == category)
        result = await self.session.execute(statement.order_by(WorkflowTemplate.category.asc(), WorkflowTemplate.name.asc()).limit(limit))
        return list(result.scalars().all())

    async def get_template(self, *, workspace_id: str, template_id: UUID) -> WorkflowTemplate | None:
        result = await self.session.execute(
            select(WorkflowTemplate)
            .options(selectinload(WorkflowTemplate.versions))
            .where(WorkflowTemplate.workspace_id == workspace_id, WorkflowTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_template_by_key(self, *, workspace_id: str, template_key: str) -> WorkflowTemplate | None:
        result = await self.session.execute(
            select(WorkflowTemplate)
            .options(selectinload(WorkflowTemplate.versions))
            .where(WorkflowTemplate.workspace_id == workspace_id, WorkflowTemplate.template_key == template_key)
        )
        return result.scalar_one_or_none()

    async def require_template(self, *, workspace_id: str, template_id: UUID) -> WorkflowTemplate:
        template = await self.get_template(workspace_id=workspace_id, template_id=template_id)
        if template is None:
            raise ValueError("Workflow template not found in workspace")
        return template

    async def require_template_version(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID,
    ) -> WorkflowTemplateVersion:
        result = await self.session.execute(
            select(WorkflowTemplateVersion).where(
                WorkflowTemplateVersion.workspace_id == workspace_id,
                WorkflowTemplateVersion.template_id == template_id,
                WorkflowTemplateVersion.id == version_id,
            )
        )
        version = result.scalar_one_or_none()
        if version is None:
            raise ValueError("Workflow template version not found in workspace")
        return version

    async def create_template(
        self,
        *,
        workspace_id: str,
        template_key: str,
        name: str,
        description: str | None,
        category: str | None,
        status: str,
        risk_level: str,
        tags: list[str] | None,
        metadata: dict[str, Any] | None,
        version: str,
        graph_definition: dict[str, Any],
        entry_node: str,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        changelog: str | None = None,
        created_by: str | None = None,
        commit: bool = True,
    ) -> WorkflowTemplate:
        existing = await self.get_template_by_key(workspace_id=workspace_id, template_key=template_key)
        if existing is not None:
            raise ValueError("Workflow template key already exists in workspace")
        template = WorkflowTemplate(
            workspace_id=workspace_id,
            template_key=template_key,
            name=name,
            description=description,
            category=category,
            status=status,
            risk_level=risk_level,
            tags=tags or [],
            template_metadata=metadata or {},
            current_version=version if status == WorkflowTemplateStatus.ACTIVE.value else None,
            latest_version=version,
        )
        self.session.add(template)
        await self.session.flush()
        await self.create_version(
            workspace_id=workspace_id,
            template_id=template.id,
            version=version,
            graph_definition=graph_definition,
            entry_node=entry_node,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            changelog=changelog,
            created_by=created_by,
            commit=False,
        )
        if commit:
            await self.session.commit()
            template = await self.require_template(workspace_id=workspace_id, template_id=template.id)
        return template

    async def create_version(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version: str,
        graph_definition: dict[str, Any],
        entry_node: str,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        changelog: str | None = None,
        created_by: str | None = None,
        commit: bool = True,
    ) -> WorkflowTemplateVersion:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        duplicate = await self.session.execute(
            select(WorkflowTemplateVersion).where(
                WorkflowTemplateVersion.workspace_id == workspace_id,
                WorkflowTemplateVersion.template_id == template.id,
                WorkflowTemplateVersion.version == version,
            )
        )
        if duplicate.scalar_one_or_none() is not None:
            raise ValueError("Workflow template version already exists and cannot be overwritten")
        compatibility = self.compatibility.check(
            graph_definition=graph_definition,
            entry_node=entry_node,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            risk_level=template.risk_level,
        )
        template_version = WorkflowTemplateVersion(
            workspace_id=workspace_id,
            template_id=template.id,
            version=version,
            graph_definition=graph_definition,
            entry_node=entry_node,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            compatibility=compatibility,
            validation_status=compatibility["validation_status"],
            validation_errors=compatibility["errors"],
            changelog=changelog,
            created_by=created_by,
        )
        self.session.add(template_version)
        template.latest_version = version
        if template.status == WorkflowTemplateStatus.ACTIVE.value and template.current_version is None and compatibility["compatible"]:
            template.current_version = version
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(template_version)
        return template_version

    async def activate_version(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID,
        commit: bool = True,
    ) -> WorkflowTemplate:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        version = await self.require_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_id)
        validation = await self.validate_template(workspace_id=workspace_id, template_id=template.id, version_id=version.id, commit=False)
        if not validation.compatibility.get("compatible", False):
            raise ValueError("Cannot activate invalid workflow template version")
        template.status = WorkflowTemplateStatus.ACTIVE.value
        template.current_version = version.version
        if commit:
            await self.session.commit()
            template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        return template

    async def disable_template(self, *, workspace_id: str, template_id: UUID) -> WorkflowTemplate:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        template.status = WorkflowTemplateStatus.DISABLED.value
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def archive_template(self, *, workspace_id: str, template_id: UUID) -> WorkflowTemplate:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        template.status = WorkflowTemplateStatus.ARCHIVED.value
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def validate_template(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID | None = None,
        commit: bool = True,
    ) -> WorkflowTemplateVersion:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        version = await self._version_for_run(workspace_id=workspace_id, template=template, version_id=version_id)
        compatibility = self.compatibility.check(
            graph_definition=version.graph_definition or {},
            entry_node=version.entry_node,
            input_schema=version.input_schema or {},
            output_schema=version.output_schema or {},
            risk_level=template.risk_level,
        )
        version.compatibility = compatibility
        version.validation_status = compatibility["validation_status"]
        version.validation_errors = compatibility["errors"]
        flag_modified(version, "compatibility")
        flag_modified(version, "validation_errors")
        if commit:
            await self.session.commit()
            await self.session.refresh(version)
        return version

    async def export_template(
        self,
        *,
        workspace_id: str,
        template_id: UUID,
        version_id: UUID | None = None,
    ) -> dict[str, Any]:
        template = await self.require_template(workspace_id=workspace_id, template_id=template_id)
        version = await self._version_for_run(workspace_id=workspace_id, template=template, version_id=version_id)
        return {
            "template_key": template.template_key,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "version": version.version,
            "graph_definition": version.graph_definition or {},
            "entry_node": version.entry_node,
            "input_schema": version.input_schema or {},
            "output_schema": version.output_schema or {},
            "metadata": {**(template.template_metadata or {}), "tags": template.tags or [], "risk_level": template.risk_level},
            "compatibility": version.compatibility or {},
        }

    async def import_template(
        self,
        *,
        workspace_id: str,
        payload: dict[str, Any],
        dry_run: bool = True,
        conflict_strategy: str = "new_version",
        created_by: str | None = None,
    ) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        template_key = str(payload.get("template_key") or "").strip()
        version = str(payload.get("version") or "1").strip()
        if not template_key:
            errors.append("template_key is required")
        graph_definition = payload.get("graph_definition") if isinstance(payload.get("graph_definition"), dict) else {}
        entry_node = str(payload.get("entry_node") or "")
        compatibility = self.compatibility.check(
            graph_definition=graph_definition,
            entry_node=entry_node,
            input_schema=payload.get("input_schema") if isinstance(payload.get("input_schema"), dict) else {},
            output_schema=payload.get("output_schema") if isinstance(payload.get("output_schema"), dict) else {},
            risk_level=str((payload.get("metadata") or {}).get("risk_level") or "low") if isinstance(payload.get("metadata"), dict) else "low",
        )
        errors.extend(compatibility["errors"])
        warnings.extend(compatibility["warnings"])
        existing = await self.get_template_by_key(workspace_id=workspace_id, template_key=template_key) if template_key else None
        action = "create_template"
        if existing is not None:
            if conflict_strategy == "error":
                errors.append("template_key already exists")
            elif conflict_strategy == "new_template":
                action = "create_template_with_new_key"
                template_key = f"{template_key}-import"
            else:
                action = "create_version"
        if dry_run or errors:
            return {"dry_run": dry_run, "valid": not errors, "action": action, "errors": errors, "warnings": warnings}
        if existing is not None and action == "create_version":
            version_model = await self.create_version(
                workspace_id=workspace_id,
                template_id=existing.id,
                version=version,
                graph_definition=graph_definition,
                entry_node=entry_node,
                input_schema=payload.get("input_schema") if isinstance(payload.get("input_schema"), dict) else {},
                output_schema=payload.get("output_schema") if isinstance(payload.get("output_schema"), dict) else {},
                changelog="Imported template version",
                created_by=created_by,
            )
            template = await self.require_template(workspace_id=workspace_id, template_id=existing.id)
            return {"dry_run": False, "valid": True, "action": action, "errors": [], "warnings": warnings, "template": template, "version": version_model}
        template = await self.create_template(
            workspace_id=workspace_id,
            template_key=template_key,
            name=str(payload.get("name") or template_key),
            description=payload.get("description"),
            category=payload.get("category"),
            status=WorkflowTemplateStatus.DRAFT.value,
            risk_level=str((payload.get("metadata") or {}).get("risk_level") or "low") if isinstance(payload.get("metadata"), dict) else "low",
            tags=(payload.get("metadata") or {}).get("tags", []) if isinstance(payload.get("metadata"), dict) else [],
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
            version=version,
            graph_definition=graph_definition,
            entry_node=entry_node,
            input_schema=payload.get("input_schema") if isinstance(payload.get("input_schema"), dict) else {},
            output_schema=payload.get("output_schema") if isinstance(payload.get("output_schema"), dict) else {},
            changelog="Imported template",
            created_by=created_by,
        )
        imported_version_result = await self.session.execute(
            select(WorkflowTemplateVersion).where(
                WorkflowTemplateVersion.workspace_id == workspace_id,
                WorkflowTemplateVersion.template_id == template.id,
                WorkflowTemplateVersion.version == version,
            )
        )
        imported_version = imported_version_result.scalar_one()
        return {"dry_run": False, "valid": True, "action": action, "errors": [], "warnings": warnings, "template": template, "version": imported_version}

    async def run_template(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        template_id: UUID | None = None,
        template_key: str | None = None,
        version_id: UUID | None = None,
        input_payload: dict[str, Any] | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        mode: str = "auto_safe",
        execution_mode: str = "immediate",
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> TemplateRunResult:
        template = await self._template_for_run(workspace_id=workspace_id, template_id=template_id, template_key=template_key)
        if template.status != WorkflowTemplateStatus.ACTIVE.value:
            raise ValueError("Only active workflow templates can run by default")
        version = await self._version_for_run(workspace_id=workspace_id, template=template, version_id=version_id)
        await self.validate_template(workspace_id=workspace_id, template_id=template.id, version_id=version.id, commit=False)
        if version.validation_status != WorkflowTemplateVersionValidationStatus.VALID.value:
            raise ValueError("Workflow template version is not valid")

        run = WorkflowTemplateRun(
            workspace_id=workspace_id,
            template_id=template.id,
            template_version_id=version.id,
            source_type=source_type,
            source_id=source_id,
            status=WorkflowTemplateRunStatus.RUNNING.value,
            input_payload=input_payload or {},
            output_payload={"template_key": template.template_key, "version": version.version, "execution_mode": execution_mode, "steps": []},
            run_metadata=metadata or {},
            started_at=datetime.now(UTC),
        )
        self.session.add(run)
        await self.session.flush()

        graph = await WorkflowGraphService(self.session).create_graph(
            workspace_id=workspace_id,
            name=f"template:{template.template_key}:{version.version}",
            description=template.description,
            version=version.version,
            graph_definition=version.graph_definition or {},
            entry_node=version.entry_node,
            metadata={"workflow_template_id": str(template.id), "workflow_template_version_id": str(version.id), "workflow_template_run_id": str(run.id)},
            commit=False,
        )
        workflow = await WorkflowStateService(self.session).create_workflow_run(
            workspace_id=workspace_id,
            source_type="workflow_template",
            source_id=str(run.id),
            workflow_graph_id=graph.id,
            graph_execution=True,
            current_node_key=version.entry_node,
            status=WorkflowRunStatus.RUNNING.value,
            variables=input_payload or {},
            context={
                "template_key": template.template_key,
                "template_version": version.version,
                "mode": mode,
                "execution_mode": execution_mode,
            },
            metadata={"workflow_template_id": str(template.id), "workflow_template_version_id": str(version.id), "workflow_template_run_id": str(run.id)},
            commit=False,
        )
        run.workflow_run_id = workflow.id

        if self._requires_approval(template=template, graph=graph, mode=mode):
            await WorkflowStateService(self.session).pause_workflow(
                workspace_id=workspace_id,
                workflow_run_id=workflow.id,
                reason="Workflow template run waiting for approval gate",
                waiting_approval=True,
                commit=False,
            )
            checkpoint = await WorkflowStateService(self.session).create_checkpoint(
                workspace_id=workspace_id,
                workflow_run_id=workflow.id,
                checkpoint_name="template-approval-gate",
                checkpoint_type="approval",
                state_payload={"template_key": template.template_key, "workflow_template_run_id": str(run.id)},
                created_by=user_id or "WorkflowTemplateRegistryService",
                commit=False,
            )
            run.output_payload = {
                **(run.output_payload or {}),
                "approval_required": True,
                "workflow_run_id": str(workflow.id),
                "checkpoint_id": str(checkpoint.id),
                "summary": f"Workflow template `{template.template_key}` is waiting for approval.",
            }
            flag_modified(run, "output_payload")
            summary = run.output_payload["summary"]
            success = True
        else:
            summary = await self._execute_metadata_graph(
                workspace_id=workspace_id,
                user_id=user_id,
                template=template,
                version=version,
                run=run,
                workflow_run_id=workflow.id,
                graph=graph,
            )
            run.status = WorkflowTemplateRunStatus.COMPLETED.value
            run.completed_at = datetime.now(UTC)
            success = True

        if commit:
            await self.session.commit()
            await self.session.refresh(run)
        return TemplateRunResult(template=template, version=version, run=run, workflow_run_id=workflow.id, success=success, summary=summary)

    async def list_template_runs(
        self,
        *,
        workspace_id: str,
        template_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowTemplateRun]:
        statement = select(WorkflowTemplateRun).where(WorkflowTemplateRun.workspace_id == workspace_id)
        if template_id is not None:
            statement = statement.where(WorkflowTemplateRun.template_id == template_id)
        if status is not None:
            statement = statement.where(WorkflowTemplateRun.status == status)
        result = await self.session.execute(statement.order_by(WorkflowTemplateRun.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_template_run(self, *, workspace_id: str, run_id: UUID) -> WorkflowTemplateRun | None:
        result = await self.session.execute(
            select(WorkflowTemplateRun).where(WorkflowTemplateRun.workspace_id == workspace_id, WorkflowTemplateRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def ensure_builtin_templates(self, *, workspace_id: str) -> None:
        for definition in BUILTIN_WORKFLOW_TEMPLATES:
            existing = await self.get_template_by_key(workspace_id=workspace_id, template_key=definition["template_key"])
            if existing is not None:
                continue
            await self.create_template(
                workspace_id=workspace_id,
                template_key=definition["template_key"],
                name=definition["name"],
                description=definition.get("description"),
                category=definition.get("category"),
                status=WorkflowTemplateStatus.ACTIVE.value,
                risk_level=definition.get("risk_level", "low"),
                tags=definition.get("tags") or [],
                metadata={"built_in": True},
                version=definition.get("version", "1"),
                graph_definition=definition.get("graph_definition") or {},
                entry_node=definition.get("entry_node") or "start",
                input_schema=definition.get("input_schema") or {},
                output_schema=definition.get("output_schema") or {},
                changelog="Built-in Phase 47 workflow template",
                created_by="system",
                commit=False,
            )

    async def _execute_metadata_graph(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        template: WorkflowTemplate,
        version: WorkflowTemplateVersion,
        run: WorkflowTemplateRun,
        workflow_run_id: UUID,
        graph: WorkflowGraph,
    ) -> str:
        workflow_service = WorkflowStateService(self.session)
        completed_steps: list[dict[str, Any]] = []
        last_artifact_id: str | None = None
        for index, node in enumerate(sorted(graph.nodes, key=lambda item: item.node_key)):
            step = await workflow_service.start_step(
                workspace_id=workspace_id,
                workflow_run_id=workflow_run_id,
                step_index=index,
                step_name=node.node_key,
                step_type=node.node_type,
                node_key=node.node_key,
                input_payload={"configuration": node.configuration or {}, "template_key": template.template_key},
                metadata={"workflow_template_run_id": str(run.id), "template_version": version.version},
                commit=False,
            )
            output = {"node_key": node.node_key, "node_type": node.node_type, "status": "completed"}
            if node.node_type == "artifact_transform":
                artifact = await OutputArtifactService(self.session).create_artifact(
                    workspace_id=workspace_id,
                    source_type=OutputArtifactSourceType.PLAYBOOK.value,
                    artifact_type=str((node.configuration or {}).get("artifact_type") or OutputArtifactType.REPORT.value),
                    title=f"{template.name} - {node.node_key}",
                    summary=f"Metadata artifact generated by workflow template {template.template_key}.",
                    content=f"# {template.name}\n\nTemplate run: {run.id}\nNode: {node.node_key}\n",
                    metadata={"template_key": template.template_key, "version": version.version, "node_key": node.node_key},
                    workflow_run_id=workflow_run_id,
                    workflow_step_id=step.id,
                    workflow_template_id=template.id,
                    workflow_template_version_id=version.id,
                    workflow_template_run_id=run.id,
                    producing_node_key=node.node_key,
                    graph_lineage={"template_key": template.template_key, "node_key": node.node_key},
                    generated_by="WorkflowTemplateRegistryService",
                    created_by=user_id or "workflow_template",
                    commit=False,
                )
                last_artifact_id = str(artifact.id)
                output["artifact_id"] = last_artifact_id
            await workflow_service.complete_step(
                workspace_id=workspace_id,
                workflow_step_id=step.id,
                output_payload=output,
                commit=False,
            )
            completed_steps.append(output)
        checkpoint = await workflow_service.create_checkpoint(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            checkpoint_name="template-final",
            checkpoint_type="auto",
            state_payload={"template_key": template.template_key, "workflow_template_run_id": str(run.id), "artifact_id": last_artifact_id},
            created_by=user_id or "WorkflowTemplateRegistryService",
            commit=False,
        )
        memory = await workflow_service.create_memory_snapshot(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            memory_type=AgentMemorySnapshotType.TASK_CONTEXT.value,
            summary=f"Workflow template {template.template_key} completed.",
            memory_payload={"template_key": template.template_key, "version": version.version, "steps": completed_steps},
            metadata={
                "checkpoint_id": str(checkpoint.id),
                "workflow_template_id": str(template.id),
                "workflow_template_version_id": str(version.id),
                "workflow_template_run_id": str(run.id),
            },
            commit=False,
        )
        await workflow_service.complete_workflow(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            output={"workflow_template_run_id": str(run.id), "artifact_id": last_artifact_id, "memory_snapshot_id": str(memory.id)},
            commit=False,
        )
        summary = f"Workflow template `{template.template_key}` completed with {len(completed_steps)} metadata step(s)."
        run.output_payload = {
            **(run.output_payload or {}),
            "workflow_run_id": str(workflow_run_id),
            "steps": completed_steps,
            "checkpoint_id": str(checkpoint.id),
            "memory_snapshot_id": str(memory.id),
            "artifact_id": last_artifact_id,
            "summary": summary,
        }
        flag_modified(run, "output_payload")
        return summary

    async def _template_for_run(
        self,
        *,
        workspace_id: str,
        template_id: UUID | None,
        template_key: str | None,
    ) -> WorkflowTemplate:
        await self.ensure_builtin_templates(workspace_id=workspace_id)
        if template_id is not None:
            return await self.require_template(workspace_id=workspace_id, template_id=template_id)
        if template_key:
            template = await self.get_template_by_key(workspace_id=workspace_id, template_key=template_key)
            if template is not None:
                return template
        raise ValueError("Workflow template not found in workspace")

    async def _version_for_run(
        self,
        *,
        workspace_id: str,
        template: WorkflowTemplate,
        version_id: UUID | None = None,
    ) -> WorkflowTemplateVersion:
        if version_id is not None:
            return await self.require_template_version(workspace_id=workspace_id, template_id=template.id, version_id=version_id)
        preferred = template.current_version or template.latest_version
        for item in template.versions or []:
            if item.version == preferred:
                return item
        if template.versions:
            return sorted(template.versions, key=lambda item: item.created_at)[-1]
        raise ValueError("Workflow template has no versions")

    def _requires_approval(self, *, template: WorkflowTemplate, graph: WorkflowGraph, mode: str) -> bool:
        if mode == "review_first":
            return True
        if mode == "execute_after_approval":
            return False
        if template.risk_level in {"medium", "high"}:
            return True
        return any(node.node_type == "approval_gate" for node in graph.nodes)
