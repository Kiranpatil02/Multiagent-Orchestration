from base import Base


WRITER_SYSTEM_PROMPT=""

class WriterAgent(Base):
    name="WRITER"

    def execute(self, input_data: dict):
        research_results=input_data["research_results"]

        messages=[
            {
                "role":"system",
                "content":WRITER_SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":research_results
            }
        ]

        