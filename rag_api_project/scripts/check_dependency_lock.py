import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_versions(filename):
    versions = {}

    for line in (ROOT / filename).read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        match = re.fullmatch(
            r"([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([^\s;]+)",
            line,
        )

        if not match:
            raise ValueError(f"Unsupported requirement: {line}")

        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        version = match.group(2)

        if name in versions:
            raise ValueError(f"Duplicate dependency: {name}")

        versions[name] = version

    return versions


def main():
    direct = load_versions("requirements.txt")
    locked = load_versions("requirements-linux-py311.lock.txt")

    mismatches = []

    for name, expected in direct.items():
        actual = locked.get(name)

        if actual != expected:
            mismatches.append(
                f"{name}: expected {expected}, locked {actual}"
            )

    if mismatches:
        for mismatch in mismatches:
            print(f"MISMATCH: {mismatch}")
        raise SystemExit(1)

    print(
        f"PASS: {len(direct)} direct dependencies match Linux lock"
    )


if __name__ == "__main__":
    main()
