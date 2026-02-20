from base import Base
import json


PLANNER_SYSTEM_PROMPT=""



class PlannerAgent(Base):
    name="PLANNER AGENT"

    def execute(self, input_data: dict):
        user_query=input_data["query"]

        messages=[
            {
                "role":"system",
                "content":PLANNER_SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":user_query
            }
        ]

        
