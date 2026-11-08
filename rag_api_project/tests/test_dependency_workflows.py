"""Keep the audited manifests aligned with what Linux CI actually installs."""

from pathlib import Path

import yaml


WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def load_workflow(name):
    # BaseLoader preserves GitHub's `on` key instead of treating it as a YAML 1.1 bool.
    return yaml.load(
        (WORKFLOWS / name).read_text(encoding="utf-8-sig"), Loader=yaml.BaseLoader
    )


def test_locked_installation_has_an_independent_blocking_audit():
    ci = load_workflow("ci.yml")
    audit = load_workflow("pip-audit.yml")
    installed = "requirements-linux-py311.lock.txt"
    assert any(
        installed in step.get("run", "") for step in ci["jobs"]["test"]["steps"]
    )
    audited = {}
    for job in audit["jobs"].values():
        for step in job["steps"]:
            if step.get("uses", "").startswith("pypa/gh-action-pip-audit@"):
                audited[step["with"]["inputs"]] = (job, step)
    for manifest in ("rag_api_project/requirements.txt", f"rag_api_project/{installed}"):
        job, step = audited[manifest]
        assert not job.get("needs"), "One failed audit must not skip the other manifest"
        assert "continue-on-error" not in job
        assert "continue-on-error" not in step
        assert "ignore-vulns" not in step["with"]
        assert step["with"].get("internal-be-careful-allow-failure", "false") == "false"


def test_lock_only_main_changes_trigger_the_audit():
    push = load_workflow("pip-audit.yml")["on"]["push"]
    assert "main" in push["branches"]
    assert "rag_api_project/requirements-linux-py311.lock.txt" in push["paths"]


def test_clean_verification_downloads_the_generated_lock():
    jobs = load_workflow("linux-lock-snapshot.yml")["jobs"]
    verify = jobs["verify-lock"]
    assert verify["needs"] == "generate-lock"
    upload = next(
        step for step in jobs["generate-lock"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    download_index, download = next(
        (index, step) for index, step in enumerate(verify["steps"])
        if step.get("uses", "").startswith("actions/download-artifact@")
    )
    install_index = next(
        index for index, step in enumerate(verify["steps"])
        if "pip install --no-cache-dir -r requirements-linux-py311.lock.txt"
        in step.get("run", "")
    )
    assert upload["with"]["name"] == download["with"]["name"]
    assert download["with"]["path"] == verify["defaults"]["run"]["working-directory"]
    assert download_index < install_index
