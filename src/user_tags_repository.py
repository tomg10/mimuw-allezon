import random
from typing import List, Optional

import redis

from schema import UserTag, ProductInfo


class UserTagsRepository:

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6778, db=0)

    def _serialize_tags(self, tags: List[UserTag]) -> str:
        result = []
        for tag in tags:
            product_info = tag.product_info
            serialized_action = f"#{product_info.product_id}|" \
                                f"{product_info.price}|" \
                                f"{product_info.brand_id}|" \
                                f"{product_info.category_id}|" \
                                f"{tag.time}|" \
                                f"{tag.device}|" \
                                f"{tag.country}|" \
                                f"{tag.origin}"
            result.append(serialized_action)
        return ''.join(result)

    def _deserialize_tags(self, cookie: str, action: str, serialized_tags: str) -> List[UserTag]:
        result = []
        for serialized_action in serialized_tags.split("#"):
            if serialized_action == '':
                continue
            parameters = serialized_action.split("|")
            product_info = ProductInfo(product_id=parameters[0],
                                       price=int(parameters[1]),
                                       brand_id=parameters[2],
                                       category_id=parameters[3])
            tag = UserTag(action=action,
                          time=parameters[4],
                          device=parameters[5],
                          country=parameters[6],
                          origin=parameters[7],
                          product_info=product_info,
                          cookie=cookie)
            result.append(tag)
        return result

    def get_user_tags(self,
                      cookie: str,
                      action: str,
                      time_start: Optional[str] = None,
                      time_end: Optional[str] = None,
                      ) -> List[UserTag]:
        serialized_tags_bytes = self.redis.get(f"user|{cookie}|{action}")
        if not serialized_tags_bytes:
            return []
        serialized_tags = serialized_tags_bytes.decode('utf-8')
        result: List[UserTag] = self._deserialize_tags(cookie=cookie, serialized_tags=serialized_tags, action=action)
        if time_start:
            result = [tag for tag in result if tag.time >= time_start]
        if time_end:
            result = [tag for tag in result if tag.time < time_end]
        return list(reversed(result))

    def add_user_tag(self, tag: UserTag):
        with self.redis.lock(name=f"user|{tag.cookie}|{tag.action}_lock", timeout=10):
            if random.randint(0, 100) != 100:
                self.redis.append(f"user|{tag.cookie}|{tag.action}", self._serialize_tags(tags=[tag]))
            else:
                current_tags = self.get_user_tags(cookie=tag.cookie, action=tag.action)
                current_tags = sorted(current_tags, key=lambda x: x.time)
                current_tags = current_tags[:199]
                current_tags.append(tag)
                self.redis.set(f"user|{tag.cookie}|{tag.action}", self._serialize_tags(tags=current_tags))
