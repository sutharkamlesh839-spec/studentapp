from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class MessageResponse(APIModel):
    message: str


class Page(APIModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
