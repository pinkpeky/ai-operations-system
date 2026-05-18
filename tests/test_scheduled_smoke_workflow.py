from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_server_docker_smoke_has_daily_schedule_and_default_profile() -> None:
    path = ROOT / ".github/workflows/server-docker-smoke.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    job = workflow["jobs"]["server-docker-smoke"]

    assert 'cron: "0 19 * * *"' in text
    assert "03:00 Asia/Shanghai" in text
    assert job["env"]["SMOKE_PROFILE"] == "${{ inputs.profile || 'server-docker' }}"
    assert job["name"] == "Docker compose smoke (${{ inputs.profile || 'server-docker' }})"
    assert workflow["concurrency"]["cancel-in-progress"] is False


def test_scheduled_smoke_docs_record_acceptance_and_artifacts() -> None:
    text = (ROOT / "docs/SCHEDULED_SMOKE.md").read_text(encoding="utf-8")

    assert "19:00 UTC" in text
    assert "03:00 Asia/Shanghai" in text
    assert "<profile>-readiness-report" in text
    assert "server-docker-smoke-logs" in text
    assert "Release smoke matrix passes with `--strict`" in text
