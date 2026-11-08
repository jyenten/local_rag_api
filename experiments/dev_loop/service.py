"""Persist local non-secret settings and start the same loopback controller."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import sys
from uuid import UUID

from .adapters import LAB, InfrastructureError
from .real_jobs import read_json, write_json

DEFAULT_CONFIG = LAB / '.runs' / 'service.json'
SERVICE = 'local-rag-dev-loop'
FIELDS = {'schema_version', 'service', 'python_executable', 'runs_root', 'allowed_run_ids',
          'source_repo', 'jobs_root', 'max_new_jobs', 'port'}


def absolute(path):
    return str(Path(path).expanduser().absolute())


def validate_profile(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError('Profile has unknown/missing fields; credentials do not belong in this file')
    if type(data['schema_version']) is not int or data['schema_version'] != 1 or data['service'] != SERVICE:
        raise ValueError('Unknown service profile')
    for key in ('python_executable', 'runs_root'):
        if not isinstance(data[key], str) or not Path(data[key]).is_absolute():
            raise ValueError('Profile paths must be absolute')
    if not Path(data['python_executable']).is_file():
        raise ValueError('Configured Python executable is unavailable')
    ids = data['allowed_run_ids']
    if not isinstance(ids, list) or not 1 <= len(ids) <= 20:
        raise ValueError('Register 1-20 exact saved run UUIDs')
    if any(not isinstance(value, str) or str(UUID(value)) != value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError('Run UUIDs must be unique and canonical')
    if type(data['port']) is not int or not 1024 <= data['port'] <= 65535:
        raise ValueError('Profile port must be between 1024 and 65535')
    if type(data['max_new_jobs']) is not int or not 1 <= data['max_new_jobs'] <= 20:
        raise ValueError('Profile new-job allowance must be 1-20')
    source, jobs = data['source_repo'], data['jobs_root']
    if source is None:
        if jobs is not None or data['max_new_jobs'] != 1:
            raise ValueError('Real-job settings require an explicitly configured source repository')
    elif (not isinstance(source, str) or not Path(source).is_absolute()
          or not isinstance(jobs, str) or not Path(jobs).is_absolute()):
        raise ValueError('Real jobs require absolute source and jobs-root paths')
    return data


def read_profile(path):
    return validate_profile(read_json(Path(path)))


def inspect_inputs(profile):
    from .publish import load_bundle
    from .real_bm25.__main__ import read_source

    for run_id in profile['allowed_run_ids']:
        load_bundle(Path(profile['runs_root']) / run_id)
    revision = None
    if profile['source_repo'] is not None:
        _, revision = read_source(Path(profile['source_repo']))
    return {'configuration_valid': True, 'registered_runs': len(profile['allowed_run_ids']),
            'real_jobs_enabled': profile['source_repo'] is not None, 'source_commit': revision,
            'listen_address': '127.0.0.1', 'port': profile['port'],
            'max_new_jobs_per_process': profile['max_new_jobs'], 'runtime_readiness': 'not_checked',
            'merge_allowed': False}


def service_arguments(profile):
    # No pass-through shell, host, arbitrary flags or credential fields.
    args = ['--runs-root', profile['runs_root'], '--port', str(profile['port'])]
    for run_id in profile['allowed_run_ids']:
        args += ['--allow-run', run_id]
    if profile['source_repo'] is not None:
        args += ['--source-repo', profile['source_repo'], '--jobs-root', profile['jobs_root'],
                 '--max-new-jobs', str(profile['max_new_jobs'])]
    return args


def main(argv=None):
    parser = argparse.ArgumentParser(description='Configure/check/start the stable local dev-loop service')
    actions = parser.add_subparsers(dest='action', required=True)
    init = actions.add_parser('init', help='Save local paths/limits once, without credentials')
    init.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    init.add_argument('--runs-root', type=Path, required=True)
    init.add_argument('--allow-run', type=UUID, action='append', required=True)
    init.add_argument('--source-repo', type=Path)
    init.add_argument('--jobs-root', type=Path)
    init.add_argument('--max-new-jobs', type=int, default=1)
    init.add_argument('--port', type=int, default=8766)
    init.add_argument('--replace', action='store_true', help='Replace an existing valid service profile explicitly')
    for name in ('check', 'start'):
        child = actions.add_parser(name)
        child.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        if args.action == 'init':
            config = args.config.absolute()
            if config.exists() or config.is_symlink():
                if not args.replace:
                    raise ValueError('Profile already exists; inspect it before using --replace')
                read_profile(config)  # Never overwrite an unrelated file or a symlink.
            profile = validate_profile({
                'schema_version': 1, 'service': SERVICE, 'python_executable': absolute(sys.executable),
                'runs_root': absolute(args.runs_root), 'allowed_run_ids': [str(value) for value in args.allow_run],
                'source_repo': absolute(args.source_repo) if args.source_repo else None,
                'jobs_root': absolute(args.jobs_root or args.runs_root.parent / 'n8n-real-jobs')
                             if args.source_repo else None,
                'max_new_jobs': args.max_new_jobs, 'port': args.port,
            })
            if args.source_repo is None and args.jobs_root is not None:
                raise ValueError('--jobs-root requires --source-repo')
            inspect_inputs(profile)
            config.parent.mkdir(parents=True, exist_ok=True)
            if any(path.is_symlink() for path in (config, *config.parents)):
                raise ValueError('Service profile must not use symlinks')
            write_json(config, profile)
            print(json.dumps({'configured': True, 'config': str(config), 'credentials_stored': False}))
            return 0
        profile = read_profile(args.config)
        if args.action == 'check':
            print(json.dumps(inspect_inputs(profile), indent=2))
            return 0
        token = os.environ.get('DEV_LOOP_TOKEN', '')
        if not token:
            if not sys.stdin.isatty():
                raise ValueError('Set DEV_LOOP_TOKEN for non-interactive startup; no token is saved in the profile')
            token = getpass.getpass('Saved DEV_LOOP_TOKEN (same as n8n Header Auth): ')
        if len(token) < 24:
            raise ValueError('DEV_LOOP_TOKEN must contain at least 24 characters')
        from .publication_api import main as serve

        previous = os.environ.get('DEV_LOOP_TOKEN')
        os.environ['DEV_LOOP_TOKEN'] = token
        try:
            return serve(service_arguments(profile))
        finally:
            if previous is None:
                os.environ.pop('DEV_LOOP_TOKEN', None)
            else:
                os.environ['DEV_LOOP_TOKEN'] = previous
    except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
