import logging
from typing import Union, Optional

from fastapi import FastAPI
from starlette.status import HTTP_204_NO_CONTENT

from schema import UserTag
from user_tags_repository import UserTagsRepository

app = FastAPI()

logger = logging.getLogger("uvicorn")
tags_repository = UserTagsRepository()

@app.post("/user_profiles/{cookie}")
async def get_tags(cookie: str, time_range: Optional[str], limit: Optional[int]):
    time_start = None if not time_range else time_range.split("_")[1]
    time_end = None if not time_range else time_range.split("_")[0]
    views = tags_repository.get_user_tags(cookie=cookie, action="VIEW", time_start=time_start, time_end=time_end)
    buys = tags_repository.get_user_tags(cookie=cookie, action="BUY", time_start=time_start, time_end=time_end)
    logger.info(f"{cookie} {time_range} {limit}")
    return {
        "cookie": cookie,
        "views": views[:limit],
        "buys": buys[:limit]
    }


@app.post("/user_tags", status_code=HTTP_204_NO_CONTENT)
async def add_tag(user_tag: UserTag):
    tags_repository.add_user_tag(tag=user_tag)
    logger.info(user_tag.json())
