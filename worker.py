from db.queries import claim_task
from orchestrator import Orchestrator
from db.connect import get_cursor
import time



def start_worker():
    print("WORKER Started....")

    while True:
        con=get_cursor()
        try:
            task=claim_task()

            if not task:
                time.sleep(1)
                con.close()
                continue

            print(f"Running task: {task["id"]}")

            orchestrator=Orchestrator(con)
            orchestrator.start_process(task)

            print(f"Task {task["id"]} Successfully completed")
        
        except Exception as e:
            print(f"Error:{e}")
        
        finally:
            print("WORKER ENDED...")
            con.close()

if __name__=="__main__":
    start_worker()