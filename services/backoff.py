import time
import random

def exponential_backoff(attempts:int, base_delay:float=1.0):
    delay=base_delay*(2**attempts)
    jitter=random.uniform(0,0.4)
    time.sleep(delay+jitter)

