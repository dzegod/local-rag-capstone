# Local Document Q&A Service

A RAG pipeline that answers questions about five internal company PDFs, running entirely on local
models through Ollama. Switching to a cloud model changes only environment variables read by `config.py`.

## Setup
1. Install Ollama (https://ollama.com/download) and pull the models:
   ```bash
   ollama pull qwen3.5:4b-q4_K_M
   ollama pull qwen3.5:2b-q4_K_M
   ollama pull nomic-embed-text
   ```
2. Raise the context window to 8192 (macOS): `launchctl setenv OLLAMA_CONTEXT_LENGTH 8192`, then restart Ollama.
3. Install dependencies: `uv sync`
4. Check: `uv run python test_api.py` prints one sentence and `stop`; `ollama ps` shows CONTEXT 8192.

## Run
| What | Command |
|------|---------|
| Rebuild `chroma_db/` | `uv run python ingest.py` -> `ingest_stats.json` |
| Benchmark models | `uv run python benchmark.py` -> `benchmark_results.json` |
| Ask one question | `uv run python pipeline.py "your question"` |
| Run all test questions | `uv run python pipeline.py` -> `pipeline_outputs.json` |
| Rate results by hand | `uv run python rate.py pipeline` / `uv run python rate.py benchmark` |

## Structure
| File | Purpose |
|------|---------|
| `config.py` | All settings: provider, models, chunking, top-K, prompt |
| `ingest.py` | Load PDFs, chunk, embed, store in ChromaDB |
| `retrieve.py` | Query the vector DB, return chunks with source, page and score |
| `generate.py` | Answer from retrieved chunks with the local LLM |
| `pipeline.py` | Retrieve + generate; runs the test set |
| `benchmark.py` | Model comparison (Exercise 1) |
| `test_questions.json` | Test set |
| `rate.py` | Interactive helper for entering hand ratings |
| `decision_log.md` | Decisions and reasoning |

## AI assistant
Claude Code (Claude Opus 5.5) helped write the code. The pipeline model is local (`qwen3.5:4b-q4_K_M` in Ollama). I wrote the decision log and all ratings by hand.

## Day 12: Evaluation
**Evaluated pipeline:** my own Day 11 pipeline (this folder), not the reference implementation.
Local model `qwen3.5:4b-q4_K_M` (thinking off), cloud model `gpt-5.6-luna`, judge `gpt-5.4-mini`, DeepEval 4.3.4.

Needs `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` in `.env` (never committed). Load it first:
`set -a; source .env; set +a; export JUDGE_BASE_URL="$AZURE_OPENAI_ENDPOINT"`

| What | Command | Output |
|------|---------|--------|
| Evaluate local outputs | `uv run python eval_pipeline.py local` | `eval_results_local.json` |
| Cloud test-set run (with the four cloud `LLM_*` variables set) | `uv run python pipeline.py --test-set pipeline_outputs_cloud.json` | `pipeline_outputs_cloud.json` |
| Evaluate cloud outputs | `uv run python eval_pipeline.py cloud` | `eval_results_cloud.json` |
| Local vs cloud comparison | `uv run python compare.py` | `compare_output.md` |
| Retrieval without a judge (Hit@5, MRR) | `uv run python retrieval_metrics.py test_questions.json pipeline_outputs_local.json` | `retrieval_metrics_local.txt` |
| Security probes | `uv run python security_probe.py local` / `cloud` | `security_results_local.json` / `_cloud.json` |

Changes to the given scripts: `security_probe.py` has two own attacks (`kb_poisoning`, `hidden_instruction`), a
per-attack injected chunk, and keeps hand-written verdicts on re-run. `retrieval_metrics.py` is snippet 07, changed to
score labels with several documents (`a.pdf; b.pdf`). `pipeline.py` gained `--test-set <file>`.

**AI assistant on Day 12:** Claude Code (Claude Opus 5.5) wrote `compare.py`, the script changes above, and ran the
evaluation scripts. For `security_results_cloud.json` it proposed verdicts that I reviewed and approved.
