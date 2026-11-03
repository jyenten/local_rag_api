"""Fixed offline check for the real BM25 module; never launch on the host."""

import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    if sys.argv[1:] != ['check']:
        raise ValueError('Only the fixed BM25 check is supported')
    raw = sys.stdin.buffer.read(262145)
    if len(raw) > 262144:
        raise ValueError('Request too large')
    payload = json.loads(raw)
    phase = payload['phase']
    if phase not in {'baseline', 'acceptance'}:
        raise ValueError('Invalid phase')
    source = payload['source']
    before = payload['before_source']
    if any(not isinstance(s, str) or len(s.encode('utf-8')) > 65536 for s in (source, before)):
        raise ValueError('Invalid source')
    workspace = Path('/work')
    (workspace / 'app/retrievers').mkdir(parents=True)
    (workspace / 'app/config.py').write_bytes(Path('/opt/bm25/vendor/app/config.py').read_bytes())
    for name in ['app/__init__.py', 'app/retrievers/__init__.py']:
        (workspace / name).write_text('', encoding='utf-8')
    (workspace / 'app/retrievers/bm25.py').write_text(source, encoding='utf-8')
    (workspace / 'before.py').write_text(before, encoding='utf-8')
    # Separate subprocesses prevent candidate imports from altering this control process.
    env = {'PATH': os.environ['PATH'], 'HOME': '/tmp', 'PYTHONPATH': '/work:/opt/bm25/vendor',
           'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
           'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-o', 'addopts=',
                            '--rootdir', '/opt/bm25/vendor/tests',
                            '--confcutdir', '/opt/bm25/vendor/tests', '-p', 'no:cacheprovider',
                            '--junitxml', '/tmp/checks.xml', '/opt/bm25/vendor/tests/test_bm25.py'],
                           cwd='/work', env=env, text=True, encoding='utf-8', errors='replace',
                           capture_output=True, timeout=15)
    comparison = None
    if tests.returncode == 0:
        benchmark = subprocess.run([sys.executable, '-I', '/opt/bm25/benchmark.py'],
                                   cwd='/work', env=env, text=True, encoding='utf-8',
                                   capture_output=True, timeout=15)
        if benchmark.returncode != 0:
            raise RuntimeError('Paired benchmark could not complete')
        comparison = json.loads(benchmark.stdout)
    junit = Path('/tmp/checks.xml')
    if junit.is_symlink() or not junit.is_file() or junit.stat().st_size > 65536:
        raise RuntimeError('Invalid test evidence')
    code = tests.returncode
    if code == 0 and phase == 'acceptance' and not (
            comparison['single_pass_observed'] and comparison['search_results_equal']):
        code = 1
    print(json.dumps({'protocol': 1, 'task_id': 'bm25-tokenize-once',
                      'returncode': code, 'regression_returncode': tests.returncode,
                      'stdout': tests.stdout[-8000:], 'stderr': tests.stderr[-8000:],
                      'junit': junit.read_text(encoding='utf-8'), 'comparison': comparison}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
