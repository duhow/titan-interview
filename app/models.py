from datetime import date

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    username: str = Field(primary_key=True, max_length=32)
    birthdate: date
