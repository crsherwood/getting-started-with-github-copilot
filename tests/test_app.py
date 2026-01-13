import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi import status
from src.app import app

@pytest.mark.asyncio
async def test_root_redirect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT)
