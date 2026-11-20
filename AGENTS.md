# AGENTS.md

## Rules (from capstone_brief.md)
- Local models only. The pipeline LLM runs in local Ollama. Never use a model tag with `cloud` in it.
- Numbers come from files. Every figure in README.md or decision_log.md must come from
  `benchmark_results.json` or `pipeline_outputs.json`, written by code. The assistant may write the
  script that measures, never the number.
- Every chat call sets `reasoning_effort` and passes the token cap under `config.TOKEN_LIMIT_PARAM`.
- `quality_rating`, `passed` and `rating_note` are filled in by hand.
- `decision_log.md` is written by hand.
- Keep `.env` away from the assistant.
- One step at a time (ingest, retrieve, generate, benchmark); commit after each working step.

## How to run
| Step | Command |
|------|---------|
| Smoke test | `uv run python test_api.py` |
| Benchmark | `uv run python benchmark.py` |
| Rebuild vector DB | `uv run python ingest.py` |
| One question | `uv run python pipeline.py "question"` |
| All test questions | `uv run python pipeline.py` |

## Checks
- `ollama ps` shows CONTEXT 8192.
- No `WARNING: empty answer` lines; `finish_reason` is `stop`.
- Chunk count stays the same when `ingest.py` is run twice.
- Relevance scores are between 0 and 1.
