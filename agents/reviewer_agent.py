from base import Base


REVIEWER_SYSTEM_PROMPT=""


class ReviewerAgent(Base):
    name="REVIEWER"

    def execute(self, input_data:dict):

        draft=input_data["draft"]

        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": draft}
        ]