"""LLM response generation — supports OpenAI and Groq."""
from __future__ import annotations
from typing import Generator
from llm.prompt_builder import build_messages
from config import LLM_PROVIDER, OPENAI_API_KEY, GROQ_API_KEY, LLM_MODEL


def generate(query: str, context: str) -> str:
    """Non-streaming response."""
    messages = build_messages(query, context)

    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=LLM_MODEL or "llama3-70b-8192",
            messages=messages,
            max_tokens=2048,
            temperature=0.1,
        )
        return resp.choices[0].message.content

    else:  # openai
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=LLM_MODEL or "gpt-4o",
            messages=messages,
            max_tokens=2048,
            temperature=0.1,
        )
        return resp.choices[0].message.content


def generate_stream(query: str, context: str) -> Generator[str, None, None]:
    """Streaming response — yields text chunks."""
    messages = build_messages(query, context)

    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        stream = client.chat.completions.create(
            model=LLM_MODEL or "llama3-70b-8192",
            messages=messages,
            max_tokens=2048,
            temperature=0.1,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    else:  # openai
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        stream = client.chat.completions.create(
            model=LLM_MODEL or "gpt-4o",
            messages=messages,
            max_tokens=2048,
            temperature=0.1,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
