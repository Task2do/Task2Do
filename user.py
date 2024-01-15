from pydantic import BaseModel

from person import Person
from task import Task


class User(BaseModel):
    user_name: str
    password: str
    life: Person
    tasks: [Task]
