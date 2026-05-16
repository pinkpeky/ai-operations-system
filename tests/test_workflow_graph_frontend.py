"""Workflow graph frontend integration file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_workflow_graph_page_and_client_exist() -> None:
    main = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard/src/api/workflowClient.ts").read_text(encoding="utf-8")

    assert "Workflow Graphs" in main
    assert "conditional routing" in main
    assert "not a visual DAG builder" in main
    assert "retry_path" in main
    assert "fallback_path" in main
    assert "createReplay" in client
    assert "/workflow-graphs" in client
    assert "/planner" in client


def test_worker_consoles_show_simplified_graph_execution_panel() -> None:
    for relative in ("worker_console/src/main.tsx", "worker_console_desktop/src/main.tsx"):
        main = (ROOT / relative).read_text(encoding="utf-8")
        assert "Graph execution panel" in main
        assert "current_node" in main
        assert "retry_paths" in main
        assert "fallback_paths" in main
        assert "Replay metadata" in main


def test_artifact_clients_include_graph_lineage_fields() -> None:
    for relative in (
        "admin_dashboard/src/api/outputArtifactClient.ts",
        "worker_console/src/api/outputArtifactClient.ts",
        "worker_console_desktop/src/api/outputArtifactClient.ts",
    ):
        client = (ROOT / relative).read_text(encoding="utf-8")
        assert "producing_node_key" in client
        assert "replay_source" in client
        assert "graph_lineage" in client
