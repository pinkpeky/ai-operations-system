"""Generate environment files from deployment profile templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from common import load_profile, profile_path
except ImportError:  # pragma: no cover - package import path for tests.
    from .common import load_profile, profile_path


def parse_env_template(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value
    return values


def render_env(values: dict[str, str]) -> str:
    return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a .env file from a deployment profile.")
    parser.add_argument("--profile", required=True, help="Deployment profile key.")
    parser.add_argument("--output", default=".env.generated", help="Output path. Defaults to .env.generated.")
    parser.add_argument("--override-json", help="Optional JSON file with KEY/VALUE overrides.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    template_path = profile_path(args.profile) / "env.template"
    values = parse_env_template(template_path.read_text(encoding="utf-8"))

    if args.override_json:
        overrides = json.loads(Path(args.override_json).read_text(encoding="utf-8"))
        if not isinstance(overrides, dict):
            raise SystemExit("override JSON must be an object")
        for key, value in overrides.items():
            values[str(key)] = str(value)

    missing = [key for key in profile.get("required_env", []) if not values.get(key)]
    if missing:
        raise SystemExit(f"Missing required env values for {args.profile}: {', '.join(missing)}")

    output = Path(args.output)
    if output.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing env file: {output}. Use --force to overwrite.")

    output.write_text(render_env(values), encoding="utf-8")
    print(json.dumps({"profile": args.profile, "output": str(output), "keys": sorted(values)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
