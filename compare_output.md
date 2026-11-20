| Metric | n | Local mean ± 2SE | Cloud mean ± 2SE | Cloud − local (per question) ± 2SE | Verdict |
|---|---|---|---|---|---|
| Answer Relevancy | 17 | 0.98 ± 0.04 | 1.00 ± 0.00 | +0.02 ± 0.04 | no clear difference |
| Contextual Precision | 17 | 0.82 ± 0.14 | 0.80 ± 0.16 | -0.02 ± 0.14 | no clear difference |
| Contextual Recall | 17 | 0.82 ± 0.19 | 0.68 ± 0.23 | -0.15 ± 0.17 | no clear difference |
| Contextual Relevancy | 17 | 0.35 ± 0.12 | 0.38 ± 0.14 | +0.03 ± 0.07 | no clear difference |
| Faithfulness | 17 | 0.84 ± 0.09 | 0.86 ± 0.16 | +0.01 ± 0.14 | no clear difference |

| Run | Model | Median generation time (ms) | Slowest (ms, id) | Avg completion tokens | Empty or failed answers |
|---|---|---|---|---|---|
| local | qwen3.5:4b-q4_K_M | 2311 | 9974 (q07) | 99.6 | 0 |
| cloud | gpt-5.6-luna | 1296 | 2647 (q12) | 48.5 | 0 |

Completion tokens are `tokens_generated` (usage.completion_tokens; includes reasoning tokens where the provider reports them). Thinking was off in both runs.
