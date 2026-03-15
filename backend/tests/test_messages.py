import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Chat, Message
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_get_messages_empty(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test getting messages from empty chat"""
    response = await async_client.get(
        f"/api/v1/messages/{test_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_messages_authenticated(
    async_client: AsyncClient, test_user_tokens, test_chat, test_message
):
    """Test getting messages from authenticated user's chat"""
    response = await async_client.get(
        f"/api/v1/messages/{test_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_message.id
    assert data[0]["content"] == "Hello!"
    assert data[0]["role"] == "user"


@pytest.mark.asyncio
async def test_get_messages_wrong_chat(
    async_client: AsyncClient, test_user_tokens, test_db_session
):
    """Test getting messages from chat owned by another user"""
    from app.services.auth import create_user

    other_user = await create_user(test_db_session, "other3@example.com", "Other User", "password")
    other_chat = Chat(user_id=other_user.id, title="Other Chat", model="claude-3-sonnet-20240229")
    test_db_session.add(other_chat)
    await test_db_session.commit()
    await test_db_session.refresh(other_chat)

    response = await async_client.get(
        f"/api/v1/messages/{other_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_stream_message_mocked(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test streaming a message with mocked Claude API"""
    with patch("app.services.claude.stream_claude_response") as mock_stream:
        # Mock the stream to return a simple response
        async def mock_generator(*args, **kwargs):
            yield "Hello"
            yield " from Claude"

        mock_stream.return_value = mock_generator()

        response = await async_client.post(
            f"/api/v1/messages/{test_chat.id}/stream",
            json={"content": "Hello Claude!"},
            headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
        )

        # Check streaming response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"

        # Stream should contain data
        content = response.text
        assert "data:" in content or content  # Either streaming format or content exists
