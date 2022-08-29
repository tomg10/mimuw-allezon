import logging
from typing import Union, Optional, Callable, List

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT
from starlette.types import Message

from schema import UserTag, UserProfile
from aggregates_repository import AggregatesRepository
from user_tags_repository import UserTagsRepository

app = FastAPI()

logger = logging.getLogger("uvicorn")
tags_repository = UserTagsRepository()
aggregates_repository = AggregatesRepository()


@app.post("/user_profiles/{cookie}")
async def get_tags(cookie: str, time_range: Optional[str], limit: Optional[int]):
    time_start = None if not time_range else time_range.split("_")[0]
    time_end = None if not time_range else time_range.split("_")[1]
    views = tags_repository.get_user_tags(cookie=cookie, action="VIEW", time_start=time_start, time_end=time_end)
    buys = tags_repository.get_user_tags(cookie=cookie, action="BUY", time_start=time_start, time_end=time_end)
    response = UserProfile(cookie=cookie, views=views[:limit], buys=buys[:limit])
    return response


@app.post("/user_tags", status_code=HTTP_204_NO_CONTENT)
async def add_tag(user_tag: UserTag):
    tags_repository.add_user_tag(tag=user_tag)
    #aggregates_repository.add_user_tag(tag=user_tag)


# @app.post("/aggregates")
# async def get_aggregates(time_range: str,
#                          action: str,
#                          brand_id: Optional[str],
#                          category_id: Optional[str],
#                          origin: Optional[str], aggregates: List[str]):
#     pass
#     # aggregates = aggregates_repository.get_aggregations()
