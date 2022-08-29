import datetime
import json
import uuid
from multiprocessing import Pool
from multiprocessing.context import Process

import redis
import requests

from schema import ProductInfo, UserTag
from user_tags_repository import UserTagsRepository

r = redis.Redis(host='localhost', port=6778, db=0)
tags_repository = UserTagsRepository()

cookies = [str(uuid.uuid4()) for i in range(100)]

ops_count = 100


def single_worker_write(cookie_id):
    start_time = datetime.datetime.now()

    for _ in range(ops_count):
        action = generate_tag(cookie=cookies[cookie_id], action="VIEW")
        requests.post('http://localhost:8080/user_tags', json=action.dict()).raise_for_status()
    return datetime.datetime.now() - start_time


def single_worker_read(cookie_id):
    start_time = datetime.datetime.now()

    for _ in range(int(ops_count / 10)):
        result = tags_repository.get_user_tags(cookie=cookies[cookie_id], action="VIEW")[:200]
        [elem.json() for elem in result]
    return datetime.datetime.now() - start_time


def generate_tag(cookie: str, action: str) -> UserTag:
    product_info = ProductInfo(product_id=123,
                               price=123,
                               brand_id=str(uuid.uuid4()),
                               category_id=str(uuid.uuid4()))
    user_action = UserTag(product_info=product_info,
                          cookie=cookie,
                          action=action,
                          origin=str(uuid.uuid4()),
                          country=str(uuid.uuid4()),
                          device=str(uuid.uuid4()),
                          time=str(datetime.datetime.now()))
    return user_action


if __name__ == '__main__':
    # request = requests.post(
    #     url='http://localhost:8000/user_tags',
    #     json={"cookie": "A",
    #           "action": "B",
    #           "time": "C",
    #           "device": "D",
    #           "country": "E",
    #           "product_info":
    #               {
    #                   "price": 1,
    #                   "product_id": "F",
    #                   "brand_id": "G",
    #                   "category_id": "H"
    #               }
    #           }
    # )
    # print(request.content)
    # print(request.status_code)
    # print(json.dumps(json.loads(content), indent=4))
    workers_count = 5
    with Pool(workers_count) as p:
        elapsed1 = p.map(single_worker_write, [i for i in range(workers_count)])

    for i in range(workers_count):
        print(f"write worker:{i},  operations:{ops_count}, elapsed:{elapsed1[i]}")
    print(f"total operations: {ops_count * workers_count}")

    # with Pool(workers_count) as p:
    #     elapsed2 = p.map(single_worker_read, [i for i in range(workers_count)])
    #
    # for i in range(workers_count):
    #     print(f"read worker:{i},  operations:{ops_count/10}, elapsed:{elapsed2[i]}")
    # print(f"total operations: {ops_count * workers_count / 10}")
