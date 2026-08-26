"""Create a RAG Engine corpus and import documents.

This is the managed path — the equivalent of Bedrock Knowledge Bases. Google
runs the chunking, embedding and index for you. Use it when you want to be
productive on day one.

Use src/dia/tools/rag_tools.py::custom_retrieve instead when you need control
Google does not give you here (your own reranker, hybrid BM25 + vector, chunk
metadata you invented). That is the equivalent of the OpenSearch path.

Run:  python -m dia.ingestion.build_corpus --display-name contracts \
          --gcs-path 'gs://my-raw-bucket/contracts/*'
"""
from __future__ import annotations

import argparse
import logging

from dia.config import settings

log = logging.getLogger(__name__)


def _client():
    # The 2026 SDK surface. Older code you will find in blog posts uses
    # `vertexai.preview.rag` — same service, older import path.
    import agentplatform

    return agentplatform.Client(project=settings.project_id, location=settings.location)


def create_corpus(display_name: str, description: str = "") -> str:
    from agentplatform import types

    client = _client()
    corpus = client.rag.create_corpus(
        display_name=display_name,
        description=description,
        backend_config=types.RagVectorDbConfig(
            rag_embedding_model_config=types.RagEmbeddingModelConfig(
                vertex_prediction_endpoint=types.VertexPredictionEndpoint(
                    publisher_model=(
                        f"projects/{settings.project_id}/locations/{settings.location}"
                        f"/publishers/google/models/{settings.embedding_model}"
                    )
                )
            )
        ),
    )
    log.info("Created corpus %s", corpus.name)
    return corpus.name


def import_files(
    corpus_name: str,
    gcs_path: str,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
) -> None:
    from agentplatform import types

    client = _client()
    op = client.rag.import_files(
        corpus_name=corpus_name,
        paths=[gcs_path],
        transformation_config=types.TransformationConfig(
            chunking_config=types.ChunkingConfig(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        ),
    )
    log.info("Import started for %s -> %s", gcs_path, corpus_name)
    return op


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--gcs-path", required=True, help="e.g. gs://bucket/prefix/*")
    parser.add_argument("--corpus", help="reuse an existing corpus resource name")
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    args = parser.parse_args()

    corpus_name = args.corpus or create_corpus(args.display_name)
    import_files(corpus_name, args.gcs_path, args.chunk_size, args.chunk_overlap)

    print("\nCorpus ready. Export this and restart your agent:\n")
    print(f"  export RAG_CORPUS='{corpus_name}'\n")


if __name__ == "__main__":
    main()
