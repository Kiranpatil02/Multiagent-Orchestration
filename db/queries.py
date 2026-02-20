from db.connect import get_cursor
import uuid
from datetime import datetime
from models.models import TaskType,TaskStatus
import json
con=get_cursor()


def now():
    return datetime.utcnow()

def create_task(**kwargs):
    cur=con.cursor()

    task_id=str(uuid.uuid4())

    cur.execute(
        """
        INSERT INTO tasks(id, plan_id, plan_step_id,parent_task_id, type, status,revision, input_json,retry_count,max_retries,next_run_at, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (task_id,kwargs["plan_id"],kwargs.get("parent_task_id"),kwargs["type"],TaskStatus.PENDING.value,kwargs.get("revision",0), json.dumps(kwargs["input_data"]),0,kwargs.get("max_retries",3), now(),now(),now())
    )

    con.commit()

    return task_id


def claim_task():
    cur=con.cursor()

    task=cur.execute(
        """
        SELECT * FROM tasks WHERE status=? AND next_run_at<=? ORDER BY created_at LIMIT 1
        """,(TaskStatus.PENDING.value,now())
    ).fetchone()

    if not task:
        return None
    
    update_task=cur.execute(
        """
        UPDATE tasks
        SET status=?, updated_at=?
        WHERE id=? AND status=?

        """,(TaskStatus.IN_PROGRESS.value, now(),task["id"], TaskStatus.PENDING.value)
    )

    con.commit()

    if update_task.rowcount==1:
        result=dict(task)
        return result
    return None


def finish_task(task_id:str):
    cur=con.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET status=?, updated_at=?
        WHERE id=?
        """,(TaskStatus.FINISH.value, now(),task_id)
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

