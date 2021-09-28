from pydantic import BaseModel


class RequestPagination(BaseModel):
    page: int = 1
    records_per_page: int = 200


class MetaData(BaseModel):
    page: int
    records_per_page: int
    total_pages: int
    total_records: int
