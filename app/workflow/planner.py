"""Workflow graph validation, condition evaluation, and next-node planning."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import WorkflowGraphEdgeType
from app.models.workflow import WorkflowGraph, WorkflowGraphEdge, WorkflowGraphNode, WorkflowRun, WorkflowStep


@dataclass(slots=True)
class WorkflowPlannerResult:
    """Structured planner result returned by APIs and services."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    entry_node: str | None = None
    execution_order: list[str] = field(default_factory=list)
    current_node: str | None = None
    next_nodes: list[str] = field(default_factory=list)
    skipped_nodes: list[str] = field(default_factory=list)
    retry_paths: list[dict[str, Any]] = field(default_factory=list)
    fallback_paths: list[dict[str, Any]] = field(default_factory=list)
    condition_results: list[dict[str, Any]] = field(default_factory=list)
    dependency_state: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "entry_node": self.entry_node,
            "execution_order": self.execution_order,
            "current_node": self.current_node,
            "next_nodes": self.next_nodes,
            "skipped_nodes": self.skipped_nodes,
            "retry_paths": self.retry_paths,
            "fallback_paths": self.fallback_paths,
            "condition_results": self.condition_results,
            "dependency_state": self.dependency_state,
        }


class SafeConditionEvaluator:
    """Small condition evaluator for workflow graph routing.

    It intentionally does not call Python ``eval``. Supported syntax:
    ``==``, ``!=``, ``and``, ``or``, ``in``, and ``exists`` over dotted paths.
    """

    _comparison_pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(==|!=|in)\s*(.+?)\s*$")

    def evaluate(self, expression: str | None, context: dict[str, Any]) -> bool:
        if not expression:
            return True
        expression = expression.strip()
        if not expression:
            return True
        if any(token in expression for token in ("__", "(", ")", "[", "]", "{", "}", ";", "\n", "\r")):
            raise ValueError("Unsupported condition syntax")
        or_parts = self._split_bool(expression, "or")
        return any(all(self._eval_atom(part, context) for part in self._split_bool(or_part, "and")) for or_part in or_parts)

    def _eval_atom(self, atom: str, context: dict[str, Any]) -> bool:
        atom = atom.strip()
        if atom.startswith("exists "):
            return self._resolve(atom.removeprefix("exists ").strip(), context) is not None
        if atom.endswith(" exists"):
            return self._resolve(atom.removesuffix(" exists").strip(), context) is not None
        match = self._comparison_pattern.match(atom)
        if not match:
            raise ValueError(f"Unsupported condition atom: {atom}")
        left_path, operator, right_raw = match.groups()
        left = self._resolve(left_path, context)
        if operator == "in":
            right_values = [self._parse_literal(part.strip(), context) for part in right_raw.split(",")]
            return left in right_values
        right = self._parse_literal(right_raw.strip(), context)
        return left == right if operator == "==" else left != right

    def _split_bool(self, expression: str, operator: str) -> list[str]:
        parts = re.split(rf"\s+{operator}\s+", expression)
        return [part.strip() for part in parts if part.strip()]

    def _parse_literal(self, raw: str, context: dict[str, Any]) -> Any:
        lowered = raw.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered == "null":
            return None
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            return raw[1:-1]
        if re.match(r"^-?\d+$", raw):
            return int(raw)
        if re.match(r"^-?\d+\.\d+$", raw):
            return float(raw)
        if "." in raw:
            value = self._resolve(raw, context)
            if value is not None:
                return value
        return raw

    def _resolve(self, dotted_path: str, context: dict[str, Any]) -> Any:
        current: Any = context
        for part in dotted_path.split("."):
            if part == "":
                return None
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)
            if current is None:
                return None
        return current


class WorkflowExecutionPlanner:
    """Validates workflow graphs and plans conditional next-node execution."""

    def __init__(self) -> None:
        self.evaluator = SafeConditionEvaluator()

    def validate_graph(
        self,
        *,
        graph: WorkflowGraph | None = None,
        nodes: list[WorkflowGraphNode] | None = None,
        edges: list[WorkflowGraphEdge] | None = None,
        entry_node: str | None = None,
    ) -> WorkflowPlannerResult:
        graph_nodes = nodes if nodes is not None else (list(graph.nodes) if graph is not None else [])
        graph_edges = edges if edges is not None else (list(graph.edges) if graph is not None else [])
        entry = entry_node or (graph.entry_node if graph is not None else None)
        errors: list[str] = []
        node_keys = [node.node_key for node in graph_nodes]
        node_set = set(node_keys)
        if not entry:
            errors.append("entry node is required")
        elif entry not in node_set:
            errors.append(f"entry node not found: {entry}")
        if len(node_keys) != len(node_set):
            errors.append("duplicate node_key detected")
        for edge in graph_edges:
            if edge.source_node_key not in node_set:
                errors.append(f"edge source not found: {edge.source_node_key}")
            if edge.target_node_key not in node_set:
                errors.append(f"edge target not found: {edge.target_node_key}")
            if edge.edge_type not in {item.value for item in WorkflowGraphEdgeType}:
                errors.append(f"unsupported edge_type: {edge.edge_type}")
            if edge.condition_expression:
                try:
                    self.evaluator.evaluate(edge.condition_expression, self._empty_context())
                except ValueError as exc:
                    errors.append(f"invalid condition on {edge.source_node_key}->{edge.target_node_key}: {exc}")
        order, cycle_error = self._topological_order(node_keys=node_keys, edges=graph_edges)
        if cycle_error:
            errors.append(cycle_error)
        reachable = self._reachable(entry, graph_edges) if entry else set()
        skipped = sorted(node_set - reachable)
        return WorkflowPlannerResult(
            valid=not errors,
            errors=errors,
            entry_node=entry,
            execution_order=order,
            skipped_nodes=skipped,
            dependency_state={key: self._dependencies_for(key, graph_edges) for key in node_keys},
        )

    def plan_next(
        self,
        *,
        graph: WorkflowGraph,
        workflow: WorkflowRun | None = None,
        completed_steps: list[WorkflowStep] | None = None,
        current_node: str | None = None,
        status: str = "success",
    ) -> WorkflowPlannerResult:
        validation = self.validate_graph(graph=graph)
        if not validation.valid:
            return validation
        node_key = current_node or (workflow.current_node_key if workflow is not None else None) or graph.entry_node
        context = self._runtime_context(workflow=workflow, completed_steps=completed_steps or [])
        outgoing = sorted(
            [edge for edge in graph.edges if edge.source_node_key == node_key],
            key=lambda edge: (edge.priority, edge.target_node_key),
        )
        next_nodes: list[str] = []
        condition_results: list[dict[str, Any]] = []
        retry_paths: list[dict[str, Any]] = []
        fallback_paths: list[dict[str, Any]] = []
        for edge in outgoing:
            allowed = self._edge_allowed(edge=edge, status=status, context=context)
            condition_results.append(
                {
                    "source_node_key": edge.source_node_key,
                    "target_node_key": edge.target_node_key,
                    "edge_type": edge.edge_type,
                    "condition_expression": edge.condition_expression,
                    "matched": allowed,
                }
            )
            if edge.edge_type == WorkflowGraphEdgeType.RETRY.value:
                retry_paths.append({"from": edge.source_node_key, "to": edge.target_node_key, "matched": allowed})
            if edge.edge_type == WorkflowGraphEdgeType.FALLBACK.value:
                fallback_paths.append({"from": edge.source_node_key, "to": edge.target_node_key, "matched": allowed})
            if allowed and edge.target_node_key not in next_nodes:
                next_nodes.append(edge.target_node_key)
        reachable = self._reachable(graph.entry_node, list(graph.edges))
        skipped = sorted(set(node.node_key for node in graph.nodes) - reachable)
        return WorkflowPlannerResult(
            valid=True,
            entry_node=graph.entry_node,
            execution_order=validation.execution_order,
            current_node=node_key,
            next_nodes=next_nodes,
            skipped_nodes=skipped,
            retry_paths=retry_paths,
            fallback_paths=fallback_paths,
            condition_results=condition_results,
            dependency_state=validation.dependency_state,
        )

    def _edge_allowed(self, *, edge: WorkflowGraphEdge, status: str, context: dict[str, Any]) -> bool:
        if edge.edge_type == WorkflowGraphEdgeType.SUCCESS.value and status != "success":
            return False
        if edge.edge_type in {WorkflowGraphEdgeType.FAILURE.value, WorkflowGraphEdgeType.FALLBACK.value} and status != "failure":
            return False
        if edge.edge_type == WorkflowGraphEdgeType.RETRY.value and status != "retry":
            return False
        if edge.condition_expression:
            return self.evaluator.evaluate(edge.condition_expression, context)
        return edge.edge_type in {
            WorkflowGraphEdgeType.SUCCESS.value,
            WorkflowGraphEdgeType.ALWAYS.value,
            WorkflowGraphEdgeType.CONDITIONAL.value,
            WorkflowGraphEdgeType.FALLBACK.value,
            WorkflowGraphEdgeType.RETRY.value,
        }

    def _runtime_context(self, *, workflow: WorkflowRun | None, completed_steps: list[WorkflowStep]) -> dict[str, Any]:
        latest_step = completed_steps[-1] if completed_steps else None
        steps_by_node = {
            step.node_key or step.step_name: {
                "status": step.status,
                "output": step.output_payload or {},
                "error": step.error,
                "metadata": step.step_metadata or {},
            }
            for step in completed_steps
        }
        return {
            "workflow": {
                "status": workflow.status if workflow is not None else None,
                "variables": workflow.variables if workflow is not None else {},
                "context": workflow.context if workflow is not None else {},
                "current_node_key": workflow.current_node_key if workflow is not None else None,
            },
            "step": {
                **steps_by_node,
                "status": latest_step.status if latest_step is not None else None,
                "output": latest_step.output_payload if latest_step is not None else {},
                "metadata": latest_step.step_metadata if latest_step is not None else {},
            },
            "artifact": {"metadata": (workflow.context or {}).get("artifact_metadata", {}) if workflow is not None else {}},
            "approval": {"status": (workflow.context or {}).get("approval_status") if workflow is not None else None},
        }

    def _empty_context(self) -> dict[str, Any]:
        return {
            "workflow": {"variables": {}, "status": None, "context": {}},
            "step": {},
            "artifact": {"metadata": {}},
            "approval": {"status": None},
        }

    def _topological_order(self, *, node_keys: list[str], edges: list[WorkflowGraphEdge]) -> tuple[list[str], str | None]:
        node_set = set(node_keys)
        indegree = {key: 0 for key in node_keys}
        adjacency: dict[str, list[str]] = {key: [] for key in node_keys}
        for edge in edges:
            if edge.source_node_key in node_set and edge.target_node_key in node_set:
                adjacency[edge.source_node_key].append(edge.target_node_key)
                indegree[edge.target_node_key] += 1
        queue = sorted([key for key, degree in indegree.items() if degree == 0])
        order: list[str] = []
        while queue:
            key = queue.pop(0)
            order.append(key)
            for target in sorted(adjacency[key]):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
                    queue.sort()
        if len(order) != len(node_keys):
            return order, "cycle detected in workflow graph"
        return order, None

    def _reachable(self, entry_node: str | None, edges: list[WorkflowGraphEdge]) -> set[str]:
        if not entry_node:
            return set()
        adjacency: dict[str, list[str]] = {}
        for edge in edges:
            adjacency.setdefault(edge.source_node_key, []).append(edge.target_node_key)
        seen = {entry_node}
        queue = [entry_node]
        while queue:
            key = queue.pop(0)
            for target in adjacency.get(key, []):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    def _dependencies_for(self, node_key: str, edges: list[WorkflowGraphEdge]) -> dict[str, Any]:
        incoming = [edge for edge in edges if edge.target_node_key == node_key]
        return {
            "dependencies": [edge.source_node_key for edge in incoming],
            "dependency_count": len(incoming),
        }
