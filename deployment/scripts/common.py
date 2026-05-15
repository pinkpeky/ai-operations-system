from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / "deployment" / "profiles"


@dataclass(slots=True)
class CheckResult:
    name: str
    status: str
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def profile_path(profile: str) -> Path:
    path = PROFILES_DIR / profile
    if not path.exists():
        raise FileNotFoundError(f"Unknown deployment profile: {profile}")
    return path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_profile(profile: str) -> dict[str, Any]:
    return load_json(profile_path(profile) / "profile.json")


def load_ports(profile: str) -> list[dict[str, Any]]:
    data = load_json(profile_path(profile) / "ports.json")
    return [item for item in data.get("ports", []) if isinstance(item, dict)]


def load_healthchecks(profile: str) -> list[dict[str, Any]]:
    data = load_json(profile_path(profile) / "healthchecks.json")
    return [item for item in data.get("healthchecks", []) if isinstance(item, dict)]


def command_exists(command: str) -> bool:
    executable = "where" if platform.system().lower() == "windows" else "which"
    try:
        subprocess.run(
            [executable, command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return True
    except Exception:
        return False


def port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def port_process_hint(port: int) -> str:
    if platform.system().lower() == "windows":
        try:
            proc = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
                timeout=5,
            )
            matches = [line.strip() for line in proc.stdout.splitlines() if f":{port} " in line]
            return "; ".join(matches[:3]) if matches else "no process details found"
        except Exception as exc:
            return f"process lookup unavailable: {exc}"
    try:
        proc = subprocess.run(
            ["sh", "-c", f"lsof -i :{port} -sTCP:LISTEN -n -P 2>/dev/null | tail -n +2"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=5,
        )
        return proc.stdout.strip() or "no process details found"
    except Exception as exc:
        return f"process lookup unavailable: {exc}"


def http_get_json(url: str, headers: dict[str, str] | None = None, timeout: float = 5.0) -> tuple[bool, str]:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - profile verifier targets configured local endpoints.
            body = response.read(512).decode("utf-8", errors="replace")
            return 200 <= response.status < 300, body
    except URLError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


def env_file_exists(path: str | None) -> bool:
    if not path:
        return False
    return Path(os.path.expandvars(path)).exists()
