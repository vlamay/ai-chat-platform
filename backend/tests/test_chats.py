import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Chat


@pytest.mark.asyncio
async def test_create_chat_authenticated(async_client: AsyncClient, test_user_tokens):
    """Test creating a chat with valid authentication"""
    response = await async_client.post(
        "/api/v1/chats",
        json={
            "title": "New Chat",
            "model": "claude-3-sonnet-20240229",
        },
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Chat"
    assert data["model"] == "claude-3-sonnet-20240229"
    assert data["user_id"] == test_user_tokens["user_id"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_chat_unauthenticated(async_client: AsyncClient):
    """Test creating a chat without authentication"""
    response = await async_client.post(
        "/api/v1/chats",
        json={
            "title": "New Chat",
            "model": "claude-3-sonnet-20240229",
        },
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_chats_empty(async_client: AsyncClient, test_user_tokens):
    """Test listing chats when none exist"""
    response = await async_client.get(
        "/api/v1/chats",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_chats_with_data(
    async_client: AsyncClient, test_user_tokens, test_chat, test_message
):
    """Test listing chats with messages"""
    response = await async_client.get(
        "/api/v1/chats",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_chat.id
    assert data[0]["title"] == test_chat.title
    assert data[0]["message_count"] == 1


@pytest.mark.asyncio
async def test_get_chat_own(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test getting a chat owned by current user"""
    response = await async_client.get(
        f"/api/v1/chats/{test_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_chat.id
    assert data["title"] == test_chat.title


@pytest.mark.asyncio
async def test_get_chat_other_user(
    async_client: AsyncClient, test_user_tokens, test_db_session
):
    """Test getting a chat owned by another user (should fail)"""
    # Create a chat for a different user
    from app.services.auth import create_user

    other_user = await create_user(test_db_session, "other@example.com", "Other User", "password")
    other_chat = Chat(user_id=other_user.id, title="Other Chat", model="claude-3-sonnet-20240229")
    test_db_session.add(other_chat)
    await test_db_session.commit()
    await test_db_session.refresh(other_chat)

    response = await async_client.get(
        f"/api/v1/chats/{other_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_chat_title(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test updating chat title"""
    response = await async_client.patch(
        f"/api/v1/chats/{test_chat.id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_chat_model(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test updating chat model"""
    response = await async_client.patch(
        f"/api/v1/chats/{test_chat.id}",
        json={"model": "claude-3-opus-20240229"},
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "claude-3-opus-20240229"


@pytest.mark.asyncio
async def test_delete_chat(async_client: AsyncClient, test_user_tokens, test_chat):
    """Test deleting a chat"""
    chat_id = test_chat.id
    response = await async_client.delete(
        f"/api/v1/chats/{chat_id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 204

    # Verify chat is deleted
    response = await async_client.get(
        f"/api/v1/chats/{chat_id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_chat_other_user(
    async_client: AsyncClient, test_user_tokens, test_db_session
):
    """Test deleting a chat owned by another user (should fail)"""
    from app.services.auth import create_user

    other_user = await create_user(test_db_session, "other2@example.com", "Other User", "password")
    other_chat = Chat(user_id=other_user.id, title="Other Chat", model="claude-3-sonnet-20240229")
    test_db_session.add(other_chat)
    await test_db_session.commit()
    await test_db_session.refresh(other_chat)

    response = await async_client.delete(
        f"/api/v1/chats/{other_chat.id}",
        headers={"Authorization": f"Bearer {test_user_tokens['access_token']}"},
    )
    assert response.status_code == 404
    assert "Chat not found" in response.json()["detail"]
