"""RAG evaluation harness.

Retrieval metrics are computed deterministically — no model, no cost, no
flakiness. Only faithfulness and answer relevance need a judge, and those run
on a cheaper model than the system under test.

The rule worth keeping: if retrieval recall is bad, no prompt engineering will
save the answer. Measure the stages separately or you will spend a week tuning
the wrong one.

  python evals/rag_eval.py --dataset evals/datasets/rag_eval.jsonl
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@dataclass
class Case:
    question: str
    expected_answer: str
    expected_sources: list[str] = field(default_factory=list)


@dataclass
class Result:
    question: str
    precision_at_k: float
    recall_at_k: float
    mrr: float
    faithfulness: float | None = None
    answer_relevance: float | None = None
    latency_ms: float = 0.0


def load_dataset(path: Path) -> list[Case]:
    cases = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        raw = json.loads(line)
        cases.append(
            Case(
                question=raw["question"],
                expected_answer=raw.get("expected_answer", ""),
                expected_sources=raw.get("expected_sources", []),
            )
        )
    return cases


def retrieval_metrics(retrieved: list[str], expected: list[str]) -> tuple[float, float, float]:
    """Precision@k, recall@k, and reciprocal rank of the first hit.

    Negative cases (expected_sources == []) are the "should not be answerable"
    probes. Keep them in the set — an index that confidently retrieves something
    for every question is worse than one that returns nothing. For those cases
    recall is vacuously 1.0 and precision rewards retrieving nothing.
    """
    if not expected:
        return (1.0 if not retrieved else 0.0), 1.0, 0.0
    expected_set = set(expected)
    hits = [uri for uri in retrieved if uri in expected_set]

    precision = len(set(hits)) / len(retrieved) if retrieved else 0.0
    recall = len(set(hits)) / len(expected_set)

    mrr = 0.0
    for rank, uri in enumerate(retrieved, start=1):
        if uri in expected_set:
            mrr = 1.0 / rank
            break
    return precision, recall, mrr


JUDGE_PROMPT = """You are grading a retrieval-augmented answer.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

ANSWER GIVEN:
{answer}

Score two things from 0.0 to 1.0:
- faithfulness: is every claim in the answer supported by the context? An answer
  that adds unsupported detail scores low even if the detail is true.
- answer_relevance: does it actually answer the question asked?

Reply with JSON only: {{"faithfulness": 0.0, "answer_relevance": 0.0, "notes": ""}}"""


def judge(question: str, context: str, answer: str, model: str) -> dict:
    from google import genai

    from dia.config import settings

    client = genai.Client(**settings.genai_kwargs)
    response = client.models.generate_content(
        model=model,
        contents=JUDGE_PROMPT.format(question=question, context=context[:20000], answer=answer),
    )
    text = (response.text or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"faithfulness": None, "answer_relevance": None, "notes": "unparseable judge output"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("evals/datasets/rag_eval.jsonl"))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--judge-model", default="gemini-3.5-flash")
    parser.add_argument("--skip-judge", action="store_true", help="retrieval metrics only, no cost")
    parser.add_argument("--fail-under", type=float, default=0.0, help="exit 1 if mean recall below")
    args = parser.parse_args()

    import time

    from dia.tools.rag_tools import custom_retrieve

    cases = load_dataset(args.dataset)
    results: list[Result] = []

    for case in cases:
        started = time.perf_counter()
        chunks = custom_retrieve(case.question, top_k=args.top_k)
        latency = (time.perf_counter() - started) * 1000

        retrieved_uris = [c.source_uri for c in chunks]
        precision, recall, mrr = retrieval_metrics(retrieved_uris, case.expected_sources)
        result = Result(case.question, precision, recall, mrr, latency_ms=latency)

        if not args.skip_judge and case.expected_answer:
            context = "\n\n---\n\n".join(c.text for c in chunks)
            scores = judge(case.question, context, case.expected_answer, args.judge_model)
            result.faithfulness = scores.get("faithfulness")
            result.answer_relevance = scores.get("answer_relevance")

        results.append(result)
        print(
            f"  {case.question[:58]:60s} P={precision:.2f} R={recall:.2f} "
            f"MRR={mrr:.2f} {latency:.0f}ms"
        )

    def mean(key: str) -> float:
        values = [getattr(r, key) for r in results if getattr(r, key) is not None]
        return statistics.mean(values) if values else 0.0

    print("\n" + "=" * 68)
    print(f"  cases              {len(results)}")
    print(f"  precision@{args.top_k:<8} {mean('precision_at_k'):.3f}")
    print(f"  recall@{args.top_k:<11} {mean('recall_at_k'):.3f}")
    print(f"  MRR                {mean('mrr'):.3f}")
    if not args.skip_judge:
        print(f"  faithfulness       {mean('faithfulness'):.3f}")
        print(f"  answer relevance   {mean('answer_relevance'):.3f}")
    print(f"  p50 latency        {statistics.median(r.latency_ms for r in results):.0f}ms")
    print("=" * 68)

    if args.fail_under and mean("recall_at_k") < args.fail_under:
        print(f"\nFAIL: recall below threshold {args.fail_under}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
