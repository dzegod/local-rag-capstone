# Decision Log: Local RAG Pipeline

## Machine
- **Hardware:** Apple M5, 16 GB unified memory, macOS 26.5.1, native Ollama 0.40.16 (Metal GPU)
- **`ollama ps` with my main model loaded:**
```
NAME                 ID              SIZE      PROCESSOR    CONTEXT    RUNNER      UNTIL
qwen3.5:4b-q4_K_M    d8b0f5e9760c    3.3 GB    100% GPU     8192       llamacpp    4 minutes from now
```

## Model Selection
- **Chosen LLM:** `qwen3.5:4b-q4_K_M`, thinking off
- **Benchmark** (`benchmark_results.json`): 4B 36.3 tok/s, 2B 63.7 tok/s (mean, thinking off for both)
- **Thinking:** Disabled for this pipeline to keep answers fast and reserve the 1,024-token generation limit for the user-facing response. With thinking enabled, internal reasoning could use part of that limit, increasing latency and risking a truncated or empty answer. I did not compare thinking on vs. off, so this is a design rationale, not a measured result.
- **Why 4B:** It is slower than the 2B, but I expect better answers. 36 tok/s is still fast enough for short answers.
- **What I considered but rejected:** The 2B model was faster, but scored slightly lower in my six-task quality benchmark (4.3/5 vs. 4.5/5 for 4B), with weaker factual accuracy. I chose 4B because answer quality mattered more than the speed gain for this project. I did not include a 9B model or llama3.2:3b in the benchmark, so I have no results to compare; the benchmark focused on the two Qwen 3.5 sizes I tested.

## Embedding Model
- **Chosen:** `nomic-embed-text` (768 dimensions, `ingest_stats.json`)
- **Why:** It is small, runs locally in Ollama, and turns text into vectors so I can find the chunks closest in meaning to a question.

## Parsing
- **Extractor:** pypdf, default `extract_text()`
- **Tables looked like:** Messy. The rows and columns lost their layout, so numbers were separated from their labels.

## Chunking Strategy
- **Chunk size:** 512 characters, **overlap:** 50 characters → 335 chunks (`ingest_stats.json`)
- **Why:** Small chunks keep one idea each, and 5 of them fit easily in the context window. These are common default values; I did not tune them.

## Retrieval Configuration
- **Top-K:** 5
- **Context window:** 8192 (`ollama ps` above); prompt_tokens 593–840 (`pipeline_outputs.json`)
- **Why:** Top-K is set to 5 to provide several relevant chunks while keeping context focused. The pipeline run recorded 593–840 prompt tokens (about 675 on average) and up to 361 generated tokens. Against the 8192-token context window, the largest observed prompt-plus-completion total was 1,029 tokens, leaving about 7,163 tokens unused in that run. I did not compare other Top-K values, so 5 is a chosen setting, not a measured optimum.

## Observations
- **Passed:** 12 of 17 (`pipeline_outputs.json`)
- **What worked:** q16 and q17 (unanswerable) were correctly refused.
- **What failed:** q09 (Copilot budget breakdown) refused, though the answer is in `meeting_notes.pdf`. My guess why: it is a table, and the table text was messy or split across chunks.
- **Also failed:** q08 (says the CRM choice was not made yet; expected HubSpot Enterprise), q12 (gives the old 3-day policy, misses the 4-day update), q14 (gives one release date, misses the conflict), q15 (leads with the proposed EUR 39 instead of saying the price is undecided).
- **Traps I hit:** context was 4096 until I restarted Ollama; moving the folder broke the imports.
- **Local vs cloud expectations:** I expect the Day 12 cloud model may answer questions needing synthesis or detailed facts (especially q09) more completely, but this needs to be tested against the same questions. I do not yet know whether it will handle q15 better or respond faster; I will compare accuracy and latency using the same prompts. Unlike the local Ollama pipeline, a cloud model may send prompts and retrieved document context to an external provider, so it has a different privacy trade-off.

## If I Had More Time
- Use a better PDF parser for tables.
- Check which chunks were retrieved for the failed questions.
- Test the 2B model on the same 17 questions.