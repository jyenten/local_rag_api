-- Kontrola po seed_real.sql. Záměrně se kontrolují jen reálná importovaná data.
DO $$
DECLARE n_documents integer; n_datasets integer; n_questions integer;
        n_runs integer; n_gold integer;
BEGIN
    SELECT COUNT(*) INTO n_documents FROM school_rag.documents;
    SELECT COUNT(*) INTO n_datasets FROM school_rag.evaluation_datasets;
    SELECT COUNT(*) INTO n_questions FROM school_rag.evaluation_questions;
    SELECT COUNT(*) INTO n_runs FROM school_rag.evaluation_runs
      WHERE record_kind='documented_baseline';
    SELECT COUNT(*) INTO n_gold FROM school_rag.gold_evidence;
    IF n_documents < 3 OR n_datasets < 2 OR n_questions < 45
       OR n_runs < 4 OR n_gold < 50 THEN
        RAISE EXCEPTION
          'Seed mismatch: documents %, datasets %, questions %, runs %, evidence %',
          n_documents,n_datasets,n_questions,n_runs,n_gold;
    END IF;
    IF EXISTS (
        SELECT 1 FROM school_rag.evaluation_questions AS q
        LEFT JOIN school_rag.gold_evidence AS g ON g.question_id=q.question_id
        WHERE g.evidence_id IS NULL
    ) THEN RAISE EXCEPTION 'Some questions have no gold evidence'; END IF;
    RAISE NOTICE 'Verified real-data seed: docs %, datasets %, questions %, evidence %, baselines %',
                 n_documents,n_datasets,n_questions,n_gold,n_runs;
END $$;
