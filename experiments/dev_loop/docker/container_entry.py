"""Trusted image entry point. Never run this script on the Windows host."""

import json
import os
import subprocess
import sys
from pathlib import Path

MAX_SOURCE_BYTES = 65536


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"demo-worker", "check"}:
        raise ValueError("Unknown operation")
    # --isolated Python does not add the script directory; add only our immutable image path.
    sys.path.insert(0, "/opt/dev-loop")
    from adapters import DemoWorker
    from tasks import NORMALIZE, get_task

    raw = sys.stdin.buffer.read(524289)
    if len(raw) > 524288:
        raise ValueError("Request too large")
    payload = json.loads(raw)
    task = get_task(payload.get("task_id", NORMALIZE.task_id))
    source = payload["source"]
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Invalid source")
    workspace = Path("/work")
    candidate = workspace / "question.py"
    candidate.write_text(source, encoding="utf-8")
    if sys.argv[1] == "demo-worker":
        if task.task_id != NORMALIZE.task_id:
            raise ValueError("Demo worker supports normalize-question only")
        attempt = payload["attempt"]
        if type(attempt) is not int or attempt not in {1, 2, 3}:
            raise ValueError("Invalid attempt")
        note = DemoWorker().implement(workspace, attempt, payload.get("feedback", ""))
        print(json.dumps({"protocol": 1, "code": candidate.read_text(encoding="utf-8"), "note": note}))
        return 0
    phase = payload["phase"]
    if phase not in {"baseline", "acceptance"}:
        raise ValueError("Invalid phase")
    env = {"PATH": os.environ["PATH"], "HOME": "/tmp",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
           "DEV_LOOP_WORKSPACE": "/work", "DEV_LOOP_PHASE": phase}
    result = subprocess.run([
        sys.executable, "-I", "-m", "pytest", "-q", "-c", "/opt/dev-loop/checks/pytest.ini",
        "--confcutdir", "/opt/dev-loop/checks", "-p", "no:cacheprovider",
        "--junitxml", "/tmp/checks.xml", str(Path("/opt/dev-loop/checks") / task.checks),
    ], cwd=workspace, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    junit = Path("/tmp/checks.xml")
    if junit.is_symlink() or (junit.exists() and junit.stat().st_size > 65536):
        raise ValueError("Invalid evidence file")
    evidence = junit.read_text(encoding="utf-8") if junit.is_file() else ""
    print(json.dumps({"protocol": 1, "task_id": task.task_id, "returncode": result.returncode,
                      "stdout": result.stdout[-8000:], "stderr": result.stderr[-8000:],
                      "junit": evidence}))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
