import pytest


@pytest.mark.asyncio
async def test_list_youtube_links(client, headers):
    r = await client.get("/api/v1/youtube", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_youtube_by_video_id(client, headers):
    r = await client.get("/api/v1/youtube/abc123", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Difret Full Movie"
    assert data["view_count"] == 500000


@pytest.mark.asyncio
async def test_youtube_not_found(client, headers):
    r = await client.get("/api/v1/youtube/nonexistent", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_youtube_linked_only(client, headers):
    r = await client.get("/api/v1/youtube?linked_only=true", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["video_id"] == "abc123"
