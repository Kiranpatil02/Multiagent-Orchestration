from base import Base
from agents.schema.research_schema import RESEARCHER_SCHEMA


RESEARCH_SYSTEM_PROMPT=""

class ResearchAgent(Base):

    name="RESEARCHER"

    def __init__(self):
        super().__init__(RESEARCHER_SCHEMA,RESEARCH_SYSTEM_PROMPT)
    
