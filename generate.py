import time

from openai import OpenAI

import config

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{c['source']}, page {c['page']}]\n{c['content']}" for c in chunks)


def generate_answer(query: str, chunks: list[dict]) -> dict:
    context = build_context(chunks)
    start = time.time()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ],
        temperature=config.TEMPERATURE,
        reasoning_effort=config.REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
    )
    elapsed_ms = round((time.time() - start) * 1000)
    choice = response.choices[0]
    usage = response.usage
    answer = choice.message.content or ""

    if not answer.strip():
        print(f"WARNING: empty answer for {query!r} (finish_reason={choice.finish_reason})")

    return {
        "query": query,
        "answer": answer,
        "context_used": context,
        "model": config.LLM_MODEL,
        "thinking": config.REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "generation_time_ms": elapsed_ms,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "tokens_generated": usage.completion_tokens if usage else None,
    }
