from enum import Enum

class TaskType(str, Enum):
    PLANNER="PLANNER"
    RESEARCH="RESEARCH"
    WRITE="WRITE"
    REVIEW="REVIEW"

class TaskStatus(str,Enum):
    PENDING="PENDING"
    IN_PROGRESS="IN_PROGRESS"
    FAILED="FAILED"
    FINISH="FINISH"

class PlanStatus(str,Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"



