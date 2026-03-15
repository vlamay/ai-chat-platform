import anthropic
from typing import AsyncGenerator
from app.core.config import settings


async def stream_claude_response(
    messages: list[dict], model: str
) -> AsyncGenerator[str, None]:
    """Stream response from Claude API"""
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Convert messages to Claude format if needed
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    async with client.messages.stream(
        model=model,
        max_tokens=2048,
        messages=formatted_messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
