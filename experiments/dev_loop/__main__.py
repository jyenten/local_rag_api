"""Run from the repository root: python -m experiments.dev_loop --help."""

import argparse
import ipaddress
import json
import os
import uuid
from pathlib import Path

from .adapters import LAB, TASK_ID, CodexWorker, DemoWorker, PytestChecker
from .workflow import run_job
from .tasks import TASK_IDS, get_task


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded LangGraph/Codex/n8n experiment")
    parser.add_argument("--backend", choices=["demo", "codex"], default="demo")
    parser.add_argument("--isolation", choices=["host", "docker"], default="host")
    parser.add_argument("--task", choices=TASK_IDS, default=TASK_ID)
    parser.add_argument("--docker-image", default=None, help="Override the fixed task's checker image")
    parser.add_argument("--codex-image", default=None, help="Override the fixed task's Codex image")
    parser.add_argument("--codex-auth-volume", default="local-rag-codex-auth")
    parser.add_argument("--serve", action="store_true", help="Expose the local n8n HTTP bridge")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--runs-dir", type=Path, default=LAB / ".runs")
    parser.add_argument("--request-id", default=None, help="Reuse an ID to read its completed result")
    parser.add_argument("--cycles", type=int, help="Measure 1-20 independent runs, not repair attempts")
    parser.add_argument("--report-dir", type=Path, help="New directory for batch data and chart")
    parser.add_argument("--allow-non-loopback", action="store_true",
                        help="Explicitly allow binding beyond the local machine")
    args = parser.parse_args()
    task = get_task(args.task)
    if args.task != TASK_ID and (args.backend != "codex" or args.isolation != "docker"):
        parser.error(f"{args.task} requires --backend codex --isolation docker")
    if args.cycles is not None:
        if not 1 <= args.cycles <= 20:
            parser.error("--cycles must be between 1 and 20")
        if args.serve or args.request_id:
            parser.error("--cycles cannot be combined with --serve or --request-id")
    elif args.report_dir:
        parser.error("--report-dir requires --cycles")
    if args.isolation == "docker":
        from .docker_adapters import DockerDemoWorker, DockerPytestChecker, DockerRunner

        runner = DockerRunner(args.docker_image or task.checker_image)
        worker, checker = DockerDemoWorker(runner), DockerPytestChecker(runner, args.task)
        if args.backend == "codex":
            from .codex_docker import DockerCodexWorker

            try:
                worker = DockerCodexWorker(args.codex_image or task.codex_image, args.codex_auth_volume, task_id=args.task)
            except ValueError as exc:
                parser.error(str(exc))
    else:
        worker = DemoWorker() if args.backend == "demo" else CodexWorker()
        checker = PytestChecker()
    if args.cycles is not None:
        from .batch import render_report, run_batch

        output = args.report_dir or LAB / ".runs/reports" / str(uuid.uuid4())
        report = run_batch(args.cycles, output, worker, checker)
        destination = render_report(report, output)
        print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))
        print(f"Report: {destination.resolve()}")
        return 0 if report["status_counts"].get("review_ready") == args.cycles else 1
    if args.serve:
        import uvicorn

        from .api import create_app

        token = os.environ.get("DEV_LOOP_TOKEN", "")
        if len(token) < 24:
            parser.error("Set DEV_LOOP_TOKEN to a random value of at least 24 characters")
        try:
            loopback = ipaddress.ip_address(args.host).is_loopback
        except ValueError:
            loopback = args.host == "localhost"
        if not loopback and not args.allow_non_loopback:
            parser.error("Binding beyond loopback requires --allow-non-loopback")
        uvicorn.run(create_app(worker, checker, args.runs_dir, token), host=args.host, port=args.port)
        return 0
    report = run_job(args.request_id or str(uuid.uuid4()), args.task, args.runs_dir, worker, checker)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "review_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
