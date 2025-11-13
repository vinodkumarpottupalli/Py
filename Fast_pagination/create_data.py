import asyncio
import uuid
import random
from database import async_session, engine
from models import Base, Car


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def generate(n: int = 1000):
    async with async_session() as session:
        objs = []
        for i in range(1, n + 1):
            if i % 3 == 1:
                brand = 'Honda'
            elif i % 3 == 2:
                brand = 'Ford'
            else:
                brand = 'BMW'

            model = f"{brand} {i}"
            transmission = 'AUTOMATIC' if (i % 2 != 0) else 'MANUAL'
            price = random.randint(30000, 80000)
            release_year = 2020 + (i % 3)
            car = Car(
                id=str(uuid.uuid4()),
                brand=brand,
                model=model,
                transmission=transmission,
                price=price,
                release_year=release_year,
            )
            objs.append(car)

        session.add_all(objs)
        await session.commit()


if __name__ == '__main__':
    n = 5000
    print(f"Creating tables and inserting {n} sample rows.")
    asyncio.run(create_tables())
    asyncio.run(generate(n))
    print("DB Insertion Completed.")
