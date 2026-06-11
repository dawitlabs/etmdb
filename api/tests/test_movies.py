import pytest


@pytest.mark.asyncio
async def test_list_movies(client, headers):
    r = await client.get("/api/v1/movies", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_movies_pagination(client, headers):
    r = await client.get("/api/v1/movies?per_page=1&page=2", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["results"]) == 1
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_get_movie_by_slug(client, headers):
    r = await client.get("/api/v1/movies/difret", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Difret"
    assert data["original_title"] == "ድፍረት"
    assert data["release_year"] == 2014
    assert data["tmdb_rating"] == 7.2
    assert len(data["youtube_links"]) == 1
    assert data["youtube_links"][0]["video_id"] == "abc123"


@pytest.mark.asyncio
async def test_get_movie_not_found(client, headers):
    r = await client.get("/api/v1/movies/nonexistent", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_list_movies_filter_year(client, headers):
    r = await client.get("/api/v1/movies?year=2014", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["results"][0]["title"] == "Difret"
