from models.models import TaskType
from db.queries import *
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent
from services.backoff import exponential_backoff
import json


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
        task_id = task["id"]
        plan_id = task["plan_id"]
        data=json.loads(task["input_json"])

        if task_type==TaskType.PLANNER.value:
            
            plan_result=self.planner.run(data["query"])

            print("PLAN RESULTS::",plan_result)

            for step in plan_result["steps"]:
                create_task(
                    plan_id=plan_id,
                    task_type=TaskType.RESEARCH.value,
                    parent_task_id=None,
                    input_data={"description":step["description"]},
                )

            finish_task(task_id, plan_result)
            print(f"Done with {len(plan_result['steps'])} research tasks")
            return

        elif task_type==TaskType.RESEARCH.value:
            result=self.researcher.run(data["description"])
            finish_task(task_id,result) 

            print("======RESEARCH RESULTS======")

            if all_research_complete(plan_id):
                all_research=get_all_research_outputs(plan_id)
                conactinate="\n\n--\nn".join(all_research)
                
                print("=====Total Research=====",conactinate)

                create_task(
                    plan_id=plan_id,
                    task_type=TaskType.WRITE.value,
                    input_data={"research_notes":conactinate},
                    parent_task_id=None
                )
                print(" Done with research, now creating write task")
            return
        
        elif task_type==TaskType.WRITE.value:
            result=self.writer.run(data["research_notes"])

            print("===========wRITE RESULTS==========",result)

            finish_task(task_id, {**result, "content": result.get("draft", "")})

            create_task(
                plan_id=plan_id,
                task_type=TaskType.REVIEW.value,
                input_data={"draft": result["draft"]},
                parent_task_id=None,
                revision=task["revision"]
            )
            print(f" Draftt written (revision {task['revision']})")
            return

        elif task_type==TaskType.REVIEW.value:
            result=self.reviewer.run(data["draft"])

            print("===============Review agent results=================",result)


            if result["approved"]:
                finish_task(task_id,result)
                print("Draft approved!!!")
                return
            
            if task["revision"]>=MAX_REVIEW:
                failed_task(task["id"])
                print(f" Max revisions reached")
                return
            revision_input = data["draft"] + "\n\n=== FEEDBACK ===\n" + result.get("feedback", "")

            
            create_task(
                plan_id=task["plan_id"],
                task_type=TaskType.WRITE.value,
                input_data={
                    "research_notes": revision_input
                },
                parent_task_id=None,
                revision=task["revision"] + 1
            )
        
            finish_task(task_id,result)
            print(f" Revising.... (attempt: {task['revision'] + 1})")
            return

    def start_process(self,task):
        try:
            self.process(task)
        except Exception as e:
            retry_count=task["retry_count"]
            max_retries=task["max_retries"]

            print("EXCEPTION:",str(e))

            if retry_count<max_retries:
                next_run=exponential_backoff(retry_count)
                update_task_retry(task["id"],next_run)
            else:
                failed_task(task["id"])
                print(f"Failed after {task['max_retries']} retries",str(e))
