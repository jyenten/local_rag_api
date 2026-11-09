"""Fixed offline protocol; candidate code never executes in the host controller."""

import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    if sys.argv[1:] != ['check']:
        raise ValueError('Only the fixed citation checker is supported')
    raw = sys.stdin.buffer.read(262145)
    if len(raw) > 262144:
        raise ValueError('Request too large')
    payload = json.loads(raw)
    phase, source = payload['phase'], payload['source']
    if phase not in {'baseline', 'acceptance'} or not isinstance(source, str) or len(source.encode()) > 65536:
        raise ValueError('Invalid source or phase')
    Path('/work/question.py').write_text(source, encoding='utf-8')
    env = {'PATH': os.environ['PATH'], 'HOME': '/tmp', 'PYTHONDONTWRITEBYTECODE': '1',
           'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'DEV_LOOP_WORKSPACE': '/work'}
    command = [sys.executable, '-m', 'pytest', '-q', '-o', 'addopts=', '-p', 'no:cacheprovider',
               '--rootdir', '/opt/citations/checks', '--confcutdir', '/opt/citations/checks',
               '--junitxml', '/tmp/checks.xml', '/opt/citations/checks/test_retrieval_citations.py']
    if phase == 'baseline':
        command += ['-k', 'test_existing_']
    tests = subprocess.run(command, env=env, cwd='/work', capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=15)
    probe = subprocess.run([sys.executable, '-I', '/opt/citations/probe.py'], env=env,
                           cwd='/work', capture_output=True, text=True, timeout=15)
    if probe.returncode:
        raise RuntimeError('Independent citation probe did not complete')
    observed = json.loads(probe.stdout)
    code = 0 if tests.returncode == 0 and (phase == 'baseline' or all(observed.values())) else 1
    evidence = Path('/tmp/checks.xml')
    if evidence.is_symlink() or not evidence.is_file() or evidence.stat().st_size > 65536:
        raise RuntimeError('Invalid test evidence')
    print(json.dumps({'protocol': 1, 'task_id': 'retrieval-citation-provenance', 'returncode': code,
        'regression_returncode': tests.returncode, 'junit': evidence.read_text(encoding='utf-8'),
        'stdout': tests.stdout[-8000:], 'stderr': tests.stderr[-8000:], 'comparison': observed}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
