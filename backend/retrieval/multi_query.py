"""
Multi-Query Retrieval: expand a single user query into N alternative
phrasings to improve recall across varied terminology in code.
"""
from __future__ import annotations
from config import LLM_PROVIDER, OPENAI_API_KEY, GROQ_API_KEY, MULTI_QUERY_COUNT

SYSTEM_PROMPT = """You are a senior developer helping search a codebase.
Given a user query about code, generate {n} alternative search queries
that cover different phrasings, synonyms, and related concepts.
Return ONLY the queries, one per line, no numbering, no extra text."""


def expand_query(query: str) -> list[str]:
    """Return original query + N alternatives."""
    alternatives = _generate_alternatives(query)
    # Deduplicate while preserving order; original always first
    seen = {query.lower()}
    result = [query]
    for q in alternatives:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            result.append(q)
    return result


def _generate_alternatives(query: str) -> list[str]:
    prompt = f"User query: {query}\n\nGenerate {MULTI_QUERY_COUNT} alternative queries:"

    try:
        if LLM_PROVIDER == "groq":
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            resp = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system",
                     "content": SYSTEM_PROMPT.format(n=MULTI_QUERY_COUNT)},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.3,
            )
            text = resp.choices[0].message.content
        else:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": SYSTEM_PROMPT.format(n=MULTI_QUERY_COUNT)},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.3,
            )
            text = resp.choices[0].message.content

        return [line.strip() for line in text.splitlines() if line.strip()]

    except Exception:
        # Fallback: simple keyword expansion
        words = query.lower().split()
        fallbacks = []
        if len(words) > 1:
            fallbacks.append(" ".join(reversed(words)))
            fallbacks.append(f"where is {query} implemented")
            fallbacks.append(f"{query} function definition")
        return fallbacks
