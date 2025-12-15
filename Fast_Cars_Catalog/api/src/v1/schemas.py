from pydantic import BaseModel


class CarSchema(BaseModel):
    id: str
    brand: str
    model: str
    transmission: str
    price: int
    release_year: int

    class Config:
        orm_mode = True
