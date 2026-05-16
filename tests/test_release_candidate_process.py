import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_candidate_model_loads_and_has_gates() -> None:
    model = json.loads((ROOT / "release/integration/release_candidate_model.json").read_text(encoding="utf-8"))
    assert model["candidate_branch"] == "codex/phase-43-55-release-candidate"
    assert model["source_branch"] == "codex/phase-55-mainline-integration-release-candidate"
    assert model["target_branch"] == "main"
    for gate in ["mainline_readiness", "integration_preflight", "release_preflight", "runtime_hygiene"]:
        assert gate in model["required_gates"]
    assert "force push main" in model["rollback_model"]["forbidden"]


def test_release_candidate_docs_include_required_boundaries() -> None:
    combined = "\n".join(
        [
            (ROOT / "docs/MAINLINE_INTEGRATION_PLAN.md").read_text(encoding="utf-8"),
            (ROOT / "docs/RELEASE_CANDIDATE_PROCESS.md").read_text(encoding="utf-8"),
        ]
    )
    for term in [
        "`main` is the Phase 55 stable baseline",
        "Phase 55 is accepted as the mainline Release Candidate baseline only",
        "Rollback",
        "not code signing",
        "not Kubernetes",
        "not real social automation",
    ]:
        assert term in combined
