from pydantic import BaseModel


class ProductInfo(BaseModel):
    product_id: str
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

