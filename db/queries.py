from db.connect import get_cursor
import uuid
from datetime import datetime
from models.models import AgentOutput,Plan,PlanStatus,Task,Request,Status,TaskType,TaskStatus
import json
con=get_cursor()

def create_request(user_query:str):
    cur=con.cursor()
    current_time=datetime.now()
    req_id = str(uuid.uuid4())
    res=cur.execute(
        """
        INSERT INTO requests (id,user_query,status,plain_id,created_at,updated_at)
        VALUES (?,?,?,?,?,?)
        """,(req_id,user_query,Status.RECEIVED,current_time,current_time),
        )
    con.commit()

    return res

def update_requset_status(request_id: str,status: Status, plan_id: str | None = None):
    cur=con.cursor()
    cur.execute(
    """
    UPDATE requests
    SET status=?, plan_id=COALESCE(?, plan_id), updated_at=?
    WHERE  id=?

    """,(Status.value,plan_id,request_id))
    con.commit()


def create_plan(request_id:str):
    cur=con.cursor()
    current_time=datetime.now()
    plan_id=str(uuid.uuid4())
    cur.execute(
    """
    INSERT INTO plans(id,request_id,status,created_at,updated_at)
    VALUES (?,?,?,?,?)

    """,(
        plan_id, request_id,PlanStatus.ACTIVE.value,
        current_time,current_time
        )
    )

    con.commit()
    return plan_id

def plan_completed(plan_id:str):
    cur=con.cursor()
    current_time=datetime.now()

    cur.execute(
        """
        UPDATE plans
        SET status=?,completed_at=?,updated_at=?
        WHERE id=?
        """,(PlanStatus.COMPLETED.value,current_time,current_time,plan_id)
    )
    con.commit()


def create_task(plan_id:str,task_type:TaskType,input_data:dict):
    cur=con.cursor()
    current_time=datetime.now()

    task_id=str(uuid.uuid4())

    cur.execute(
        """
        INSERT INTO tasks(id, plan_id, type, status, input_json, created_at, updated_at)
        """,(task_id,plan_id,task_type.value,TaskStatus.PENDING.value,json.dumps(input_data),current_time,current_time)
    )

    con.commit()

    return task_id


def claim_task():
    cur=con.cursor()
    current_time=datetime.now()

    task=cur.execute(
        """
        SELECT * FROM tasks WHERE status=? ORDER BY created_at LIMIT 1
        """,(TaskStatus.PENDING.value)
    ).fetchone()

    if not task:
        return None
    
    update_task=cur.execute(
        """
        UPDATE tasks
        SET status=?, updated_at=?
        WHERE id=? AND status=?

        """,(TaskStatus.IN_PROGRESS.value, current_time,task["id"], TaskStatus.PENDING.value)
    )

    con.commit()

    if update_task.rowcount==1:
        result=dict(task)
        return result
    con.close()
    return None


def finish_task(task_id:str):
    cur=con.cursor()
    current_time=datetime.now()

    cur.execute(
        """
        UPDATE tasks
        SET status=?, updated_at=?
        WHERE id=?
        """,(TaskStatus.FINISH.value, current_time,task_id)
    )
    con.commit()
    con.close()


def agent_output(task_id:str,agent_type:str,payload:dict,status:str):
    cur=con.cursor()
    id=str(uuid.uuid4())
    current_time=datetime.now()

    cur.execute(
        """
        INSERT INTO agent_outputs(id, task_id, agent_type, status, payload_json,created_at)
        VALUES(?,?,?,?,?,?)

        """,(id,task_id,agent_type,status,json.dumps(payload),current_time)
    )
    con.commit()
    con.close()



def _row_to_plan(row):
    return Plan(
        id      = row["id"],
        request_id= row["request_id"],
        status= PlanStatus(row["status"]),
        user_query= row["user_query"],
        max_revision=  row["max_revisions"],
        current_revision=row["current_revision"],
        version        = row["version"],
        # created_at     = _req_dt(row["created_at"]),
        # updated_at     = _req_dt(row["updated_at"]),
        # completed_at   = _dt(row["completed_at"]),
    )




