import datetime
from typing import Optional

import redis

from schema import UserTag, SingleBucket


class AggregatesRepository:

    def __init__(self, redis: Optional[redis.Redis] = None):
        self.redis = redis.Redis(host='localhost', port=6778, db=0) if not redis else redis

    def add_user_tag(self, tag: UserTag):

        variants = [f"{tag.origin}||", f"|{tag.product_info.brand_id}|", f"||{tag.product_info.category_id}"]
        for variant in variants:
            self.add_dense_tag(f"{tag.action}|{variant}|{tag.origin}|sum", minute_id=0, value=tag.product_info.price)
            self.add_dense_tag(f"{tag.action}|{variant}|{tag.origin}|count", minute_id=0, value=1)
        pass

    def extract_minute_id(self, time_raw: str):
        return int(datetime.datetime.fromisoformat(time_raw).timestamp() / 60)

    def add_dense_tag(self, filter_hash: str, minute_id: int, value: int) -> None:
        sum_key = f"{filter_hash}|{minute_id}"
        sum_value = self.redis.get(sum_key)
        if not sum_value:
            sum_value = 0
        sum_value += value
        self.redis.set(sum_key, sum_value)

    def get_dense_tag(self, filter_hash: str, minute_id: int) -> int:
        sum_key = f"{filter_hash}|{minute_id}"
        sum_value = self.redis.get(sum_key)
        if not sum_value:
            sum_value = 0
        return sum_value

    def get_aggregations(self,
                         aggregation_type: str,
                         action: str,
                         start_time: str,
                         end_time: str,
                         origin: str,
                         brand_id: str,
                         category_id: str,
                         ):
        start_minute = self.extract_minute_id(start_time)
        end_minute = self.extract_minute_id(end_time)
        is_sparse = (category_id and brand_id) or (category_id and origin) or (brand_id and origin)

        if is_sparse:
            # TODO
            raise Exception("Not implemented yet")
            return []
        else:
            result = []
            for i in range(start_minute, end_minute):
                value = self.get_dense_tag(filter_hash=f"{action}|{origin}|{brand_id}|{category_id}|{aggregation_type}",
                                           minute_id=i)
                result.append(SingleBucket(bucket_id=i - start_minute + 1, value=value))
            return result
