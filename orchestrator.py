from models.models import TaskType
from db.queries import *
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent


planner=PlannerAgent()
researcher=ResearchAgent()
writer=WriterAgent()
reviewer=ReviewerAgent()


def process_task(task):

    task_id=task["id"]
    plan_id=task["plan_id"]
    task_type=task["type"]
    input_data=json.loads(task["input_json"])

    if task_type==TaskType.PLAN.value:
        result=planner.execute(input_data)
        agent_output(task_id,"PLANNER",result,"SUCCESS")

        for subtask in result["subtasks"]:
            create_task(plan_id,TaskType.RESEARCH,{"topic":subtask})

    elif task_type==TaskType.RESEARCH.value:
        result=researcher.execute(input_data)

        agent_output(task_id,"RESEARCHER",result,"SUCESS")

        finish_task(task_id)

        con=get_cursor()

        count=con.execute(
            """
            SELECT COUNT(*) as c FROM tasks
            WHERE plan_id=? AND type=? AND status!=?

            """,(plan_id,TaskType.RESEARCH.value,"FINISHED")
        ).fetchone()["c"]

        con.close()

        if count==0:
            create_task(plan_id,TaskType.WRITE,{"plan_id":plan_id})
        return
    
    elif task_type==TaskType.REVIEW.value:
        result=reviewer.execute(input_data)

        agent_output(task_id,"REVIEWER",result,"SUCCESS")

        if result["approved"]:
            plan_completed(plan_id)

    finish_task(task_id)
