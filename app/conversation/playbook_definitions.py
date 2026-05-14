"""Built-in Conversation Playbook definitions.

These templates are deliberately small and deterministic. They standardize
common Conversation Runtime flows without becoming a full workflow builder.
"""

from __future__ import annotations

from typing import Any


BUILTIN_PLAYBOOKS: list[dict[str, Any]] = [
    {
        "name": "browser_search_summary",
        "description": "Open a page, fetch browser content, and summarize the result.",
        "category": "browser",
        "risk_level": "medium",
        "default_inputs": {"url": "https://example.com", "query": "example page summary"},
        "metadata": {"builtin": True, "phase": "40"},
        "steps": [
            {
                "step_type": "tool",
                "title": "Open page and collect browser content",
                "route_name": "browser",
                "selected_tool": "browser_tool",
                "route_type": "tool",
                "tool_input": {
                    "action_type": "navigate_and_screenshot",
                    "target": "{url}",
                    "url": "{url}",
                    "screenshot_name": "playbook-search-summary",
                    "metadata": {"playbook": "browser_search_summary"},
                },
            },
            {"step_type": "summarize", "title": "Summarize browser result"},
        ],
    },
    {
        "name": "browser_screenshot_report",
        "description": "Open a page, capture a screenshot, fetch title/content, and prepare a report.",
        "category": "browser",
        "risk_level": "medium",
        "default_inputs": {"url": "https://example.com"},
        "metadata": {"builtin": True, "phase": "40"},
        "steps": [
            {
                "step_type": "tool",
                "title": "Open page and capture screenshot",
                "route_name": "browser",
                "selected_tool": "browser_tool",
                "route_type": "tool",
                "tool_input": {
                    "action_type": "navigate_and_screenshot",
                    "target": "{url}",
                    "url": "{url}",
                    "screenshot_name": "playbook-screenshot-report",
                    "metadata": {"playbook": "browser_screenshot_report"},
                },
            },
            {"step_type": "summarize", "title": "Generate screenshot report"},
        ],
    },
    {
        "name": "rag_answer",
        "description": "Run knowledge-base retrieval and return a concise answer foundation.",
        "category": "rag",
        "risk_level": "low",
        "default_inputs": {"query": "What is in the knowledge base?", "collection_name": None, "top_k": 5},
        "metadata": {"builtin": True, "phase": "40"},
        "steps": [
            {
                "step_type": "tool",
                "title": "Search knowledge base",
                "route_name": "rag_search",
                "selected_tool": "rag_search_tool",
                "route_type": "tool",
                "tool_input": {
                    "query": "{query}",
                    "collection_name": "{collection_name}",
                    "top_k": "{top_k}",
                    "final_top_k": "{top_k}",
                    "search_mode": "hybrid",
                },
            },
            {"step_type": "summarize", "title": "Summarize RAG result"},
        ],
    },
    {
        "name": "content_generation",
        "description": "Generate short-video title, description, hashtags, and CTA.",
        "category": "content",
        "risk_level": "low",
        "default_inputs": {"topic": "AI automation operations", "platform": "short_video", "style": "professional concise"},
        "metadata": {"builtin": True, "phase": "40"},
        "steps": [
            {
                "step_type": "agent",
                "title": "Generate content draft",
                "route_name": "content",
                "route_type": "agent",
                "tool_input": {
                    "topic": "{topic}",
                    "platform": "{platform}",
                    "style": "{style}",
                },
            }
        ],
    },
    {
        "name": "trend_research_draft",
        "description": "Create a simulated trend research plan and content draft without social-platform automation.",
        "category": "research",
        "risk_level": "low",
        "default_inputs": {"topic": "AI automation operations", "platform": "short_video", "style": "research concise"},
        "metadata": {"builtin": True, "phase": "40", "simulated_research": True},
        "steps": [
            {
                "step_type": "planning",
                "title": "Create trend research plan",
                "route_name": "planning",
                "route_type": "planning",
                "tool_input": {
                    "root_goal": "Research trend signals for {topic} and draft content. This is simulated research only.",
                    "metadata": {"playbook": "trend_research_draft", "simulated": True},
                },
            },
            {
                "step_type": "agent",
                "title": "Draft content from simulated research",
                "route_name": "content",
                "route_type": "agent",
                "tool_input": {
                    "topic": "{topic}",
                    "platform": "{platform}",
                    "style": "{style}",
                },
            },
        ],
    },
    {
        "name": "openclaw_mock_device_check",
        "description": "Run a mock OpenClaw device inspection. It never calls real OpenClaw or a real device.",
        "category": "openclaw",
        "risk_level": "medium",
        "default_inputs": {"target": "mock-device"},
        "metadata": {"builtin": True, "phase": "40", "mock": True},
        "steps": [
            {
                "step_type": "tool",
                "title": "Run mock device inspection",
                "route_name": "openclaw",
                "selected_tool": "openclaw_tool",
                "route_type": "tool",
                "tool_input": {
                    "action_type": "execute_action",
                    "openclaw_action_type": "mock_inspect",
                    "target": "{target}",
                    "input_payload": {"source": "conversation_playbook"},
                    "metadata": {"playbook": "openclaw_mock_device_check", "mock": True},
                },
            }
        ],
    },
]
