from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID


class TaskType(str, Enum):
    PLAN="PLAN"
    RESEARCH="RESEARCH"
    WRITE="WRITE"
    REVIEW="REVIEW"

class TaskStatus(str,Enum):
    PENDING="PENDING"
    QUEUED="QUEUED"
    IN_PROGRESS="IN_PROGRESS"
    FAILED="FAILED"
    CANCELLED="CANCELLED"
    FINISH="FINISH"

class PlanStatus(str,Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Status(str,Enum):
    RECEIVED="RECEIVED"
    PLANNING="PLANNING"
    IN_PROGRESS="IN_PROGRESS"
    FAILED="FAILED"
    COMPLETED="COMPELETED"

class Agent(str,Enum):
    PLANNER="PLANNER"
    RESEARCHER="RESEARCHER"
    WRITER="WRITER"
    REVIEWER="REVIEWER"

class AgentStatus(str,Enum):
    SUCCESS="SUCCESS"
    FAILED="FAILED"


@dataclass
class Request:
    id: int
    user_txt:str
    status:Status
    plan_id:Optional[str]=None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Plan:
    id: int
    request_id:str
    user_query:str
    max_revision:int=3
    current_revision:int=0
    version:int=1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class Task:
    id:str
    plan_id:str
    type:TaskType
    status:TaskStatus
    priority:int
    assigned_agent:str
    retry_count:int
    max_retries:int
    version:int
    created_at:datetime
    updated_at:datetime

@dataclass
class AgentOutput:
    id:str
    task_id:int
    agent_id:str
    status:AgentStatus
    payload:str
    version:int=1
    confidence_score:Optional[int]=None
    error_message:Optional[str]=None
    duration:int=0
    created_at:datetime=field(default_factory=datetime.utcnow)



