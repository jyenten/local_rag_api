-- Analytické SQL: skutečné záznamy DEV/RANDOM + zdokumentovaná historie.
-- Spouštějte až po 01_schema.sql a 02_seed_real.sql.

-- Q1 Počty otázek a gold evidence podle datasetu.
SELECT d.dataset_name, COUNT(DISTINCT q.question_id) AS questions,
       COUNT(g.evidence_id) AS evidence_records
FROM school_rag.evaluation_datasets AS d
LEFT JOIN school_rag.evaluation_questions AS q ON q.dataset_id = d.dataset_id
LEFT JOIN school_rag.gold_evidence AS g ON g.question_id = q.question_id
GROUP BY d.dataset_id, d.dataset_name
ORDER BY d.dataset_name;

-- Q2 Dokumenty nejčastěji používané jako očekávaný důkaz.
SELECT doc.source_filename, COUNT(*) AS evidence_count,
       COUNT(DISTINCT g.question_id) AS supported_questions
FROM school_rag.documents AS doc
JOIN school_rag.gold_evidence AS g ON g.document_id = doc.document_id
GROUP BY doc.document_id, doc.source_filename
ORDER BY evidence_count DESC;

-- Q3 Zásadní školní JOIN: téma -> otázka -> dokument -> stránky.
SELECT d.dataset_name, q.external_question_id, q.topic,
       doc.source_filename, g.pages
FROM school_rag.evaluation_datasets AS d
JOIN school_rag.evaluation_questions AS q ON q.dataset_id = d.dataset_id
JOIN school_rag.gold_evidence AS g ON g.question_id = q.question_id
JOIN school_rag.documents AS doc ON doc.document_id = g.document_id
WHERE q.topic LIKE 'ospf%'
ORDER BY d.dataset_name, q.external_question_id, g.evidence_ordinal;

-- Q4 Rozbalení skutečných fyzických stran PDF.
SELECT doc.source_filename, p.page_number, COUNT(*) AS evidence_occurrences
FROM school_rag.gold_evidence AS g
JOIN school_rag.documents AS doc ON doc.document_id = g.document_id
CROSS JOIN LATERAL unnest(g.pages) AS p(page_number)
GROUP BY doc.source_filename, p.page_number
ORDER BY evidence_occurrences DESC, doc.source_filename, p.page_number;

-- Q5 Zdokumentované historické srovnání, NIKOLI nově změřené.
SELECT d.dataset_name, r.retriever, r.run_date, r.mrr,
       r.hit_at_1, r.hit_at_3, r.hit_at_5, r.hit_at_8,
       r.record_kind
FROM school_rag.evaluation_runs AS r
JOIN school_rag.evaluation_datasets AS d ON d.dataset_id = r.dataset_id
WHERE r.record_kind = 'documented_baseline'
ORDER BY d.dataset_name, r.retriever;

-- Q6 Porovnání pouze běhů se stejným datasetem a se známým indexem.
SELECT d.dataset_name, r.indexing_run_id,
       MAX(r.mrr) FILTER (WHERE r.retriever='bm25') AS bm25_mrr,
       MAX(r.mrr) FILTER (WHERE r.retriever='vector') AS vector_mrr
FROM school_rag.evaluation_runs AS r
JOIN school_rag.evaluation_datasets AS d ON d.dataset_id = r.dataset_id
WHERE r.record_kind='jsonl_run' AND r.indexing_run_id IS NOT NULL
GROUP BY d.dataset_name, r.dataset_id, r.indexing_run_id
HAVING COUNT(DISTINCT r.retriever) FILTER
       (WHERE r.retriever IN ('bm25','vector')) = 2;

-- Q7 Nejproblematičtější testovací témata (až budou skutečné per-question runs).
SELECT q.topic, r.retriever, COUNT(*) AS evaluated,
       AVG(res.reciprocal_rank) AS mean_rr,
       COUNT(*) FILTER (WHERE res.first_evidence_rank IS NULL) AS no_match
FROM school_rag.evaluation_results AS res
JOIN school_rag.evaluation_questions AS q ON q.question_id = res.question_id
JOIN school_rag.evaluation_runs AS r ON r.evaluation_run_id = res.evaluation_run_id
GROUP BY q.topic,r.retriever
ORDER BY mean_rr ASC, evaluated DESC;

-- Q8 Kontrola úplnosti záznamu skutečně importovaných běhů.
SELECT r.evaluation_run_id, r.retriever, r.question_count,
       COUNT(res.result_id) AS stored_results
FROM school_rag.evaluation_runs AS r
LEFT JOIN school_rag.evaluation_results AS res
    ON res.evaluation_run_id = r.evaluation_run_id
WHERE r.record_kind='jsonl_run'
GROUP BY r.evaluation_run_id
HAVING COUNT(res.result_id) <> r.question_count;
