from pydantic import BaseModel
from datetime import datetime


class HelloMessage(BaseModel):
    time: datetime
    message: str
