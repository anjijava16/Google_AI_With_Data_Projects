"""Deploy the orchestrator to Agent Runtime (formerly Agent Engine).

  python -m dia.deploy.deploy_agent_runtime --display-name "DIA Orchestrator"

What actually happens: your agent is pickled with cloudpickle, uploaded to the
staging bucket, and rebuilt inside a managed container. Two consequences worth
internalising before you debug for an hour:

  1. Anything not importable from `requirements` or `extra_packages` will fail
     at *deploy* time, not at build time.
  2. Module-level state that is not picklable (open clients, threads) breaks the
     upload. Build clients lazily inside functions — which is why every module
     in this repo imports its cloud client inside the function body.
"""
from __future__ import annotations

import argparse
import logging

import vertexai

from dia.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--display-name", default="DIA Orchestrator")
    parser.add_argument("--description", default="Document intelligence and analytics agent")
    parser.add_argument("--smoke-test", action="store_true", help="run locally, do not deploy")
    args = parser.parse_args()

    from vertexai import agent_engines

    from dia.agents.root_agent import root_agent

    app = agent_engines.AdkApp(agent=root_agent, enable_tracing=True)

    if args.smoke_test:
        import asyncio

        async def run():
            async for event in app.async_stream_query(
                user_id="smoke-test", message="What tables can you query?"
            ):
                print(event)

        asyncio.run(run())
        return

    if not settings.staging_bucket:
        raise SystemExit("STAGING_BUCKET must be set (gs://...)")

    client = vertexai.Client(project=settings.project_id, location=settings.location)
    remote_agent = client.agent_engines.create(
        agent=app,
        config={
            "display_name": args.display_name,
            "description": args.description,
            "staging_bucket": settings.staging_bucket,
            "requirements": "requirements-agent.txt",
            "extra_packages": ["src/dia"],
            "env_vars": {
                "GOOGLE_CLOUD_PROJECT": settings.project_id,
                "GOOGLE_CLOUD_LOCATION": settings.location,
                "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
                "RAG_CORPUS": settings.rag_corpus,
                "BQ_DATASET": settings.bq_dataset,
                "ORCHESTRATOR_MODEL": settings.orchestrator_model,
                "REASONING_MODEL": settings.reasoning_model,
            },
        },
    )

    resource_name = remote_agent.api_resource.name
    print("\nDeployed.\n")
    print(f"  resource: {resource_name}")
    print(
        "  console:  https://console.cloud.google.com/agent-platform/runtimes"
        f"/locations/{settings.location}/agent-runtimes?project={settings.project_id}\n"
    )


if __name__ == "__main__":
    main()
