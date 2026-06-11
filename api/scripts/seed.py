"""
Seed the ETMDB database from gathered JSON files.

Usage:
    python -m scripts.seed
    python -m scripts.seed --seed-json /path/to/etmdb_seed.json --youtube-json /path/to/youtube.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path

from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from app.models.api_key import APIKey
from app.models.credit import Credit
from app.models.genre import Genre, MovieGenre
from app.models.movie import Movie
from app.models.person import Person
from app.models.youtube_link import YouTubeLink
from app.slug import slugify
from app.dependencies import hash_api_key

SEED_JSON = Path.home() / "etmdb_seed.json"
YOUTUBE_JSON = Path.home() / "amharic_ethiopian_movies.json"

GENRES = [
    ("drama", "Drama", "ድራማ"),
    ("comedy", "Comedy", "ኮሜዲ"),
    ("romance", "Romance", "ፍቅር"),
    ("action", "Action", "አክሽን"),
    ("thriller", "Thriller", None),
    ("horror", "Horror", None),
    ("documentary", "Documentary", "ዶክመንተሪ"),
    ("historical", "Historical", "ታሪካዊ"),
    ("social", "Social", "ማህበራዊ"),
]


def normalize_title(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    noise = [
        "full ethiopian movie", "new ethiopian movie", "ethiopian movie",
        "amharic movie", "ethiopian film", "amharic film",
        "full movie", "full length", "new movie",
        "official video", "ሙሉ ፊልም", "አዲስ", "አማርኛ ፊልም",
    ]
    for year in range(2010, 2030):
        noise.append(str(year))
    for word in noise:
        t = t.replace(word, "")
    return re.sub(r"\s+", " ", t).strip()


def unique_slug(title: str, existing: set[str]) -> str:
    base = slugify(title) or "untitled"
    slug = base
    counter = 1
    while slug in existing:
        slug = f"{base}-{counter}"
        counter += 1
    existing.add(slug)
    return slug


def seed_genres(session: Session) -> None:
    for slug, name, name_am in GENRES:
        existing = session.exec(select(Genre).where(Genre.slug == slug)).first()
        if not existing:
            session.add(Genre(name=name, name_am=name_am, slug=slug))
    session.commit()
    print(f"  Seeded {len(GENRES)} genres")


def seed_movies(session: Session, seed_path: Path) -> dict[str, int]:
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])

    # Pre-load existing unique keys to avoid constraint errors on re-seed
    existing_movies = session.exec(select(Movie)).all()
    slug_set: set[str] = {m.slug for m in existing_movies}
    existing_tmdb_ids: set[int] = {m.tmdb_id for m in existing_movies if m.tmdb_id is not None}
    existing_imdb_ids: set[str] = {m.imdb_id for m in existing_movies if m.imdb_id is not None}
    existing_wikidata_ids: set[str] = {m.wikidata_id for m in existing_movies if m.wikidata_id is not None}
    title_to_id: dict[str, int] = {normalize_title(m.title): m.id for m in existing_movies}

    skipped = 0
    imported = 0

    for record in records:
        title = record.get("title")
        source = record.get("source", "")
        if not title:
            continue
        if source == "wikipedia_list" and not record.get("description"):
            skipped += 1
            continue

        # Skip already-imported records by any unique ID
        tmdb_id = record.get("tmdb_id")
        imdb_id = record.get("imdb_id")
        wikidata_id = record.get("wikidata_id")
        if (
            (tmdb_id and tmdb_id in existing_tmdb_ids)
            or (imdb_id and imdb_id in existing_imdb_ids)
            or (wikidata_id and wikidata_id in existing_wikidata_ids)
        ):
            skipped += 1
            continue

        slug = unique_slug(title, slug_set)
        languages = record.get("languages", [])
        countries = record.get("countries", [])

        media_type = record.get("type", "movie")
        if media_type not in ("movie", "series"):
            media_type = "movie"

        movie = Movie(
            title=title,
            original_title=record.get("original_title"),
            slug=slug,
            overview=record.get("description"),
            poster_url=record.get("image_url"),
            backdrop_url=record.get("backdrop_url"),
            release_date=record.get("release_date"),
            release_year=_parse_year(record.get("release_year") or record.get("release_date")),
            spoken_languages=languages if isinstance(languages, list) else [],
            countries=countries if isinstance(countries, list) else [],
            tmdb_id=record.get("tmdb_id"),
            imdb_id=record.get("imdb_id"),
            wikidata_id=record.get("wikidata_id"),
            wikipedia_url=record.get("wikipedia_url"),
            type=media_type,
            source=source,
            tmdb_rating=record.get("tmdb_rating"),
            tmdb_votes=record.get("tmdb_votes"),
        )
        session.add(movie)
        session.flush()

        title_to_id[normalize_title(title)] = movie.id

        directors = record.get("directors", [])
        for director_name in directors:
            _add_credit(session, movie.id, director_name, "director", slug_set)

        imported += 1

    session.commit()
    print(f"  Imported {imported} movies, skipped {skipped} stubs")
    return title_to_id


def seed_youtube(
    session: Session, youtube_path: Path, title_to_id: dict[str, int]
) -> None:
    with open(youtube_path, encoding="utf-8") as f:
        data = json.load(f)

    videos = data.get("videos", [])
    existing_video_ids: set[str] = set(session.exec(select(YouTubeLink.video_id)).all())
    matched = 0
    unmatched = 0
    movie_view_counts: dict[int, tuple[int, int]] = {}

    for video in videos:
        video_id = video.get("video_id")
        if not video_id or video_id in existing_video_ids:
            continue

        movie_id, confidence = _match_to_movie(video, title_to_id)
        view_count = video.get("view_count") or 0

        published = _parse_datetime(video.get("published_at"))

        link = YouTubeLink(
            video_id=video_id,
            title=video.get("title", ""),
            channel_title=video.get("channel_title"),
            channel_id=video.get("channel_id"),
            published_at=published,
            duration_seconds=video.get("duration_seconds"),
            view_count=view_count,
            like_count=video.get("like_count"),
            thumbnail_url=video.get("thumbnail_url"),
            embeddable=video.get("embeddable", True),
            language=video.get("language"),
            movie_id=movie_id,
            is_primary=False,
            match_confidence=confidence,
        )
        session.add(link)

        if movie_id:
            matched += 1
            best_views, best_link_id = movie_view_counts.get(movie_id, (0, 0))
            session.flush()
            if view_count > best_views:
                movie_view_counts[movie_id] = (view_count, link.id)
        else:
            unmatched += 1

    session.commit()

    for _movie_id, (_, link_id) in movie_view_counts.items():
        link = session.get(YouTubeLink, link_id)
        if link:
            link.is_primary = True
    session.commit()

    print(f"  Imported {len(videos)} YouTube links ({matched} matched, {unmatched} unmatched)")


def seed_demo_api_key(session: Session) -> None:
    demo_hash = hash_api_key("demo-key-etmdb-2026")
    existing = session.exec(select(APIKey).where(APIKey.key_hash == demo_hash)).first()
    if not existing:
        session.add(
            APIKey(
                key_hash=demo_hash,
                key_prefix="demo-key",
                name="Demo Key",
                email="demo@etmdb.dev",
                rate_limit=10000,
            )
        )
        session.commit()
        print("  Created demo API key: demo-key-etmdb-2026")


def _match_to_movie(
    video: dict, title_to_id: dict[str, int]
) -> tuple[int | None, float | None]:
    duration = video.get("duration_seconds") or 0
    if duration < 1800:
        return None, None

    normalized = normalize_title(video.get("title", ""))
    if not normalized:
        return None, None

    if normalized in title_to_id:
        return title_to_id[normalized], 1.0

    best_ratio = 0.0
    best_id = None
    for movie_title, movie_id in title_to_id.items():
        ratio = SequenceMatcher(None, normalized, movie_title).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_id = movie_id

    if best_ratio >= 0.7 and best_id is not None:
        return best_id, best_ratio

    return None, None


def _add_credit(
    session: Session, movie_id: int, person_name: str, role: str, slug_set: set[str]
) -> None:
    slug = slugify(person_name) or "unknown"
    person = session.exec(select(Person).where(Person.slug == slug)).first()
    if not person:
        person = Person(name=person_name, slug=unique_slug(person_name, slug_set))
        session.add(person)
        session.flush()

    session.add(Credit(movie_id=movie_id, person_id=person.id, role=role))


def _parse_year(value: str | int | None) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value)[:4])
    except (ValueError, TypeError):
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed ETMDB database")
    parser.add_argument("--seed-json", type=Path, default=SEED_JSON)
    parser.add_argument("--youtube-json", type=Path, default=YOUTUBE_JSON)
    parser.add_argument("--database-url", default="sqlite:///./etmdb.db")
    args = parser.parse_args()

    engine = create_engine(args.database_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        print("Seeding genres...")
        seed_genres(session)

        print("Seeding movies...")
        title_to_id = seed_movies(session, args.seed_json)

        print("Seeding YouTube links...")
        seed_youtube(session, args.youtube_json, title_to_id)

        print("Seeding demo API key...")
        seed_demo_api_key(session)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
