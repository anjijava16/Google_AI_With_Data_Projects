"""FastMCP server exposing the platform's tools over MCP.

Why bother when ADK can call the Python functions directly? Because MCP makes
the same tools reachable from Claude Desktop, Cursor, a LangGraph app, or
another team's agent without them importing your package. One implementation,
many consumers — the same reason you would put a capability behind an API
instead of a shared library.

Run local (stdio):   python -m dia.mcp_server.server
Run remote (HTTP):   MCP_TRANSPORT=http PORT=8081 python -m dia.mcp_server.server
"""
from __future__ import annotations

import logging
import os

from mcp.server.fastmcp import FastMCP

from dia.tools.bigquery_tools import list_tables as _list_tables
from dia.tools.bigquery_tools import run_sql as _run_sql
from dia.tools.rag_tools import custom_retrieve

logging.basicConfig(level=logging.INFO)
mcp = FastMCP("document-intelligence")


@mcp.tool()
def search_corpus(query: str, top_k: int = 10) -> dict:
    """Search the document corpus and return passages with source URIs."""
    chunks = custom_retrieve(query, top_k=top_k)
    return {
        "passages": [
            {"text": c.text, "source_uri": c.source_uri, "score": round(c.score, 4)}
            for c in chunks
        ]
    }


@mcp.tool()
def describe_tables() -> dict:
    """List BigQuery tables and their schemas."""
    return _list_tables()


@mcp.tool()
def query_bigquery(sql: str) -> dict:
    """Run a read-only BigQuery SELECT. Non-SELECT statements are rejected."""
    return _run_sql(sql)


@mcp.prompt()
def grounded_analysis(question: str) -> str:
    """Prompt template that forces citation discipline on any MCP client."""
    return f"""Answer this question using only the tools available to you.

Question: {question}

Procedure:
1. Call `search_corpus` for anything about document contents.
2. Call `describe_tables` then `query_bigquery` for anything quantitative.
3. Cite the source_uri for every claim drawn from a document.
4. If the tools do not support an answer, say so. Do not fill gaps from memory.
"""


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run()
    else:
        # streamable-http is what you want behind Cloud Run
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
