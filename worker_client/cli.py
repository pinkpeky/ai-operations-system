"""Worker Client CLI。"""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Sequence

import uvicorn

from worker_client.config import load_worker_client_config, load_worker_state
from worker_client.heartbeat import heartbeat_loop, send_heartbeat_once
from worker_client.logging import configure_worker_logging, log_event
from worker_client.registration import register_worker
from worker_client.runtime import create_worker_client_app
from worker_client.runtime_manager import WorkerRuntimeManager


def build_parser() -> argparse.ArgumentParser:
    """构造 CLI parser。"""

    parser = argparse.ArgumentParser(prog="python -m worker_client.cli")
    parser.add_argument("--config", default=None, help="Path to worker_config.yaml")
    parser.add_argument("--log-level", default="INFO", help="Python logging level")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="Register this machine as a Browser Worker")
    register.add_argument("--force", action="store_true", help="Force re-registration even if worker_state.json exists")

    heartbeat = subparsers.add_parser("heartbeat", help="Run heartbeat loop")
    heartbeat.add_argument("--status", default="online", choices=["online", "busy", "error"], help="Heartbeat status")
    heartbeat.add_argument("--once", action="store_true", help="Send one heartbeat and exit")

    serve = subparsers.add_parser("serve", help="Serve local Worker Runtime API")
    serve.add_argument("--host", default=None, help="Override runtime host")
    serve.add_argument("--port", type=int, default=None, help="Override runtime port")

    start = subparsers.add_parser("start", help="Register if needed, serve runtime, and run heartbeat loop")
    start.add_argument("--force-register", action="store_true", help="Force registration before start")
    start.add_argument("--host", default=None, help="Override runtime host")
    start.add_argument("--port", type=int, default=None, help="Override runtime port")
    return parser


async def _serve_runtime_with_manager(
    config,
    manager: WorkerRuntimeManager,
    log_level: str,
) -> int:  # type: ignore[no-untyped-def]
    """在当前 event loop 内运行 runtime，并把状态同步给 Runtime Manager。"""

    state = load_worker_state(config.state_path)
    app = create_worker_client_app(config, state=state, manager=manager)
    server_config = uvicorn.Config(app, host=config.runtime_host, port=config.runtime_port, log_level=log_level)
    server = uvicorn.Server(server_config)
    manager.attach_server(server)
    manager.mark_runtime_running(True)
    log_event("worker runtime serve started", extra={"host": config.runtime_host, "port": config.runtime_port})
    try:
        await server.serve()
    finally:
        manager.mark_runtime_running(False)
        log_event("worker runtime serve stopped")
    return 0


async def _run_start(args: argparse.Namespace) -> int:
    """同时启动 runtime server 与 heartbeat loop。"""

    config = load_worker_client_config(args.config)
    if args.host:
        config.runtime_host = args.host
    if args.port:
        config.runtime_port = args.port
    config.validate_config()
    await register_worker(config, force=args.force_register)
    manager = WorkerRuntimeManager(config)
    manager.start_heartbeat()
    try:
        return await _serve_runtime_with_manager(config, manager, str(args.log_level).lower())
    finally:
        manager.stop_heartbeat()


async def _run_async(args: argparse.Namespace) -> int:
    """执行异步 CLI 命令。"""

    config = load_worker_client_config(args.config)
    config.validate_config()
    if args.command == "register":
        result = await register_worker(config, force=args.force)
        print(f"worker_id={result.worker_id} registered={result.registered} state_path={Path(config.state_path)}")
        return 0
    if args.command == "heartbeat":
        if args.once:
            result = await send_heartbeat_once(config, status=args.status)
            print(f"worker_id={result.worker_id} heartbeat={result.success} auth_status={result.auth_status}")
            return 0 if result.success else 1
        await heartbeat_loop(config, status=args.status)
        return 0
    if args.command == "serve":
        if args.host:
            config.runtime_host = args.host
        if args.port:
            config.runtime_port = args.port
        config.validate_config()
        manager = WorkerRuntimeManager(config)
        return await _serve_runtime_with_manager(config, manager, str(args.log_level).lower())
    if args.command == "start":
        return await _run_start(args)
    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint。"""

    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(levelname)s:%(name)s:%(message)s",
    )
    configure_worker_logging()
    try:
        return asyncio.run(_run_async(args))
    except KeyboardInterrupt:
        print("worker_client stopped")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
