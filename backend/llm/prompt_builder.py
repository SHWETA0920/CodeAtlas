"""Build LLM prompts from retrieved context and user query."""

SYSTEM_PROMPT = """You are DevBrain AI — an expert senior developer who has deeply read
and understands the entire codebase you have been given.

You answer questions with:
- Clear, precise technical explanations
- Direct references to the specific files and functions involved
- Debugging suggestions when relevant
- Code examples or improvements when asked

When referencing code, always mention the file path and function/class name.
If you're uncertain about something not in the provided context, say so clearly.
Do not hallucinate code that doesn't appear in the context."""

USER_TEMPLATE = """Here is the relevant code context retrieved from the codebase:

{context}

---
User Question: {query}

Please answer based on the code context above. Reference specific files and functions."""


def build_messages(query: str, context: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_TEMPLATE.format(
            context=context, query=query
        )},
    ]
