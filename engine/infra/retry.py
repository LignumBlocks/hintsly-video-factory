import time
from functools import wraps
import logging

logger = logging.getLogger("hintsly")

def retry(attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == attempts - 1:
                        logger.error(f"Failed after {attempts} attempts: {e}")
                        raise e
                    logger.warning(f"Attempt {i+1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
