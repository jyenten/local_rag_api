"""Host-reviewed task registrations. HTTP never supplies modules, paths or tests."""

from dataclasses import dataclass

from .adapters import InfrastructureError

BM25 = 'bm25-tokenize-once'
CITATIONS = 'retrieval-citation-provenance'
REAL_TASK_IDS = (BM25, CITATIONS)


@dataclass(frozen=True)
class RegisteredTask:
    task_id: str
    module: object
    description: str
    backend: str
    commit_message: str
    pr_title: str
    pr_body: str

    @property
    def manifest(self):
        return self.module.MANIFEST

    @property
    def target(self):
        return self.manifest['target']

    @property
    def fixed_files(self):
        return {} if self.task_id == BM25 else self.module.fixed_files()

    @property
    def allowed_files(self):
        return [self.target, *self.fixed_files]

    def public_comparison(self, comparison):
        if self.task_id == CITATIONS:
            self.module.validate_comparison(comparison)
            return comparison
        return {**{key: comparison[key] for key in (
            'document_count', 'paired_trials', 'search_results_equal', 'single_pass_observed')},
            **{key: {side: comparison[key][side] for side in ('before', 'after')}
               for key in ('median_init_ms', 'init_tokenize_calls')}}


def get_registered_task(task_id=BM25):
    if task_id == BM25:
        from .real_bm25 import __main__ as module

        return RegisteredTask(BM25, module, 'Historical BM25 tokenize-once optimization',
            'codex-real-bm25-docker', 'perf(bm25): tokenize each document once during initialization',
            'perf(bm25): reuse validated document tokens',
            'BM25 currently tokenizes each document twice during construction. Reuse the validated '
            'tokens in the same sorted record. Only the constructor body changes.\n\n'
            'Publication reran 68 regressions before/after in the pinned offline Docker checker, '
            'requiring identical results for six synthetic queries and tokenizer calls 2000 → 1000. '
            'This does not establish real-corpus or end-to-end latency improvement.')
    if task_id == CITATIONS:
        from .citations import task as module

        return RegisteredTask(CITATIONS, module, 'Preserve source/page of selected context lines',
            'codex-real-citations-docker', 'fix(retrieval): preserve citation provenance in fallback context',
            'fix(retrieval): preserve source metadata and negative-score candidates',
            'Fallback context can attach the first document metadata to evidence from another source, '
            'and a relative threshold can discard every negative-scoring candidate. Change only the '
            'two registered method bodies. Include the host-reviewed fixed regression file.\n\n'
            'Publication reran 3 baseline and 15 acceptance cases plus fresh-process provenance '
            'probes in pinned offline Docker. Synthetic texts and mocked model/storage constructors '
            'test the real module; this does not measure real-PDF accuracy or latency.')
    raise InfrastructureError('Unknown host-registered real task')
