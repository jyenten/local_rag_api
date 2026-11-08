<a id="top"></a>

# Evaluation Curator Agent

[Česky](../cs/EVAL_CURATOR_AGENT.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Goal](#en-goal)
- [Allowed output](#en-allowed-output)
- [Existing datasets](#en-existing-datasets)
- [Source material](#en-source-material)
- [Candidate creation method](#en-candidate-creation-method)
- [Candidate schema](#en-candidate-schema)
- [Gold evidence rules](#en-gold-evidence-rules)
- [Topic diversity](#en-topic-diversity)
- [Prohibited behavior](#en-prohibited-behavior)
- [Batch size](#en-batch-size)
- [Validation](#en-validation)
- [Human approval boundary](#en-human-approval-boundary)

</details>

---

<a id="en"></a>

**Working directory:** Run commands from `rag_api_project/`. Dataset and PDF paths below are relative to that project directory.

<a id="en-goal"></a>

## Goal

Prepare high-quality candidate evaluation questions for the offline RAG retrieval evaluation dataset.

Target dataset structure:

- DEV: 20 questions
- RANDOM: 25 questions
- TEST: 15 questions

Total target: 60 questions.

The agent prepares candidates only.
The agent must never promote candidates into the real evaluation datasets.

---


<a id="en-allowed-output"></a>

## Allowed output

Write candidate questions only to:

eval/candidates/

Example:

eval/candidates/random_batch_001.json

Do not modify:

- eval/dev_questions.json
- eval/random_questions.json
- eval/test_questions.json
- app/
- document_search/
- evaluation/
- tests/

---


<a id="en-existing-datasets"></a>

## Existing datasets

Before generating candidates, inspect DEV/RANDOM for duplicate facts and topic coverage:

- eval/dev_questions.json
- eval/random_questions.json

Keep `eval/test_questions.json` held out. The validation script checks its IDs and normalized questions automatically, without requiring manual inspection of TEST contents during development. Ensure all three dataset files are present: the script skips missing files.

Avoid duplicate questions, duplicate facts, and unnecessarily repeated topics.

---


<a id="en-source-material"></a>

## Source material

Use only the PDF documents in:

data/

Gold evidence must come from the actual PDF text.

Use the existing document explorer for discovery:

```bash
python -m scripts.search_pdf "<query>" --top-k 10 --interactive
```

BM25 search is a discovery tool only.

A high BM25 score does not mean that a passage is correct gold evidence.

---


<a id="en-candidate-creation-method"></a>

## Candidate creation method

Always work in this direction:

evidence -> question

Never:

question -> search until something approximately matches

For every candidate:

1. Find a clear factual passage in a source PDF.
2. Record the physical PDF page number.
3. Create one question that is directly answered by that evidence.
4. Copy a stable exact evidence fragment into contains_any.
5. Keep the question narrow enough that the evidence fully answers it.
6. Avoid questions requiring several unrelated facts unless one evidence fragment supports all of them.

---


<a id="en-candidate-schema"></a>

## Candidate schema

Output must be a JSON array.

Each item must follow this structure:

```json
[
  {
    "id": "topic_random_001",
    "topic": "descriptive-topic",
    "question": "One clear question?",
    "gold_evidence": [
      {
        "source": "Exact_Source_Filename.pdf",
        "pages": [123],
        "contains_any": [
          "Exact supporting fragment from the source page"
        ]
      }
    ]
  }
]
```

---


<a id="en-gold-evidence-rules"></a>

## Gold evidence rules

Gold evidence must:

- use the exact PDF filename
- use physical PDF page numbers
- contain text actually present on the specified page
- directly answer the question
- use stable fragments rather than headers or navigation text

Do not use printed page numbers from inside the PDF.

Do not invent or paraphrase contains_any fragments.

Multiple GoldEvidence objects are allowed when several independently valid passages answer the same question.

contains_any has OR semantics.

Do not place two fragments into contains_any when both are required together to answer the question.

---


<a id="en-topic-diversity"></a>

## Topic diversity

Prefer coverage outside topics that are already overrepresented.

Avoid producing a batch dominated by one protocol or one PDF.

Useful areas may include, when supported by the corpus:

- IPv4 / IPv6 addressing
- DHCP / DHCPv6
- NAT
- routing fundamentals
- BGP
- EIGRP
- RIP
- OSPF
- route redistribution
- Neighbor Discovery
- routing security or validation mechanisms
- protocol-independent routing features

Topic diversity is secondary to evidence quality.

Never create a weak question just to improve topic balance.

---


<a id="en-prohibited-behavior"></a>

## Prohibited behavior

Do not:

- modify retrieval code
- modify evaluation metrics
- modify existing gold evidence
- run retrieval and rewrite gold merely to improve a metric
- copy an existing DEV or RANDOM question with different wording
- invent source text
- guess page numbers
- use external internet sources
- use knowledge not contained in the local PDFs as gold evidence
- promote candidates into a real dataset

---


<a id="en-batch-size"></a>

## Batch size

Generate exactly 5 candidates per batch unless instructed otherwise.

For RANDOM use IDs consistent with the existing dataset, for example:

```text
bgp_random_002
ipv6_random_002
routing_random_002
```

IDs must be unique across all evaluation datasets and the current candidate batch.

---


<a id="en-validation"></a>

## Validation

After writing the candidate JSON, run:

```bash
python -m scripts.validate_eval_candidates <candidate-file>
```

If validation fails:

1. diagnose the candidate
2. correct only the candidate file
3. rerun validation

Do not weaken the validator.

A batch is complete only when validation prints:

```text
VALID: 5 candidate(s)
```

---


<a id="en-human-approval-boundary"></a>

## Human approval boundary

After validation, stop.

Report:

- candidate file path
- the 5 candidate IDs
- topic of each candidate
- source PDF and page of each candidate
- validation result

Do not run promote_eval_candidates.

Promotion requires explicit human approval.

[↑ Back to top](#top)
