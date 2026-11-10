-- Testujeme na SKUTEČNÉ PostgreSQL 16 databázi po 01_schema + 02_seed_real.
-- Testovací záznamy se nikdy neukládají: všechny úspěšné operace skončí ROLLBACK.
-- Chybové stavy odchytávají samostatné bloky; neočekávaný úspěch testu = chyba.
BEGIN;
DO $school_test$
DECLARE
  d_id bigint;
  q_id bigint;
  wrong_q bigint;
  doc_id bigint;
  idx_id bigint;
  run_id bigint;
  actual_rr numeric;
  actual_status text;
BEGIN
  SELECT dataset_id INTO STRICT d_id
    FROM school_rag.evaluation_datasets WHERE dataset_name='dev';
  SELECT question_id INTO STRICT q_id
    FROM school_rag.evaluation_questions WHERE dataset_id=d_id LIMIT 1;
  SELECT question_id INTO STRICT wrong_q
    FROM school_rag.evaluation_questions
   WHERE dataset_id<>d_id LIMIT 1;
  SELECT document_id INTO STRICT doc_id FROM school_rag.documents LIMIT 1;

  -- UNIQUE na dokument.
  BEGIN
    INSERT INTO school_rag.documents(source_filename)
    SELECT source_filename FROM school_rag.documents WHERE document_id=doc_id;
    RAISE EXCEPTION 'FAIL: duplicita dokumentu byla povolena';
  EXCEPTION WHEN unique_violation THEN NULL;
  END;

  -- CHECK na negativní stranu.
  BEGIN
    INSERT INTO school_rag.gold_evidence
      (question_id,document_id,evidence_ordinal,pages,contains_any)
    VALUES (q_id,doc_id,1001,ARRAY[0],ARRAY['real fragment']);
    RAISE EXCEPTION 'FAIL: negativni strana prosla';
  EXCEPTION WHEN check_violation THEN NULL;
  END;

  -- CHECK prázdného fragmentu důkazu.
  BEGIN
    INSERT INTO school_rag.gold_evidence
      (question_id,document_id,evidence_ordinal,pages,contains_any)
    VALUES (q_id,doc_id,1002,ARRAY[1],ARRAY['']);
    RAISE EXCEPTION 'FAIL: prazdny fragment prosel';
  EXCEPTION WHEN check_violation THEN NULL;
  END;

  -- FK: odkaz na neexistující dokument.
  BEGIN
    INSERT INTO school_rag.gold_evidence
      (question_id,document_id,evidence_ordinal,pages,contains_any)
    VALUES (q_id,-1000,1003,ARRAY[1],ARRAY['test']);
    RAISE EXCEPTION 'FAIL: neexistujici dokument prosel';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;

  -- Skutečný dynamický INSERT + UPDATE pro indexovací běh;
  -- v rámci testu se nic trvale neukládá.
  INSERT INTO school_rag.indexing_runs
    (collection_name, embedding_model, status)
  VALUES ('ci-test', 'test-model', 'running')
  RETURNING indexing_run_id INTO idx_id;

  UPDATE school_rag.indexing_runs
     SET status='completed', finished_at=now(), chunk_count=0
   WHERE indexing_run_id=idx_id;
  SELECT status INTO STRICT actual_status
    FROM school_rag.indexing_runs WHERE indexing_run_id=idx_id;
  IF actual_status<>'completed' THEN
    RAISE EXCEPTION 'FAIL: stav indexovaciho behu nebyl aktualizovan';
  END IF;

  -- Konzistence dataset_id / dataset_label (DEV nesmí tvrdit RANDOM).
  BEGIN
    INSERT INTO school_rag.evaluation_runs
     (dataset_id,dataset_label,retriever,run_date,question_count,
      record_kind,source_reference)
    VALUES (d_id,'random','bm25',current_date,1,'jsonl_run','CI test');
    RAISE EXCEPTION 'FAIL: nesoulad datasetu prosel';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;

  -- Testovací běh s jednou otázkou - VŽDY ROLLBACK (není měření).
  INSERT INTO school_rag.evaluation_runs
    (dataset_id,dataset_label,indexing_run_id,retriever,run_date,
     question_count,record_kind,source_reference)
  VALUES (d_id,'dev',idx_id,'bm25',current_date,1,
          'jsonl_run','CI synthetic test, rolled back')
  RETURNING evaluation_run_id INTO run_id;

  INSERT INTO school_rag.evaluation_results
    (evaluation_run_id,dataset_id,question_id,first_evidence_rank)
  VALUES (run_id,d_id,q_id,2);

  SELECT reciprocal_rank INTO STRICT actual_rr
    FROM school_rag.evaluation_results WHERE evaluation_run_id=run_id;
  IF actual_rr<>0.5 THEN
    RAISE EXCEPTION 'FAIL: reciprocal rank %, expected 0.5',actual_rr;
  END IF;

  -- FK: výsledková otázka z cizího datasetu.
  BEGIN
    INSERT INTO school_rag.evaluation_results
      (evaluation_run_id,dataset_id,question_id,first_evidence_rank)
    VALUES (run_id,d_id,wrong_q,1);
    RAISE EXCEPTION 'FAIL: otazka z jineho datasetu prosla';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;

  RAISE NOTICE 'PASS: UNIQUE, CHECK, FK, dataset integrity, insert/update, reciprocal_rank';
END
$school_test$;
ROLLBACK;
