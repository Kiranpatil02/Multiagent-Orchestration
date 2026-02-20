from base import Base
from agents.schema.planner_schema import PLANNER_SCHEMA


PLANNER_SYSTEM_PROMPT=""



class PlannerAgent(Base):
    name="PLANNER AGENT"

    def __init__(self):
        super().__init__(PLANNER_SCHEMA,PLANNER_SYSTEM_PROMPT)

        
