from models.models import TaskType
from db.queries import *
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent
from services.backoff import exponential_backoff


MAX_REVIEW=3

class Orchestrator:

    def __init__(self,db_session):
        self.db=db_session
        self.planner=PlannerAgent()
        self.researcher=ResearchAgent()
        self.writer=WriterAgent()
        self.reviewer=ReviewerAgent()


    def process(self,task):

        task_type=task["type"]
        data=json.loads(task["input_json"])

        if task_type==TaskType.PLANNER.value:
            
            plan_result=self.planner.run(data["query"])

            for step in plan_result["steps"]:
                create_task(
                    plan_id=task["plan_id"],
                    type=TaskType.RESEARCH.value,
                    input_json={"description":step["description"]},
                    parent_task_id=task["id"]
                )

        elif task_type==TaskType.RESEARCH.value:
            result=self.researcher.run(data["description"])

            create_task(
                plan_id=task["plan_id"],
                type=TaskType.WRITE.value,
                input_json={"research_notes": result["research_notes"]},
                parent_task_id=task["id"]
            )
        
        elif task_type==TaskType.WRITE.value:
            result=self.writer.run(data["research_notes"])

            create_task(
                plan_id=task["plan_id"],
                type=TaskType.REVIEW.value,
                input_json={"draft": result["draft"]},
                parent_task_id=task["id"],
                revision=task["revision"]
            )
        
        elif task_type==TaskType.REVIEW.value:
            result=self.reviewer.run(data["draft"])

            if result["approved"]:
                finish_task(task["id"])
                return
            if task["revision"]>=MAX_REVIEW:
                failed_task(task["id"])
                return
            
            create_task(
                plan_id=task["plan_id"],
                type=TaskType.WRITE.value,
                input_json={
                    "research_notes": data["draft"] + "\nFeedback:\n" + result.get("feedback", "")
                },
                parent_task_id=task["id"],
                revision=task["revision"] + 1
            )
        
        finish_task(task['id'])

    def start_process(self,task):
        try:
            self.process(task)
        except Exception as e:
            retry_count=task["retry_count"]
            max_retries=task["max_retries"]

            if retry_count<max_retries:
                next_run=exponential_backoff(retry_count)
                update_task_retry(task["id"],next_run)
            else:
                failed_task(task["id"])