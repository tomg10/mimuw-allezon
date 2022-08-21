import logging
from typing import Union, Optional

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT
from starlette.types import Message

from schema import UserTag, UserProfile
from user_tags_repository import UserTagsRepository

app = FastAPI()

logger = logging.getLogger("uvicorn")
tags_repository = UserTagsRepository()

class RequestContextLogMiddleware(BaseHTTPMiddleware):

    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        await self.set_body(request)
        body = await request.body()
        jsonbody = await request.json()
        logger.info(body)
        id_ = jsonbody['external_id']
        response = await call_next(request)
        return response



@app.post("/user_profiles/{cookie}")
async def get_tags(debug_answer: UserProfile, cookie: str, time_range: Optional[str], limit: Optional[int]):
    time_start = None if not time_range else time_range.split("_")[0]
    time_end = None if not time_range else time_range.split("_")[1]
    views = tags_repository.get_user_tags(cookie=cookie, action="VIEW", time_start=time_start, time_end=time_end)
    buys = tags_repository.get_user_tags(cookie=cookie, action="BUY", time_start=time_start, time_end=time_end)
    response = UserProfile(cookie=cookie, views=views[:limit], buys=buys[:limit])
    logger.info(f"{cookie} {time_range} {limit}")
    logger.info(f"Expected answer:\n{debug_answer.json()}")
    logger.info(f"Sent answer:\n{debug_answer.json()}")
    return debug_answer


@app.post("/user_tags", status_code=HTTP_204_NO_CONTENT)
async def add_tag(user_tag: UserTag):
    tags_repository.add_user_tag(tag=user_tag)
    logger.info(user_tag.json())
