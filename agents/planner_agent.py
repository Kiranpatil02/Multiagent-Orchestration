from agents.base import Base
from agents.schema.planner_schema import PLANNER_SCHEMA


PLANNER_SYSTEM_PROMPT="""
You are a planning agent responsible for breaking down complex tasks into discrete subtasks.

Your job is to analyze the user's request and create a step-by-step plan where each step can be researched independently.
IMPORTANT:Max two steps

IMPORTANT:
Output JSON format only:
{
    "steps": [
        {
            "title": "step title",
            "description": "description of what needs to be researched"
        }
    ]
}


"""



class PlannerAgent(Base):
    name="PLANNER AGENT"

    def __init__(self):
        super().__init__(PLANNER_SCHEMA,PLANNER_SYSTEM_PROMPT)

        
