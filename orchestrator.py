from models.models import TaskType
from db.queries import *
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent


MAX_REVIEW=3

class Orchestrator:

    def __init__(self,db_session):
        self.db=db_session
        self.planner=PlannerAgent()
        self.researcher=ResearchAgent()
        self.writer=WriterAgent()
        self.reviewer=ReviewerAgent()


    def run_task(self,task):
        try:
            task.status="PLANNING"
            # self.db.commit()

            plan_result=self.planner.run(task.user_input)
            task.plan=plan_result

            self.db.commit()

            for subtasks in plan_result["steps"]:
                task.status="RESEARCHING"

                research=self.researcher.run(subtasks["description"])

                task.status="WRITING"

                draft=self.writer.run(research["research_notes"])

                review_count=0
                approved=False

                while review_count<MAX_REVIEW:
                    task.status="REVIEWING"
                    self.db.commit()

                    review=self.reviewer.run(draft["draft"])

                    if review["approved"]:
                        approved=True
                        final_output+=draft["draft"]
                        break

                    rewrite=(
                        draft["draft"]
                        +"Reviewer Feedback:"
                        +review.get("feedback","")
                    )

                    draft=self.writer.run(rewrite)
                    review_count+=1
                if not approved:
                    raise Exception("Allocated Reviewes exceeded.")
                
            task.result=final_output
            task.status="COMPLETED"
            self.db.commit()
        except Exception as e:
            task.status="FAILED"
            task.error_message=str(e)
            self.db.commit()

            raise
