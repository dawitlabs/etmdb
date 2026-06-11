import pytest


@pytest.mark.asyncio
async def test_search_by_title(client, headers):
    r = await client.get("/api/v1/search?q=Difret", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["title"] == "Difret"


@pytest.mark.asyncio
async def test_search_by_overview(client, headers):
    r = await client.get("/api/v1/search?q=shepherd", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["title"] == "Lamb"


@pytest.mark.asyncio
async def test_search_no_results(client, headers):
    r = await client.get("/api/v1/search?q=xyznonexistent", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_search_amharic(client, headers):
    r = await client.get("/api/v1/search?q=ድፍረት", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
