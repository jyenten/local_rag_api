-- Ověřovací skript po 07_migrate_from_seven_tables.sql (nebo novém seedu).
DO $check_upgrade$
DECLARE table_count integer; n_baselines integer; n_hits integer;
BEGIN
  SELECT COUNT(*) INTO table_count FROM information_schema.tables
    WHERE table_schema='school_rag' AND table_type='BASE TABLE';
  IF table_count<>8 THEN RAISE EXCEPTION 'Expected 8 tables, got %',table_count; END IF;
  IF to_regclass('school_rag.evaluation_runs') IS NOT NULL
     OR to_regclass('school_rag.eval_hit_rates') IS NULL THEN
    RAISE EXCEPTION 'Old table still exists or normalized metrics missing';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='school_rag' AND table_name='eval_runs'
      AND column_name IN ('hit_at_1','hit_at_3','hit_at_5','hit_at_8')
  ) THEN RAISE EXCEPTION 'Legacy Hit@k columns still present'; END IF;
  SELECT COUNT(*) INTO n_baselines FROM school_rag.eval_runs
    WHERE record_kind='documented_baseline';
  SELECT COUNT(*) INTO n_hits
    FROM school_rag.eval_hit_rates AS h
    JOIN school_rag.eval_runs AS r
      ON r.evaluation_run_id=h.evaluation_run_id
    WHERE r.record_kind='documented_baseline';
  IF n_baselines<4 OR n_hits<16 THEN
    RAISE EXCEPTION 'Expected four original baselines and 16 Hit@k metrics, got % and %',
      n_baselines,n_hits;
  END IF;
  IF EXISTS (
    SELECT r.evaluation_run_id FROM school_rag.eval_runs AS r
    LEFT JOIN school_rag.eval_hit_rates AS h
      ON h.evaluation_run_id=r.evaluation_run_id
    WHERE r.record_kind='documented_baseline'
    GROUP BY r.evaluation_run_id
    HAVING COUNT(h.k)<>4
  ) THEN RAISE EXCEPTION 'A historical baseline has incomplete Hit@k'; END IF;
  RAISE NOTICE 'PASS: % tables, % baselines, % historical Hit@k rows',
     table_count,n_baselines,n_hits;
END $check_upgrade$;
