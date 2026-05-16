"""Built-in workflow template definitions.

These templates are graph metadata only. They do not perform social-platform
automation, remote desktop streaming, ComfyUI, or real OpenClaw actions.
"""

from __future__ import annotations

from typing import Any


BUILTIN_WORKFLOW_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_key": "browser_screenshot_report_graph",
        "name": "Browser Screenshot Report Graph",
        "description": "Open a URL, capture screenshot/page metadata, and package a report artifact.",
        "category": "browser",
        "risk_level": "medium",
        "tags": ["browser", "screenshot", "report"],
        "version": "1",
        "entry_node": "open_url",
        "input_schema": {"type": "object", "required": ["url"], "properties": {"url": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"report_artifact_id": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "open_url", "node_type": "tool_call", "configuration": {"tool": "browser_tool", "action": "navigate"}},
                {"node_key": "screenshot", "node_type": "tool_call", "configuration": {"tool": "browser_tool", "action": "screenshot"}},
                {"node_key": "page_snapshot", "node_type": "tool_call", "configuration": {"tool": "browser_tool", "action": "get_page"}},
                {"node_key": "report_artifact", "node_type": "artifact_transform", "configuration": {"artifact_type": "report"}},
            ],
            "edges": [
                {"source_node_key": "open_url", "target_node_key": "screenshot", "edge_type": "success"},
                {"source_node_key": "screenshot", "target_node_key": "page_snapshot", "edge_type": "success"},
                {"source_node_key": "page_snapshot", "target_node_key": "report_artifact", "edge_type": "success"},
            ],
        },
    },
    {
        "template_key": "content_generation_graph",
        "name": "Content Generation Graph",
        "description": "Generate title, description, hashtags, CTA, and a content draft artifact.",
        "category": "content",
        "risk_level": "low",
        "tags": ["content", "draft"],
        "version": "1",
        "entry_node": "generate_title",
        "input_schema": {"type": "object", "properties": {"topic": {"type": "string"}, "style": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"content_artifact_id": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "generate_title", "node_type": "playbook_step", "configuration": {"part": "title"}},
                {"node_key": "generate_description", "node_type": "playbook_step", "configuration": {"part": "description"}},
                {"node_key": "generate_hashtags", "node_type": "playbook_step", "configuration": {"part": "hashtags"}},
                {"node_key": "generate_cta", "node_type": "playbook_step", "configuration": {"part": "cta"}},
                {"node_key": "content_artifact", "node_type": "artifact_transform", "configuration": {"artifact_type": "content_draft"}},
            ],
            "edges": [
                {"source_node_key": "generate_title", "target_node_key": "generate_description", "edge_type": "success"},
                {"source_node_key": "generate_description", "target_node_key": "generate_hashtags", "edge_type": "success"},
                {"source_node_key": "generate_hashtags", "target_node_key": "generate_cta", "edge_type": "success"},
                {"source_node_key": "generate_cta", "target_node_key": "content_artifact", "edge_type": "success"},
            ],
        },
    },
    {
        "template_key": "rag_answer_graph",
        "name": "RAG Answer Graph",
        "description": "Retrieve documents and summarize an answer artifact.",
        "category": "rag",
        "risk_level": "low",
        "tags": ["rag", "knowledge"],
        "version": "1",
        "entry_node": "retrieve_docs",
        "input_schema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"rag_artifact_id": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "retrieve_docs", "node_type": "tool_call", "configuration": {"tool": "rag_search_tool"}},
                {"node_key": "summarize_answer", "node_type": "playbook_step", "configuration": {"summary": True}},
                {"node_key": "rag_artifact", "node_type": "artifact_transform", "configuration": {"artifact_type": "rag_answer"}},
            ],
            "edges": [
                {"source_node_key": "retrieve_docs", "target_node_key": "summarize_answer", "edge_type": "success"},
                {"source_node_key": "summarize_answer", "target_node_key": "rag_artifact", "edge_type": "success"},
            ],
        },
    },
    {
        "template_key": "approval_then_browser_graph",
        "name": "Approval Then Browser Graph",
        "description": "Require approval before a browser action and package resulting artifact metadata.",
        "category": "approval",
        "risk_level": "medium",
        "tags": ["approval", "browser"],
        "version": "1",
        "entry_node": "approval_gate",
        "input_schema": {"type": "object", "required": ["url"], "properties": {"url": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"package_artifact_id": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "approval_gate", "node_type": "approval_gate"},
                {"node_key": "browser_action", "node_type": "tool_call", "configuration": {"tool": "browser_tool"}},
                {"node_key": "artifact_package", "node_type": "artifact_transform", "configuration": {"package": True}},
            ],
            "edges": [
                {"source_node_key": "approval_gate", "target_node_key": "browser_action", "edge_type": "conditional", "condition_expression": "approval.status == approved"},
                {"source_node_key": "browser_action", "target_node_key": "artifact_package", "edge_type": "success"},
            ],
        },
    },
    {
        "template_key": "openclaw_mock_inspect_graph",
        "name": "OpenClaw Mock Inspect Graph",
        "description": "Run a mock OpenClaw inspect action and create a JSON artifact.",
        "category": "openclaw",
        "risk_level": "medium",
        "tags": ["openclaw", "mock"],
        "version": "1",
        "entry_node": "mock_inspect",
        "input_schema": {"type": "object", "properties": {"target": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"json_artifact_id": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "mock_inspect", "node_type": "tool_call", "configuration": {"tool": "openclaw_tool", "mock": True}},
                {"node_key": "json_artifact", "node_type": "artifact_transform", "configuration": {"artifact_type": "json"}},
            ],
            "edges": [{"source_node_key": "mock_inspect", "target_node_key": "json_artifact", "edge_type": "success"}],
        },
    },
    {
        "template_key": "task_retry_demo_graph",
        "name": "Task Retry Demo Graph",
        "description": "Demonstrate a simulated failure path, retry edge, and fallback summary.",
        "category": "task",
        "risk_level": "low",
        "tags": ["task", "retry", "fallback"],
        "version": "1",
        "entry_node": "simulated_failure",
        "input_schema": {"type": "object", "properties": {"simulate_failure": {"type": "boolean"}}},
        "output_schema": {"type": "object", "properties": {"fallback_summary": {"type": "string"}}},
        "graph_definition": {
            "nodes": [
                {"node_key": "simulated_failure", "node_type": "no_op", "retry_policy": {"max_retries": 1}},
                {"node_key": "retry_route", "node_type": "retry"},
                {"node_key": "fallback_summary", "node_type": "playbook_step"},
            ],
            "edges": [
                {"source_node_key": "simulated_failure", "target_node_key": "retry_route", "edge_type": "retry"},
                {"source_node_key": "simulated_failure", "target_node_key": "fallback_summary", "edge_type": "fallback"},
            ],
        },
    },
]
