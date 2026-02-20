from base import Base
from agents.schema.writer_schema import WRITER_SCHEMA


WRITER_SYSTEM_PROMPT=""

class WriterAgent(Base):
    name="WRITER"

    def __init__(self):
        super().__init__(WRITER_SCHEMA,WRITER_SYSTEM_PROMPT)


        