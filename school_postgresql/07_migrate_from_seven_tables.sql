-- In-place převod EXISTUJÍCÍ sedmitabulkové DB na osm tabulek; PostgreSQL 16+.
-- NEPOUŠTĚT na nové prázdné DB a NEPOUŠTĚT opakovaně.
-- Před spuštěním udělej zálohu. Celá změna je atomická (BEGIN/COMMIT).
-- Provede přejmenování tabulek, zachová všechna ID i FK a přenese všechny
-- nenulové hodnoty Hit@1/3/5/8, včetně případných skutečných JSONL běhů.
BEGIN;
SET LOCAL lock_timeout = '10s';

DO $preflight$
BEGIN
  IF current_database() NOT IN ('local_rag_school','school_migration_ci') THEN
    RAISE EXCEPTION 'Refusing migration outside local_rag_school (current: %)',
      current_database();
  END IF;
  IF to_regclass('school_rag.evaluation_runs') IS NULL
     OR to_regclass('school_rag.evaluation_results') IS NULL
     OR to_regclass('school_rag.evaluation_datasets') IS NULL
     OR to_regclass('school_rag.evaluation_questions') IS NULL THEN
    RAISE EXCEPTION 'Expected original seven-table schema not found; do not run twice';
  END IF;
  IF to_regclass('school_rag.eval_runs') IS NOT NULL
     OR to_regclass('school_rag.eval_hit_rates') IS NOT NULL THEN
    RAISE EXCEPTION 'Eight-table target already exists; refusing mixed migration';
  END IF;
END $preflight$;

-- Přejmenování zachová OID, data i existující vazby (FK).
ALTER TABLE school_rag.evaluation_datasets RENAME TO eval_datasets;
ALTER TABLE school_rag.evaluation_questions RENAME TO eval_questions;
ALTER TABLE school_rag.evaluation_runs RENAME TO eval_runs;
ALTER TABLE school_rag.evaluation_results RENAME TO eval_results;

CREATE TABLE school_rag.eval_hit_rates (
    evaluation_run_id bigint NOT NULL
        REFERENCES school_rag.eval_runs(evaluation_run_id) ON DELETE CASCADE,
    k integer NOT NULL CHECK (k > 0),
    hit_rate numeric(8,6) NOT NULL CHECK (hit_rate BETWEEN 0 AND 1),
    CONSTRAINT eval_hit_rates_pk PRIMARY KEY (evaluation_run_id,k)
);

INSERT INTO school_rag.eval_hit_rates(evaluation_run_id,k,hit_rate)
SELECT r.evaluation_run_id, h.k, h.hit_rate
FROM school_rag.eval_runs AS r
CROSS JOIN LATERAL (VALUES
  (1,r.hit_at_1), (3,r.hit_at_3), (5,r.hit_at_5), (8,r.hit_at_8)
) AS h(k,hit_rate)
WHERE h.hit_rate IS NOT NULL;

-- Klíčový ochranný krok: před smazáním sloupců kontrola úplnosti i hodnot.
DO $verify_copy$
DECLARE original_count bigint; copied_count bigint;
BEGIN
  SELECT COUNT(*) INTO original_count
  FROM school_rag.eval_runs AS r
  CROSS JOIN LATERAL (VALUES
    (r.hit_at_1),(r.hit_at_3),(r.hit_at_5),(r.hit_at_8)
  ) AS v(hit_rate)
  WHERE v.hit_rate IS NOT NULL;
  SELECT COUNT(*) INTO copied_count FROM school_rag.eval_hit_rates;
  IF original_count <> copied_count THEN
    RAISE EXCEPTION 'Hit@k row count mismatch: source %, target %',
      original_count,copied_count;
  END IF;
  IF EXISTS (
    SELECT 1 FROM school_rag.eval_runs AS r
    CROSS JOIN LATERAL (VALUES
      (1,r.hit_at_1), (3,r.hit_at_3), (5,r.hit_at_5), (8,r.hit_at_8)
    ) AS v(k,hit_rate)
    LEFT JOIN school_rag.eval_hit_rates AS h
      ON h.evaluation_run_id=r.evaluation_run_id AND h.k=v.k
    WHERE v.hit_rate IS NOT NULL
      AND (h.evaluation_run_id IS NULL OR h.hit_rate IS DISTINCT FROM v.hit_rate)
  ) THEN
    RAISE EXCEPTION 'Hit@k value mismatch; old columns preserved by transaction rollback';
  END IF;
  RAISE NOTICE 'Verified % Hit@k rows copied exactly',copied_count;
END $verify_copy$;

ALTER TABLE school_rag.eval_runs DROP CONSTRAINT runs_metrics_range;
ALTER TABLE school_rag.eval_runs
    DROP COLUMN hit_at_1,
    DROP COLUMN hit_at_3,
    DROP COLUMN hit_at_5,
    DROP COLUMN hit_at_8;
ALTER TABLE school_rag.eval_runs ADD CONSTRAINT runs_metrics_range
    CHECK (mrr IS NULL OR mrr BETWEEN 0 AND 1);
COMMIT;
