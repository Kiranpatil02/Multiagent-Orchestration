from base import Base
from agents.schema.research_schema import RESEARCHER_SCHEMA


RESEARCH_SYSTEM_PROMPT=""

class ResearchAgent(Base):

    name="RESEARCHER"

    def __init__(self):
        super().__init__(RESEARCHER_SCHEMA)

    def run(self, steps_description: str):
        
        return self.execute(RESEARCH_SYSTEM_PROMPT, steps_description)
    
