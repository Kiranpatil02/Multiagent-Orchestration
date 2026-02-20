from db.queries import claim_task
from orchestrator import process_task
import time

def start_worker():
    while True:
        task=claim_task()
        if task:
            process_task(task)
        else:
            time.sleep(1)