from pydantic import BaseModel


class Request(BaseModel):
    request_id: int
    purpose: ["affiliation", "project"]
    description: str