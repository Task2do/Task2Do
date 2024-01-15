from pydantic import BaseModel


class Person(BaseModel):
    private_name: str
    surname: str
    company: int
    mail: str