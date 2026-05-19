from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class IssuePriority(str, Enum):
    low = "low"
    medium = 'medium'
    high = 'high'


class CreateIssue(BaseModel):
    title: str = Field(min_length=3, max_length = 100)
    description : str = Field(min_length = 10,max_length = 1000)
    priority : IssuePriority = IssuePriority.medium

class UpdateIssue(BaseModel):
    title = Optional[str] = Field(default = None, max_length = 100)
    description = Optional[str] = Field(default = None,min_length=10, max_length = 1000)
    priority : Optional[IssuePriority] = None

class IssueResponse(BaseModel):
    id : int
    title : str
    description : str
    priority : IssuePriority
    


