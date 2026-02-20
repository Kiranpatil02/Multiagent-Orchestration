from base import Base



RESEARCH_SYSTEM_PROMPT=""

class ResearchAgent(Base):

    name="RESEARCHER"

    def execute(self, input_data: dict):
        topic=input_data["topic"]

        messages=[
            {
                "role":"system",
                "content":RESEARCH_SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":topic
            }
        ]
