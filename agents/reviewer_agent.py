from base import Base
from agents.schema.reviewer_schema import REVIEWER_SCHEMA

REVIEWER_SYSTEM_PROMPT="""
You are a review agent responsible for evaluating draft documents for quality.

Your job is to review the draft and determine if it meets quality standards.

Output JSON format:
{
    "approved": true/false,
    "feedback": "Specific feedback on what needs improvement (required if not approved)"
}

"""


class ReviewerAgent(Base):
    name="REVIEWER"

    def __init__(self):
        super().__init__(REVIEWER_SCHEMA,REVIEWER_SYSTEM_PROMPT)
