import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import decode_token


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient, test_db_session: AsyncSession):
    """Test successful user registration"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, test_user):
    """Test registration with duplicate email"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",  # Already used by test_user
            "name": "Another User",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_user):
    """Test successful login"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, test_user):
    """Test login with wrong password"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    """Test login with non-existent user"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_valid(async_client: AsyncClient, test_user_tokens):
    """Test token refresh with valid refresh token"""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": test_user_tokens["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # Verify new token is different
    assert data["access_token"] != test_user_tokens["access_token"]


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client: AsyncClient):
    """Test token refresh with invalid refresh token"""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_as_access_token(async_client: AsyncClient, test_user_tokens):
    """Test token refresh using access token instead of refresh token (should fail)"""
    # Create an access token and try to use it as a refresh token
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": test_user_tokens["access_token"]},
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]
