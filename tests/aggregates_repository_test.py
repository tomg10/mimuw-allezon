import datetime
import unittest
import uuid
from typing import List

import redis
import testing.redis

from aggregates_repository import AggregatesRepository
from schema import UserTag, ProductInfo, SingleBucket


class AggregatesRepositoryTest(unittest.TestCase):

    def setUp(self) -> None:
        self.redis_setup = testing.redis.RedisServer()
        self.redis_setup.__enter__()
        self.redis = redis.Redis(**self.redis_setup.dsn())
        self.aggregates_repository = AggregatesRepository(redis=self.redis)

    def tearDown(self):
        self.redis_setup.__exit__()

    def generate_tag(self, cookie: str, action: str, time: datetime.datetime,
                     category_id: int = 1,
                     origin_id: int = 2,
                     country_id: int = 3,
                     brand_id: int = 4,
                     price: int = 100) -> UserTag:
        product_info = ProductInfo(product_id=123,
                                   price=price,
                                   brand_id=f"some_brand_{brand_id}",
                                   category_id=f"some_category_{category_id}",
                                   )
        user_action = UserTag(product_info=product_info,
                              cookie=cookie,
                              action=action,
                              origin=f"origin_{origin_id}",
                              country=f"country_{country_id}",
                              device=str(uuid.uuid4()),
                              time=str(time),
                              )
        return user_action

    def print_buckets(self, buckets: List[SingleBucket]):
        for bucket in buckets:
            print(f"{bucket.bucket_id:<3}: {bucket.value}")


    def test_simple_redis(self):
        base_date = datetime.datetime(year=2010, month=10, day=5)
        tag = self.generate_tag(cookie="cookie_A", action="VIEW", time=base_date)
        self.aggregates_repository.add_user_tag(tag)
        result = self.aggregates_repository.get_aggregations(aggregation_type="sum",
                                                    start_time=str(base_date - datetime.timedelta(minutes=10)),
                                                    end_time=str(base_date + datetime.timedelta(minutes=10)),
                                                    action="",
                                                    brand_id="",
                                                    category_id="",
                                                    origin="")
        self.print_buckets(result)