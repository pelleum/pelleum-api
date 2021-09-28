from fastapi import Query

from app.usecases.schemas import request_pagination


def paginate(
    records_per_page=Query(200), page=Query(1)
) -> request_pagination.RequestPagination:

    records_per_page = int(records_per_page)
    page = int(page)

    records_per_page = min(records_per_page, 200)
    records_per_page = max(records_per_page, 0)
    page = max(page, 1)

    return request_pagination.RequestPagination(
        page=page, records_per_page=records_per_page
    )
