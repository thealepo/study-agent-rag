from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import types

from .prompts import SYSTEM_PROMPT
from .rag import retrieve


DEFAULT_MODEL = "gemini-3.1-flash-lite"


def create_client(
    api_key: str | None = None,
) -> genai.Client:
    """Create a Gemini client."""

    key = api_key or os.getenv("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your key."
        )

    return genai.Client(
        api_key=key
    )


def _history_to_contents(
    history: list[dict[str, Any]],
) -> list[types.Content]:

    contents: list[types.Content] = []

    for message in history or []:

        role = message.get("role")
        content = message.get("content")

        if (
            role not in {"user", "assistant"}
            or not isinstance(content, str)
        ):
            continue

        gemini_role = (
            "model"
            if role == "assistant"
            else "user"
        )

        contents.append(
            types.Content(
                role=gemini_role,
                parts=[
                    types.Part.from_text(
                        text=content
                    )
                ],
            )
        )

    return contents


def study_agent(
    query: str,
    history: list[dict[str, Any]],
    knowledge_base: dict[str, Any],
    embedding_model: Any,
    client: genai.Client,
    model_name: str = DEFAULT_MODEL,
) -> str:
    """
    Answer one conversational turn
    with access to the uploaded notes.
    """

    def search_notes(query: str) -> str:
        """
        Search the uploaded class notes
        for information relevant to a query.
        """

        relevant_chunks = retrieve(
            query=query,
            model=embedding_model,
            chunks=knowledge_base["chunks"],
            embeddings=knowledge_base["embeddings"],
        )

        return "\n\n".join(
            relevant_chunks
        )

    contents = _history_to_contents(
        history
    )

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=query
                )
            ],
        )
    )

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[search_notes],
        ),
    )

    return response.text or ""
