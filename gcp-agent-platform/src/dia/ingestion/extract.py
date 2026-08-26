"""Document text extraction with a pluggable backend.

Two backends, deliberately:
  - docling   : runs anywhere, no cloud dependency, good tables/layout
  - docai     : Google Document AI, managed, OCR for scans, per-page billing

This is the GCP mirror of the AWS Textract decision. Keep both behind one
interface so the eval harness can benchmark them on YOUR documents instead of
you trusting a vendor benchmark.
"""
from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Literal, Protocol

from google.cloud import storage

log = logging.getLogger(__name__)

Backend = Literal["docling", "docai"]


@dataclass
class ExtractedDoc:
    uri: str
    text: str
    page_count: int
    backend: str
    mean_ocr_confidence: float | None = None


class Extractor(Protocol):
    def extract(self, uri: str) -> ExtractedDoc: ...


def _read_gcs(uri: str) -> bytes:
    if not uri.startswith("gs://"):
        raise ValueError(f"Expected a gs:// URI, got {uri}")
    bucket_name, _, blob_name = uri[len("gs://"):].partition("/")
    client = storage.Client()
    return client.bucket(bucket_name).blob(blob_name).download_as_bytes()


class DoclingExtractor:
    """Local/in-container extraction. No per-page cost, but you pay in CPU
    and cold-start time — size your Cloud Run instance accordingly."""

    def __init__(self) -> None:
        from docling.document_converter import DocumentConverter  # lazy: heavy import

        self._converter = DocumentConverter()

    def extract(self, uri: str) -> ExtractedDoc:
        from docling.datamodel.base_models import DocumentStream

        payload = _read_gcs(uri)
        source = DocumentStream(name=uri.rsplit("/", 1)[-1], stream=io.BytesIO(payload))
        result = self._converter.convert(source)
        doc = result.document
        return ExtractedDoc(
            uri=uri,
            text=doc.export_to_markdown(),
            page_count=len(getattr(doc, "pages", []) or []) or 1,
            backend="docling",
        )


class DocAIExtractor:
    """Google Document AI. Closest analogue to AWS Textract.

    Note the difference that bites people: Textract you call with a plain API
    name; Document AI requires you to have *created a processor* first and to
    address it by full resource path, in the processor's own region.
    """

    def __init__(self, processor_path: str) -> None:
        from google.api_core.client_options import ClientOptions
        from google.cloud import documentai

        # Region is embedded in the processor path: projects/P/locations/L/processors/ID
        region = processor_path.split("/locations/")[1].split("/")[0]
        self._documentai = documentai
        self._client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{region}-documentai.googleapis.com")
        )
        self._path = processor_path

    def extract(self, uri: str, mime_type: str = "application/pdf") -> ExtractedDoc:
        payload = _read_gcs(uri)
        request = self._documentai.ProcessRequest(
            name=self._path,
            raw_document=self._documentai.RawDocument(content=payload, mime_type=mime_type),
        )
        doc = self._client.process_document(request=request).document

        confidences = [
            block.layout.confidence
            for page in doc.pages
            for block in page.blocks
            if block.layout.confidence
        ]
        return ExtractedDoc(
            uri=uri,
            text=doc.text,
            page_count=len(doc.pages),
            backend="docai",
            mean_ocr_confidence=sum(confidences) / len(confidences) if confidences else None,
        )


def get_extractor(backend: Backend, processor_path: str | None = None) -> Extractor:
    if backend == "docling":
        return DoclingExtractor()
    if backend == "docai":
        if not processor_path:
            raise ValueError("docai backend requires processor_path")
        return DocAIExtractor(processor_path)
    raise ValueError(f"Unknown backend: {backend}")
