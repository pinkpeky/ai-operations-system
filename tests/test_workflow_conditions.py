"""Workflow graph condition evaluator tests."""

from __future__ import annotations

import pytest

from app.workflow.planner import SafeConditionEvaluator


def test_condition_evaluator_supports_safe_boolean_expressions() -> None:
    evaluator = SafeConditionEvaluator()
    context = {
        "workflow": {"variables": {"requires_review": True, "tier": "medium"}, "status": "running"},
        "step": {"output": {"score": 7}},
        "artifact": {"metadata": {"kind": "report"}},
        "approval": {"status": "approved"},
    }

    assert evaluator.evaluate("workflow.variables.requires_review == true", context) is True
    assert evaluator.evaluate("approval.status == 'approved' and step.output.score == 7", context) is True
    assert evaluator.evaluate("workflow.variables.tier in low,medium,high", context) is True
    assert evaluator.evaluate("exists artifact.metadata.kind", context) is True


def test_condition_evaluator_rejects_python_eval_syntax() -> None:
    evaluator = SafeConditionEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate("__import__('os').system('whoami')", {})
