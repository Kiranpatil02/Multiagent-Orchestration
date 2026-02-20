from services.backoff import exponential_backoff

MAX_RETRIES=3

def retries(func):
    def decorator(*args,**kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args,**kwargs)
            except Exception as e:
                if attempt==MAX_RETRIES-1:
                    raise
                exponential_backoff(attempt)
    return decorator