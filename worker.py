from db.queries import claim_task
from db.init import init_db
from orchestrator import Orchestrator
from db.connect import get_cursor
import time
import signal


shutdown = False
def signal_handler(sig, frame):
    global shutdown
    print("Shutting down workers")
    shutdown = True


def start_worker():
    print("WORKER Started....")

    signal.signal(signal.SIGINT,signal_handler)
    signal.signal(signal.SIGTERM,signal_handler)
    con=get_cursor()
    orchestrator=Orchestrator(con)

    while not shutdown:
        try:
            task=claim_task()

            if not task:
                time.sleep(1)
                continue

            print(f"Running task: {task["id"]}")
            orchestrator.start_process(task)

        except Exception as e:
            print(f"Error:{e}")
 
    print("WORKER STOPPED")


# if __name__=="__main__":
#     init_db()
#     start_worker()