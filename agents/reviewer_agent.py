from base import Base
from agents.schema.reviewer_schema import REVIEWER_SCHEMA

REVIEWER_SYSTEM_PROMPT=""


class ReviewerAgent(Base):
    name="REVIEWER"

    def __init__(self):
        super().__init__(REVIEWER_SCHEMA,REVIEWER_SYSTEM_PROMPT)
