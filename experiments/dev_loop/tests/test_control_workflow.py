"""Workflow security paths and real JavaScript expressions, without an n8n server."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

PATH = Path(__file__).resolve().parents[1] / 'n8n-control-workflow.json'
FLOW = json.loads(PATH.read_text(encoding='utf-8'))
NODES = {node['name']: node for node in FLOW['nodes']}


def js(expression, data, *, execution_id='71', preview=None):
    executable = shutil.which('node')
    if not executable:
        pytest.skip('Node.js expression checks run on GitHub hosted runners')
    script = r'''
const vm = require('node:vm');
const fs = require('node:fs');
const p = JSON.parse(fs.readFileSync(0, 'utf8'));
const context = { $json: p.data, $execution: { id: p.execution_id },
    $: name => { if (name !== 'Zkontrolovat plán') throw Error(name);
                 return { first: () => ({ json: p.preview }) }; } };
const value = vm.runInNewContext('(' + p.expression.slice(3, -2).trim() + ')', context,
                                 { timeout: 1000 });
process.stdout.write(JSON.stringify(value));
'''
    result = subprocess.run([executable, '-e', script], input=json.dumps({
        'expression': expression, 'data': data, 'execution_id': execution_id, 'preview': preview}),
        text=True, capture_output=True, timeout=5)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_import_has_no_secrets_or_hidden_execution_channels_and_uses_only_fixed_endpoints():
    assert FLOW['active'] is False and FLOW['pinData'] == {}
    assert not any('credentials' in node for node in FLOW['nodes'])
    assert not any(node['type'].endswith(('.code', '.executeCommand', '.webhook')) for node in FLOW['nodes'])
    trigger = NODES['Ovládání úloh']
    assert trigger['parameters']['authentication'] == 'basicAuth'
    assert trigger['parameters']['options']['path'] == 'local-rag-control'
    requests = [n for n in FLOW['nodes'] if n['type'].endswith('.httpRequest')]
    assert {n['parameters']['url'] for n in requests} == {
        'http://host.docker.internal:8766/control/preview',
        'http://host.docker.internal:8766/control/execute'}
    for node in requests:
        assert node['retryOnFail'] is False
        assert node['parameters']['genericAuthType'] == 'httpHeaderAuth'
    fields = {f['fieldName']: f for f in trigger['parameters']['formFields']['values']}
    assert set(fields) == {'action', 'task_id', 'request_id'}
    assert fields['action']['defaultValue'] == 'catalog'


def next_nodes(name, output=0):
    return [edge['node'] for edge in FLOW['connections'].get(name, {}).get('main', [[]])[output]]


def test_mutation_path_requires_both_controller_plan_and_human_approval_and_cancel_is_terminal():
    assert next_nodes('Ovládání úloh') == ['Zkontrolovat plán']
    assert next_nodes('Zkontrolovat plán') == ['Vyžaduje schválení?']
    assert next_nodes('Vyžaduje schválení?', 0) == ['Prohlédnout a schválit']
    assert next_nodes('Vyžaduje schválení?', 1) == ['Výsledek a report']
    assert next_nodes('Prohlédnout a schválit') == ['Schváleno?']
    assert next_nodes('Schváleno?', 0) == ['Provést schválenou akci']
    assert next_nodes('Schváleno?', 1) == ['Zrušeno bez provedení']
    assert next_nodes('Zrušeno bez provedení') == []
    assert next_nodes('Výsledek a report') == []
    fields = NODES['Prohlédnout a schválit']['parameters']['formFields']['values']
    assert len(fields) == 1 and fields[0]['defaultValue'] == 'Zrušit'
    for name, key, expected in [('Vyžaduje schválení?', 'requires_approval', True),
                                ('Schváleno?', 'decision', 'Schválit')]:
        condition = NODES[name]['parameters']['conditions']['conditions'][0]
        assert js(condition['leftValue'], {key: expected}) == expected
    assert NODES['Schváleno?']['parameters']['conditions']['conditions'][0]['rightValue'] == 'Schválit'


def test_preview_creates_stable_job_id_only_for_new_generation_and_preserves_explicit_ids():
    expression = NODES['Zkontrolovat plán']['parameters']['jsonBody']
    catalog = json.loads(js(expression, {'action': 'catalog', 'task_id': 'bm25-tokenize-once'}))
    assert catalog['request_id'] is None
    generated = json.loads(js(expression, {'action': 'generate', 'task_id': 'bm25-tokenize-once'}))
    assert generated['request_id'] == '00000000-0000-4000-8000-000000000071'
    explicit = json.loads(js(expression, {'action': 'report', 'task_id': 'bm25-tokenize-once',
                                         'request_id': '  00000000-0000-4000-8000-000000000061  '}))
    assert explicit['request_id'].endswith('000061') and set(explicit) == {'action', 'task_id', 'request_id'}


def test_mutation_uses_reviewed_identity_and_hash_not_tampered_form_fields():
    expression = NODES['Provést schválenou akci']['parameters']['jsonBody']
    plan = {'action': 'publish', 'task_id': 'bm25-tokenize-once',
            'request_id': '00000000-0000-4000-8000-000000000061', 'plan_sha256': 'a' * 64}
    result = json.loads(js(expression, {'decision': 'Schválit', 'action': 'generate',
                                      'request_id': 'other', 'plan_sha256': 'forged'}, preview=plan))
    assert result == {**plan, 'approved': True}


def test_report_and_approval_render_untrusted_code_as_text_with_readable_diff():
    data = {'result': {'diff': '<script>alert(1)</script>\n+ safe code\n'}, 'status': 'view'}
    expressions = [NODES['Výsledek a report']['parameters']['completionMessage'],
                   NODES['Prohlédnout a schválit']['parameters']['options']['formDescription']]
    for expression in expressions:
        rendered = js(expression, data)
        assert '<script>' not in rendered and '&lt;script&gt;' in rendered
        assert 'Diff před / po' in rendered and '\n+ safe code\n' in rendered
