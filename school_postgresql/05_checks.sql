-- Kontrola po seed_real.sql. Záměrně se kontrolují jen reálná importovaná data.
DO $$
DECLARE n_documents integer; n_datasets integer; n_questions integer;
        n_runs integer; n_gold integer; n_hits integer;
BEGIN
    SELECT COUNT(*) INTO n_documents FROM school_rag.documents;
    SELECT COUNT(*) INTO n_datasets FROM school_rag.eval_datasets;
    SELECT COUNT(*) INTO n_questions FROM school_rag.eval_questions;
    SELECT COUNT(*) INTO n_runs FROM school_rag.eval_runs
      WHERE record_kind='documented_baseline';
    SELECT COUNT(*) INTO n_gold FROM school_rag.gold_evidence;
    SELECT COUNT(*) INTO n_hits FROM school_rag.eval_hit_rates AS h
      JOIN school_rag.eval_runs AS r ON r.evaluation_run_id=h.evaluation_run_id
      WHERE r.record_kind='documented_baseline';
    IF n_documents < 3 OR n_datasets < 2 OR n_questions < 45
       OR n_runs < 4 OR n_gold < 62 OR n_hits < 16 THEN
        RAISE EXCEPTION
          'Seed mismatch: documents %, datasets %, questions %, runs %, evidence %, hits %',
          n_documents,n_datasets,n_questions,n_runs,n_gold,n_hits;
    END IF;
    IF EXISTS (
        SELECT 1 FROM school_rag.eval_questions AS q
        LEFT JOIN school_rag.gold_evidence AS g ON g.question_id=q.question_id
        WHERE g.evidence_id IS NULL
    ) THEN RAISE EXCEPTION 'Some questions have no gold evidence'; END IF;
    IF EXISTS (
        SELECT r.evaluation_run_id FROM school_rag.eval_runs AS r
        LEFT JOIN school_rag.eval_hit_rates AS h
          ON h.evaluation_run_id=r.evaluation_run_id
        WHERE r.record_kind='documented_baseline'
        GROUP BY r.evaluation_run_id
        HAVING COUNT(h.k)<>4 OR COUNT(DISTINCT h.k)<>4
    ) THEN RAISE EXCEPTION 'Baseline must have four distinct Hit@k values'; END IF;
    RAISE NOTICE 'Verified seed: docs %, datasets %, questions %, evidence %, baselines %, Hit@k rows %',
                 n_documents,n_datasets,n_questions,n_gold,n_runs,n_hits;
END $$;
