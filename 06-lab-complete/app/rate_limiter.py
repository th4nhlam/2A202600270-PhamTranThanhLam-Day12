import time
import logging
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory store
from collections import defaultdict, deque
_in_memory_windows: dict[str, deque] = defaultdict(deque)

# Redis client (lazy initialization)
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None and settings.redis_url:
        try:
            import redis
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            _redis_client.ping()
            logger.info("Connected to Redis for rate limiting")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to in-memory.")
            _redis_client = False # Disable redis
    return _redis_client

def check_rate_limit(key: str):
    """
    Check if the request rate for the given key exceeds the limit.
    Uses Redis if available, otherwise falls back to in-memory sliding window.
    """
    now = time.time()
    limit = settings.rate_limit_per_minute
    
    redis_conn = get_redis()
    
    if redis_conn:
        try:
            pipe = redis_conn.pipeline()
            redis_key = f"rate_limit:{key}"
            # Remove old entries
            pipe.zremrangebyscore(redis_key, 0, now - 60)
            # Add current entry
            pipe.zadd(redis_key, {str(now): now})
            # Count entries in the last 60s
            pipe.zcard(redis_key)
            # Set expiry to clean up old keys
            pipe.expire(redis_key, 60)
            
            _, _, count, _ = pipe.execute()
            
            if count > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} req/min",
                    headers={"Retry-After": "60"},
                )
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}. Falling back to in-memory.")
            # Continue to in-memory fallback
            
    # In-memory falling back
    window = _in_memory_windows[key]
    while window and window[0] < now - 60:
        window.popleft()
        
    if len(window) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} req/min",
            headers={"Retry-After": "60"},
        )
    
    window.append(now)
