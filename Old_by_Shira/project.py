from datetime import datetime

from pydantic import BaseModel

from manager import Manager
from user import User


class Project(BaseModel):
    project_id: int
    manager: Manager
    project_employees: [User]
    deadline: datetime
    is_active: bool = False