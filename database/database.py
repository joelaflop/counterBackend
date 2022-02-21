# import sqlalchemy
# from sqlalchemy import MetaData
# from sqlalchemy import Table, Column, Integer, String
# from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import selectinload  # used for relationships
from constants import DEBUG, DATABASE_CONNECTION_STRING

mapper_registry = registry()
Base = mapper_registry.generate_base()

engine = create_async_engine(DATABASE_CONNECTION_STRING, echo=DEBUG, future=True)

# sessionmaker version
session_factory = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# async with engine.begin() as conn:
#     result = await conn.execute(sqlalchemy.text("select * from users"))
#     print(result.all())
