from collections import defaultdict
import time
from fastapi import HTTPException

_requests: dict = defaultdict(list)

def check_rate_limit(user_id: str, limit: int = 30, window: int = 60):
    now = time.time()
    _requests[user_id] = [t for t in _requests[user_id] if now - t < window]
    if len(_requests[user_id]) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    _requests[user_id].append(now)
