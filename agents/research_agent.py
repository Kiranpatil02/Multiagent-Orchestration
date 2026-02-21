from base import Base
from agents.schema.research_schema import RESEARCHER_SCHEMA


RESEARCH_SYSTEM_PROMPT="""

You are a research agent responsible for gathering information on specific topics.

Your job is to provide comprehensive research notes based on the given description.

IMPORTANT:
Output JSON format only:
{
    "research_notes": "Research findings, facts, and relevant information"
}

"""

class ResearchAgent(Base):

    name="RESEARCHER"

    def __init__(self):
        super().__init__(RESEARCHER_SCHEMA,RESEARCH_SYSTEM_PROMPT)
    
