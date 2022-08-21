from typing import List

from pydantic import BaseModel


class ProductInfo(BaseModel):
    product_id: int
    brand_id: str
    category_id: str
    price: int

class UserTag(BaseModel):
    time: str
    cookie: str
    country: str
    device: str
    action: str
    product_info: ProductInfo

class UserProfile(BaseModel):
    cookie: str
    views: List[UserTag]
    buys: List[UserTag]