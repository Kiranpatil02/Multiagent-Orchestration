from db.connect import get_cursor
import uuid
from datetime import datetime,timezone
from models.models import TaskType,TaskStatus
import json
con=get_cursor()


def now():
    return datetime.now(timezone.utc).isoformat()

def create_user_request(query: str):
        cur = con.cursor()
        request_id = str(uuid.uuid4())
        
        cur.execute(
            """
            INSERT INTO user_requests(id, query, status, created_at, updated_at)
            VALUES (?,?,?,?,?)
            """,
            (request_id, query, "PROCESSING", now(), now())
        )
        
        return request_id

def create_plan(request_id:str):
        cur = con.cursor()
        plan_id = str(uuid.uuid4())
        
        cur.execute(
            """
            INSERT INTO plans(id, request_id, status, created_at, updated_at)
            VALUES (?,?,?,?,?)
            """,
            (plan_id, request_id, "ACTIVE", now(), now())
        )
        
        return plan_id


def create_task(plan_id: str, task_type: str, input_data: dict, 
                parent_task_id: str|None=None, revision: int = 0, 
                max_retries: int = 3):
    
    cur=con.cursor()
    task_id=str(uuid.uuid4())

    cur.execute(
        """
        INSERT INTO tasks(id, plan_id,parent_task_id, type, status,revision, input_json,retry_count,max_retries,next_run_at, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
           (task_id, plan_id, parent_task_id, task_type, 
             TaskStatus.PENDING.value, revision, json.dumps(input_data), 
             0, max_retries, now(), now(), now())
    )

    con.commit()

    return task_id


def claim_task():
    cur=con.cursor()

    task=cur.execute(
        """
        SELECT id FROM tasks WHERE status=? AND (next_run_at IS NULL OR next_run_at<=?) ORDER BY created_at LIMIT 1
        """,(TaskStatus.PENDING.value,now())
    ).fetchone()

    if not task:
        return None
    
    task_id = task["id"]
    
    update_task=cur.execute(
        """
        UPDATE tasks
        SET status=?, updated_at=?
        WHERE id=? AND status=?

        """,(TaskStatus.IN_PROGRESS.value, now(),task["id"], TaskStatus.PENDING.value)
    )

    con.commit()

    if update_task.rowcount==1:
        claimed_task = cur.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return dict(claimed_task)
    return None


def finish_task(task_id:str, output_data:dict):
    cur=con.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET status=?, output_json=?, updated_at=?
        WHERE id=?
        """,(TaskStatus.FINISH.value, json.dumps(output_data) if output_data else None, now(),task_id)
    )
    con.commit()


def failed_task(task_id:str):
    cur=con.cursor()

    cur.execute(
        """
        UPDATE tasks SET status='FAILED', updated_at=?
        WHERE id=?

        """,(now(),task_id)
    )

    con.commit()

def update_task_retry(task_id,next_run_at):
    cur=con.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET retry_count=retry_count+1,
            status='PENDING',
            next_run_at=?,
            updated_at=? WHERE id=?

        """,(next_run_at,now(),task_id)
    )

    con.commit()


def get_tasks(plan_id: str, task_type: str):
    cur=con.cursor()
    tasks = cur.execute(
        """
        SELECT * FROM tasks 
        WHERE plan_id = ? AND type = ?
        """,
        (plan_id, task_type)
    ).fetchall()

    return [dict(t) for t in tasks]

def all_research_complete(plan_id: str):
    tasks = get_tasks(plan_id, "RESEARCH")
    if not tasks:
        return False
    return all(t["status"] == TaskStatus.FINISH.value for t in tasks)

def get_all_research_outputs(plan_id: str):
    tasks = get_tasks(plan_id, "RESEARCH")
    outputs = []
    for task in tasks:
        if task["output_json"]:
            data = json.loads(task["output_json"])
            if "research_notes" in data:
                outputs.append(data["research_notes"])
    return outputs