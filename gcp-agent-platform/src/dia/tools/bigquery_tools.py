"""BigQuery tools for the analytics agent.

Guardrails matter more than cleverness here. A text-to-SQL agent with an
unbounded BigQuery credential is a way to spend a lot of money very fast. Three
controls, all of which you want in production:

  1. read-only IAM on the service account (roles/bigquery.dataViewer)
  2. maximum_bytes_billed on every job — a hard stop, not a warning
  3. dry-run first so the agent can see the cost before committing
"""
from __future__ import annotations

import logging
import re

from google.cloud import bigquery

from dia.config import settings

log = logging.getLogger(__name__)

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def _client() -> bigquery.Client:
    return bigquery.Client(project=settings.project_id)


def list_tables() -> dict:
    """ADK tool: list tables available for analysis, with their schemas.

    Call this before writing any SQL so you use real column names.
    """
    client = _client()
    dataset_ref = f"{settings.project_id}.{settings.bq_dataset}"
    tables = {}
    try:
        for table_item in client.list_tables(dataset_ref):
            table = client.get_table(table_item.reference)
            tables[table.table_id] = [
                {"name": f.name, "type": f.field_type, "description": f.description}
                for f in table.schema
            ]
    except Exception as exc:
        log.exception("list_tables failed")
        return {"status": "error", "error": str(exc)}

    return {"status": "ok", "dataset": dataset_ref, "tables": tables}


def run_sql(sql: str) -> dict:
    """ADK tool: run a read-only BigQuery SELECT and return rows.

    Only SELECT statements are permitted. Always fully qualify tables as
    `project.dataset.table`. Prefer aggregates over raw row dumps.

    Args:
        sql: A BigQuery Standard SQL SELECT statement.
    """
    if _FORBIDDEN.search(sql):
        return {"status": "rejected", "error": "Only read-only SELECT queries are allowed."}
    if not sql.strip().lower().startswith(("select", "with")):
        return {"status": "rejected", "error": "Query must start with SELECT or WITH."}

    client = _client()

    # 1. dry run — cost check before we commit to anything
    try:
        dry = client.query(
            sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        )
        estimated = dry.total_bytes_processed or 0
    except Exception as exc:
        return {"status": "invalid_sql", "error": str(exc)}

    if estimated > settings.bq_max_bytes_billed:
        return {
            "status": "too_expensive",
            "estimated_bytes": estimated,
            "limit_bytes": settings.bq_max_bytes_billed,
            "error": "Query would scan more than the configured limit. Add filters "
                     "on partition columns or select fewer columns, then retry.",
        }

    # 2. real run, still capped at the server side
    try:
        job = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                maximum_bytes_billed=settings.bq_max_bytes_billed,
                use_query_cache=True,
            ),
        )
        rows = [dict(r) for r in job.result(max_results=200)]
    except Exception as exc:
        log.exception("query failed")
        return {"status": "error", "error": str(exc)}

    return {
        "status": "ok",
        "row_count": len(rows),
        "bytes_processed": job.total_bytes_processed,
        "rows": rows,
    }
