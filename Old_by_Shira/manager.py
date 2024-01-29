from pydantic import BaseModel

from person import Person
from user import User


class Manager(BaseModel):
    user_name: str
    password: str
    life: Person
    my_employees: [User]
