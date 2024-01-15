from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    project_id: int
    task_id: int
    description: str
    status: ["didn't start", "in progress", "finished"]
    created_by_user: bool = False
    is_active: bool = True
    deadline: datetime