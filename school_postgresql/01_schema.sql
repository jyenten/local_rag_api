-- Školní PostgreSQL model, 7 tabulek (oddělený od provozního RAG).
-- Spouštět v NOVÉ databázi; tento skript neprovádí DROP.
BEGIN;
CREATE SCHEMA school_rag;

CREATE TABLE school_rag.documents (
    document_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_filename text NOT NULL UNIQUE,
    file_sha256 char(64),
    registered_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT documents_filename_nonblank CHECK (btrim(source_filename) <> ''),
    CONSTRAINT documents_sha256_valid CHECK (
        file_sha256 IS NULL OR file_sha256 ~ '^[0-9a-f]{64}$'
    )
);

CREATE TABLE school_rag.evaluation_datasets (
    dataset_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name text NOT NULL CHECK (dataset_name IN ('dev','random','test')),
    source_path text NOT NULL,
    source_git_blob_sha char(40) NOT NULL,
    source_commit_sha char(40) NOT NULL,
    imported_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT datasets_revision_unique UNIQUE (dataset_name, source_git_blob_sha),
    CONSTRAINT datasets_id_name_unique UNIQUE (dataset_id, dataset_name),
    CONSTRAINT datasets_git_sha_valid CHECK (
        source_git_blob_sha ~ '^[0-9a-f]{40}$'
        AND source_commit_sha ~ '^[0-9a-f]{40}$'
    )
);

CREATE TABLE school_rag.evaluation_questions (
    question_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id bigint NOT NULL REFERENCES school_rag.evaluation_datasets(dataset_id),
    external_question_id text NOT NULL,
    topic text NOT NULL,
    question_text text NOT NULL,
    CONSTRAINT questions_external_unique UNIQUE (dataset_id,external_question_id),
    CONSTRAINT questions_dataset_pair UNIQUE (question_id,dataset_id),
    CONSTRAINT questions_required_text CHECK (
        btrim(external_question_id) <> '' AND btrim(topic) <> ''
        AND btrim(question_text) <> ''
    )
);

CREATE TABLE school_rag.gold_evidence (
    evidence_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id bigint NOT NULL REFERENCES school_rag.evaluation_questions(question_id),
    document_id bigint NOT NULL REFERENCES school_rag.documents(document_id),
    evidence_ordinal integer NOT NULL CHECK (evidence_ordinal > 0),
    pages integer[] NOT NULL,
    contains_any text[] NOT NULL,
    CONSTRAINT evidence_position_unique UNIQUE (question_id,evidence_ordinal),
    CONSTRAINT evidence_pages_valid CHECK (
        cardinality(pages) > 0 AND 0 < ALL(pages)
    ),
    CONSTRAINT evidence_fragments_valid CHECK (
        cardinality(contains_any) > 0
        AND array_position(contains_any, NULL) IS NULL
        AND array_position(contains_any, '') IS NULL
    )
);
-- Stránky jsou fyzické, číslované od 1; contains_any má OR sémantiku.

CREATE TABLE school_rag.indexing_runs (
    indexing_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collection_name text NOT NULL,
    embedding_model text,
    corpus_snapshot_sha256 char(64),
    status text NOT NULL DEFAULT 'running'
        CHECK (status IN ('running','completed','failed')),
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    chunk_count integer CHECK (chunk_count >= 0),
    notes text,
    CONSTRAINT indexing_collection_required CHECK (btrim(collection_name) <> ''),
    CONSTRAINT indexing_finish_valid CHECK (
        finished_at IS NULL OR finished_at >= started_at
    ),
    CONSTRAINT indexing_hash_valid CHECK (
        corpus_snapshot_sha256 IS NULL
        OR corpus_snapshot_sha256 ~ '^[0-9a-f]{64}$'
    )
);
-- Chunks a embeddingy zůstávají v ChromaDB; sem zapisujeme jen audit běhů.

CREATE TABLE school_rag.evaluation_runs (
    evaluation_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id bigint REFERENCES school_rag.evaluation_datasets(dataset_id),
    dataset_label text NOT NULL CHECK (dataset_label IN ('dev','random','test')),
    indexing_run_id bigint REFERENCES school_rag.indexing_runs(indexing_run_id),
    retriever text NOT NULL
        CHECK (retriever IN ('bm25','vector','legacy','hybrid_rrf')),
    run_date date NOT NULL,
    executed_at timestamptz,
    question_count integer NOT NULL CHECK (question_count > 0),
    retrieval_top_k integer CHECK (retrieval_top_k > 0),
    git_commit_sha char(40),
    git_dirty boolean,
    dataset_sha256 char(64),
    mrr numeric(8,6),
    hit_at_1 numeric(8,6),
    hit_at_3 numeric(8,6),
    hit_at_5 numeric(8,6),
    hit_at_8 numeric(8,6),
    latency_mean_ms numeric(12,3),
    latency_p50_ms numeric(12,3),
    latency_p95_ms numeric(12,3),
    record_kind text NOT NULL
        CHECK (record_kind IN ('documented_baseline','jsonl_run')),
    source_reference text NOT NULL,
    provenance_note text,
    CONSTRAINT runs_dataset_pair UNIQUE (evaluation_run_id,dataset_id),
    CONSTRAINT runs_dataset_name_fk FOREIGN KEY (dataset_id,dataset_label)
       REFERENCES school_rag.evaluation_datasets(dataset_id,dataset_name),
    CONSTRAINT runs_historical_dataset_guard CHECK (
        (record_kind='documented_baseline' AND dataset_id IS NULL)
        OR (record_kind='jsonl_run' AND dataset_id IS NOT NULL)
    ),
    CONSTRAINT runs_metrics_range CHECK (
        (mrr IS NULL OR mrr BETWEEN 0 AND 1)
        AND (hit_at_1 IS NULL OR hit_at_1 BETWEEN 0 AND 1)
        AND (hit_at_3 IS NULL OR hit_at_3 BETWEEN 0 AND 1)
        AND (hit_at_5 IS NULL OR hit_at_5 BETWEEN 0 AND 1)
        AND (hit_at_8 IS NULL OR hit_at_8 BETWEEN 0 AND 1)
    ),
    CONSTRAINT runs_latency_nonnegative CHECK (
        (latency_mean_ms IS NULL OR latency_mean_ms >= 0)
        AND (latency_p50_ms IS NULL OR latency_p50_ms >= 0)
        AND (latency_p95_ms IS NULL OR latency_p95_ms >= 0)
    ),
    CONSTRAINT runs_sha_valid CHECK (
        (git_commit_sha IS NULL OR git_commit_sha ~ '^[0-9a-f]{40}$')
        AND (dataset_sha256 IS NULL OR dataset_sha256 ~ '^[0-9a-f]{64}$')
    ),
    CONSTRAINT runs_provenance_required CHECK (btrim(source_reference) <> ''),
    CONSTRAINT runs_latency_order CHECK (
        latency_p95_ms IS NULL OR latency_p50_ms IS NULL
        OR latency_p95_ms >= latency_p50_ms
    )
);

CREATE TABLE school_rag.evaluation_results (
    result_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    evaluation_run_id bigint NOT NULL,
    dataset_id bigint NOT NULL,
    question_id bigint NOT NULL,
    first_evidence_rank integer CHECK (first_evidence_rank > 0),
    reciprocal_rank numeric(12,7) GENERATED ALWAYS AS (
        CASE WHEN first_evidence_rank IS NULL THEN 0::numeric
             ELSE round(1::numeric / first_evidence_rank, 7)
        END
    ) STORED,
    CONSTRAINT results_run_question_unique UNIQUE (evaluation_run_id,question_id),
    CONSTRAINT results_run_dataset_fk
        FOREIGN KEY (evaluation_run_id,dataset_id)
        REFERENCES school_rag.evaluation_runs(evaluation_run_id,dataset_id),
    CONSTRAINT results_question_dataset_fk
        FOREIGN KEY (question_id,dataset_id)
        REFERENCES school_rag.evaluation_questions(question_id,dataset_id)
);
-- Composite FKs brání omylu: výsledek musí patřit ke stejnému datasetu
-- jako konkrétní vyhodnocovací běh. dataset_id zde slouží k integritě.

CREATE INDEX idx_questions_dataset_topic
    ON school_rag.evaluation_questions(dataset_id,topic);
CREATE INDEX idx_gold_document ON school_rag.gold_evidence(document_id);
CREATE INDEX idx_runs_dataset_retriever_date
    ON school_rag.evaluation_runs(dataset_id,retriever,run_date DESC);
CREATE INDEX idx_runs_indexing ON school_rag.evaluation_runs(indexing_run_id);
CREATE INDEX idx_results_question ON school_rag.evaluation_results(question_id);
COMMIT;
