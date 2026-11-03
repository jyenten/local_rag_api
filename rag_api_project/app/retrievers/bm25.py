
import chromadb
from rank_bm25 import BM25Okapi

from app.config import Settings
from document_search.tokenize import tokenize


Metadata = dict[str, str | int | float | bool | None]
BATCH_SIZE = 500


class BM25Retriever:
    def __init__(self, settings: Settings):
        self.settings = settings

        client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
        )

        collection = client.get_collection(
            name=settings.collection_name,
        )

        count = collection.count()

        if count == 0:
            raise ValueError("Cannot index an empty Chroma collection.")

        records: list[tuple[str, str, Metadata, list[str]]] = []

        for offset in range(0, count, BATCH_SIZE):
            batch = collection.get(
                limit=min(BATCH_SIZE, count - offset),
                offset=offset,
                include=["documents", "metadatas"],
            )

            ids = batch["ids"]
            documents = batch["documents"]
            metadatas = batch["metadatas"]

            if (
                documents is None
                or metadatas is None
                or len(ids) != len(documents)
                or len(ids) != len(metadatas)
            ):
                raise RuntimeError("Incomplete Chroma batch.")

            for chunk_id, document, metadata in zip(
                ids,
                documents,
                metadatas,
                strict=True,
            ):
                if not isinstance(chunk_id, str) or not chunk_id.strip():
                    raise ValueError(f"Invalid chunk ID: {chunk_id!r}")

                if not isinstance(document, str):
                    raise ValueError(
                        f"Invalid document for chunk {chunk_id}"
                    )

                tokens = tokenize(document)
                if not tokens:
                    raise ValueError(
                        f"Invalid document for chunk {chunk_id}"
                    )

                if not isinstance(metadata, dict):
                    raise ValueError(
                        f"Invalid metadata for chunk {chunk_id}"
                    )

                source = metadata.get("source")
                page = metadata.get("page")

                if not isinstance(source, str) or not source.strip():
                    raise ValueError(
                        f"Invalid source for chunk {chunk_id}"
                    )

                if type(page) is not int or page < 1:
                    raise ValueError(
                        f"Invalid page for chunk {chunk_id}"
                    )

                records.append(
                    (chunk_id, document, dict(metadata), tokens)
                )

        records.sort(key=lambda record: record[0])

        if (
            len(records) != count
            or len({record[0] for record in records}) != count
        ):
            raise RuntimeError(
                "Chroma corpus count or IDs are inconsistent."
            )

        self.ids = tuple(record[0] for record in records)
        self.documents = tuple(record[1] for record in records)
        self.metadatas = tuple(record[2] for record in records)

        corpus = [
            record[3]
            for record in records
        ]

        self.token_sets = tuple(
            frozenset(tokens)
            for tokens in corpus
        )

        self.model = BM25Okapi(corpus)

    def search(
        self,
        question: str,
    ) -> tuple[list[str], list[float], list[Metadata]]:
        if not isinstance(question, str):
            raise ValueError("Question must be a string.")

        query_tokens = tokenize(question)

        if not query_tokens:
            raise ValueError(
                "Question must contain searchable tokens."
            )

        scores = self.model.get_scores(query_tokens)

        if len(scores) != len(self.documents):
            raise RuntimeError(
                "BM25 score count does not match the corpus."
            )

        query_terms = set(query_tokens)

        matching_indices = [
            index
            for index, tokens in enumerate(self.token_sets)
            if not query_terms.isdisjoint(tokens)
        ]

        ranked_indices = sorted(
            matching_indices,
            key=lambda index: (
                -float(scores[index]),
                self.ids[index],
            ),
        )

        top_indices = ranked_indices[
            :self.settings.retrieval_results
        ]

        top_documents = [
            self.documents[index]
            for index in top_indices
        ]

        top_scores = [
            float(scores[index])
            for index in top_indices
        ]

        top_metadatas = [
            dict(self.metadatas[index])
            for index in top_indices
        ]

        return top_documents, top_scores, top_metadatas
