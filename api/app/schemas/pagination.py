from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    page: int
    per_page: int
    total: int
    total_pages: int
    results: list[T]

    @classmethod
    def create(
        cls, results: list[T], total: int, page: int, per_page: int
    ) -> "PaginatedResponse[T]":
        return cls(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=ceil(total / per_page) if per_page > 0 else 0,
            results=results,
        )
