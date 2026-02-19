from db.connect import get_cursor
import uuid
from datetime import datetime, timezone
from models.models import AgentOutput,Plan,PlanStatus,Task,Request,Status,TaskType,TaskStatus

con=get_cursor()

def create_request(user_query:str):
    cur=con.cursor()
    current_time=datetime.now()
    req=Request(
        id= str(uuid.uuid4()),
        user_query=user_query,
        status=Status.RECEIVED,
        plan_id=None,
        created_at=current_time,
        updated_at=current_time,
    )
    cur.execute(
        """
        INSERT INTO requests (id,user_query,status,plain_id,created_at,updated_at)
        VALUES (?,?,?,?,?,?)
        """,(req.id,req.user_query,req.status,req.plan_id,current_time,current_time),
        )
    con.commit()

    return req

def update_requset_status(request_id: str,status: Status, plan_id: str | None = None):
    cur=con.cursor()
    cur.execute(
    """
    UPDATE requests
    SET status=?, plan_id=COALESCE(?, plan_id), updated_at=?
    WHERE  id=?

    """,(Status.value,plan_id,request_id))
    con.commit()


def create_plan(request_id:str,user_request:str,max_revision:int=3):
    cur=con.cursor()
    current_time=datetime.now()

    plan=Plan(
        id=str(uuid.uuid4()),
        request_id=request_id,
        status=PlanStatus.ACTIVE,
        user_query=user_request,
        max_revision=max_revision,
        current_revision=0,
        version=1,
        created_at=current_time,
        updated_at=current_time,
        completed_at=current_time
    )
    cur.execute(
    """
    INSERT INTO plans(id,request_id,status,user_query,max_revision,current_revision
                      version,created_at,updated_at)
    VALUES (?,?,?,?,?,?,?,?,?)

    """,(
        plan.id, plan.request_id,plan.status,plan.user_query,plan.max_revision,plan.current_revision,plan.version,
        current_time,current_time
        )
    )

    con.commit()
    return plan


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

def get_active_plans():
    cur=con.cursor()
    res=cur.execute(
        """
        SELECT * FROM plans WHERE status="ACTIVE" ORDER BY created_at
        """
    ).fetchall()

    return [_row_to_plan(res) for r in res]


def update_plan_status(plan_id: str, status: PlanStatus):
    cur=con.cursor()

    curr_time=datetime.now()

    if status == PlanStatus.COMPLETED or status == PlanStatus.FAILED or status == PlanStatus.CANCELLED:
        completed_at = curr_time
    else:
        completed_at = None

    cur.execute(
        """
        UPDATE plans
        SET status =?,
            updated_at=?,
            completed_at=COALESCE(?,completed_at),
            version=version+1
        WHERE id=?
        """,(status.value,curr_time,completed_at, plan_id)
    )

    con.commit()

def increase_revision_count(plan_id: str):
    cur=con.cursor()
    curr_time= datetime.now() 

    cur.execute(
        """
        UPDATE plans
        SET current_revision = current_revision + 1,
            updated_at= ?,
            version= version + 1
        WHERE id = ?
        """,
        (curr_time, plan_id),
    )
    con.commit()

    res = cur.execute(
        "SELECT current_revision FROM plans WHERE id = ?", (plan_id,)
    ).fetchone()
    return res["current_revision"]


def create_task(plan_id,task_type:TaskType,input_data:dict,priority:int=5,max_retries:int=3):

    cur=con.cursor()
    current_time=datetime.now()
    task=Task(
        id=str(uuid.uuid4()),
        plan_id= plan_id,
        type= task_type,
        status= TaskStatus.PENDING,
        priority= priority,
        assigned_agent = None,
        retry_count = 0,
        max_retries= max_retries,
        version = 1,
        created_at = current_time,
        updated_at = current_time,
    )
    #TODO: dependencies on other tasks
    cur.execute(
        """
        INSERT INTO tasks
        (id,plan_id,type,status,priority,retry_count,max_retries,version,created_at,updated_at)
        VALUES()

        """,(task.id,task.plan_id,task.type,task.status,task.priority,)
    )
    con.commit()

    return task

def get_all_tasks(plan_id: str):
    cur=con.cursor()

    res=cur.execute(
        """
        SELECT * FROM tasks WHERE plan_id = ? ORDER BY created_at
        """, (plan_id,)
    ).fetchall()
    return # serialise

def update_task_status( task_id: str,task_status: TaskStatus, current_version: int,assigned_agent: str | None = None,) :
    cur=con.cursor()
    current_time=datetime.now()

    res=cur.execute(
        """
        UPDATE tasks
        SET  status=?,
            assigned_agent=COALESCE(?,assigned_agent),
            version=version+1,
            updated_at=?
        WHERE id=? AND version=?
        """,(task_status.value,assigned_agent,current_time,task_id,current_version)
    )
    con.commit()
    return res.rowcount==1

def plan_complete(plan_id:str):
    tasks=get_all_tasks(plan_id)
    terminal_state={TaskStatus.FINISH}

    return all(t.status in terminal_state for t in tasks) and len(tasks) > 0





