"""
Pagination helper for MongoDB queries.
"""
from typing import Any, Dict, List, Optional
from math import ceil


class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 10):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), 100)  # cap at 100
        self.skip = (self.page - 1) * self.page_size


def paginate_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    """Build a standardized paginated response envelope."""
    total_pages = ceil(total / page_size) if page_size > 0 else 1
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
