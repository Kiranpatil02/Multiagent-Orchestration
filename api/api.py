from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.queries import *
from db.init import init_db
from models.models import TaskStatus,TaskType
import json
from fastapi import Request

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

con=get_cursor()


@app.get("/test")
async def check():
    return{
        "status":"Running"
    }

@app.post("/api/tasks")
async def submit_task(req:Request):
    try:
        body = await req.json()

        request = body.get("request")

        if not request:
            raise HTTPException(status_code=400, detail="User query empty")

        if len(request) > 5000:
            raise HTTPException(status_code=400, detail="Query too long (max 5000 chars)")

        request_id = create_user_request(request)
        plan_id = create_plan(request_id)

        create_task(
            plan_id=plan_id,
            task_type=TaskType.PLANNER.value,
            input_data={"query": request}
        )

        return {"request_id": request_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")
    

@app.get("/api/tasks/{request_id}/status")
async def get_status(request_id:str):

    cur=con.cursor()
    try:

        user_request=cur.execute(
            "SELECT * FROM user_requests WHERE id=?",
            (request_id,)
        ).fetchone()

        if not user_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        plan = con.execute(
                "SELECT * FROM plans WHERE request_id = ?",
                (request_id,)
            ).fetchone()

        plan_id=plan["id"]


        tasks = con.execute(
                """SELECT * FROM tasks 
                   WHERE plan_id = ? 
                   ORDER BY created_at""",
                (plan_id,)
            ).fetchall()
        
        tasks_list = [dict(t) for t in tasks]

        response = _build_status_response(user_request, tasks_list)
            
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _build_status_response(user_request, tasks):
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == TaskStatus.FINISH.value)
        failed = sum(1 for t in tasks if t["status"] == TaskStatus.FAILED.value)
        in_progress = sum(1 for t in tasks if t["status"] == TaskStatus.IN_PROGRESS.value)
        pending = sum(1 for t in tasks if t["status"] == TaskStatus.PENDING.value)

        current_agent = None
        for task in reversed(tasks):
            if task["status"] == TaskStatus.IN_PROGRESS.value:
                current_agent = task["type"]
                break

        pipeline = {
            "planner": {
                "status": "pending",
                "output": None
            },
            "research": {
                "status": "pending",
                "total_tasks": 0,
                "completed_tasks": 0,
                "tasks": []
            },
            "writer": {
                "status": "pending",
                "current_revision": 0,
                "output": None
            },
            "reviewer": {
                "status": "pending",
                "feedback": None,
                "approved": None,
                "revision_history": []
            }
        }
    

        outputs=[]

        for task in tasks:
            task_type = task["type"]
            output = json.loads(task["output_json"]) if task["output_json"] else None
            if task_type == TaskType.PLANNER.value:
                pipeline["planner"]["status"] = task["status"].lower()
                if output:
                    pipeline["planner"]["output"] = output
                    outputs.append({
                        "agent": "PLANNER",
                        "timestamp": task["created_at"],
                        "output": output
                    })

            elif task_type == TaskType.RESEARCH.value:
                pipeline["research"]["total_tasks"] += 1
                if task["status"] == TaskStatus.FINISH.value:
                    pipeline["research"]["completed_tasks"] += 1
                
                pipeline["research"]["tasks"].append({
                    "id": task["id"],
                    "status": task["status"].lower(),
                    "output": output
                })
                
                if output:
                    outputs.append({
                        "agent": "RESEARCH",
                        "timestamp": task["created_at"],
                        "output": output
                    })

                if pipeline["research"]["completed_tasks"] == pipeline["research"]["total_tasks"]:
                    pipeline["research"]["status"] = "complete"
                elif task["status"] == TaskStatus.IN_PROGRESS.value:
                    pipeline["research"]["status"] = "in_progress"
                elif pipeline["research"]["completed_tasks"] > 0:
                    pipeline["research"]["status"] = "in_progress"

            elif task_type == TaskType.WRITE.value:
                if task["status"] != TaskStatus.PENDING.value:
                    pipeline["writer"]["status"] = task["status"].lower()
                    pipeline["writer"]["current_revision"] = task["revision"]
                    if output:
                        pipeline["writer"]["output"] = output
                        outputs.append({
                            "agent": "WRITER",
                            "revision": task["revision"],
                            "timestamp": task["created_at"],
                            "output": output
                        })

            elif task_type == TaskType.REVIEW.value:
                if task["status"] != TaskStatus.PENDING.value:
                    pipeline["reviewer"]["status"] = task["status"].lower()
                    
                    if output:
                        pipeline["reviewer"]["approved"] = output.get("approved")
                        pipeline["reviewer"]["feedback"] = output.get("feedback")
                        
                        # Add to revision history
                        pipeline["reviewer"]["revision_history"].append({
                            "revision": task["revision"],
                            "approved": output.get("approved"),
                            "feedback": output.get("feedback"),
                            "timestamp": task["created_at"]
                        })
                        
                        outputs.append({
                            "agent": "REVIEWER",
                            "revision": task["revision"],
                            "timestamp": task["created_at"],
                            "output": output
                        })
            
        is_complete = (completed + failed >= total) and total > 0 

        return {
                "request_id": user_request["id"],
                "query": user_request["query"],
                "is_complete": is_complete,
                "progress": {
                    "percentage": int((completed / total) * 100) if total > 0 else 0,
                    "total_tasks": total,
                    "completed": completed,
                    "in_progress": in_progress,
                    "pending": pending,
                    "failed": failed
                },
                "current_agent": current_agent,
                "pipeline": pipeline,
                "all_outputs": outputs
            }
