-- Dynamické operace v informačním systému: provádět jen při reálné události.
-- Tento demonstrační blok se na konci vrátí zpět (ROLLBACK).
-- Nevydává vymyšlenou metriku za skutečné měření.
BEGIN;
INSERT INTO school_rag.indexing_runs
    (collection_name, embedding_model, status, notes)
VALUES ('ospf', 'all-MiniLM-L6-v2', 'running',
        'Příklad zahájení nového indexování – transakce bude vrácena.')
RETURNING indexing_run_id, status, started_at;
-- Skutečná aplikace může po dokončení aktualizovat daný běh na
-- status=completed, finished_at=now(), chunk_count=<změřený počet>.
ROLLBACK;

-- Skutečná nová evaluace se zapisuje až z originálního JSONL výsledku
-- (viz README); jednotlivé per-question výsledky se nevymýšlejí.
