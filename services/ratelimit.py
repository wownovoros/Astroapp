import time
from collections import defaultdict

_REQUESTS = defaultdict(list)


def is_allowed(user_id: int, limit: int = 6, period_seconds: int = 60) -> bool:
    now = time.time()
    valid = [ts for ts in _REQUESTS[user_id] if now - ts < period_seconds]
    _REQUESTS[user_id] = valid
    if len(valid) >= limit:
        return False
    _REQUESTS[user_id].append(now)
    return True
