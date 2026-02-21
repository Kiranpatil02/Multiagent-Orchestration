from agents.base import Base
from agents.schema.writer_schema import WRITER_SCHEMA


WRITER_SYSTEM_PROMPT="""

You are a writing agent responsible for understanding research into clear, well structured, clean reports.

Your job is to take research notes and create a well draft document.

IMPORTANT:
Output JSON format:
{
    "draft": "Complete draft report with introduction, body sections, and conclusion"
}

"""

class WriterAgent(Base):
    name="WRITER"

    def __init__(self):
        super().__init__(WRITER_SCHEMA,WRITER_SYSTEM_PROMPT)


        