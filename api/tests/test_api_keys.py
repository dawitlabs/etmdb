import pytest


@pytest.mark.asyncio
async def test_missing_api_key(client):
    r = await client.get("/api/v1/movies")
    assert r.status_code == 401
    assert "Missing API key" in r.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_api_key(client):
    r = await client.get("/api/v1/movies", headers={"X-Api-Key": "bad-key"})
    assert r.status_code == 401
    assert "Invalid" in r.json()["detail"]


@pytest.mark.asyncio
async def test_valid_api_key(client, headers):
    r = await client.get("/api/v1/movies", headers=headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_stats_no_auth_required(client):
    r = await client.get("/api/v1/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_movies" in data
