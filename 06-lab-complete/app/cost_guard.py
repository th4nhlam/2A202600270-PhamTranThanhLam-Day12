import time
import logging
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

_in_memory_cost = 0.0
_in_memory_day = time.strftime("%Y-%m-%d")

# Redis client (lazy initialization)
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None and settings.redis_url:
        try:
            import redis
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            _redis_client.ping()
        except Exception:
            _redis_client = False
    return _redis_client

def check_and_record_cost(input_tokens: int, output_tokens: int):
    """Check if the daily budget is exceeded and record the cost."""
    global _in_memory_cost, _in_memory_day
    
    today = time.strftime("%Y-%m-%d")
    cost_to_add = (input_tokens / 1000000) * 0.150 + (output_tokens / 1000000) * 0.600
    
    redis_conn = get_redis()
    if redis_conn:
        try:
            redis_key = f"daily_cost:{today}"
            current_cost = float(redis_conn.get(redis_key) or 0.0)
            
            if current_cost >= settings.daily_budget_usd:
                raise HTTPException(status_code=503, detail="Daily budget exhausted.")
            
            # Use INCRBYFLOAT for atomic updates if possible (though we need to handle key expiration)
            new_cost = redis_conn.incrbyfloat(redis_key, cost_to_add)
            redis_conn.expire(redis_key, 86400 * 2) # keep for 2 days
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis cost guard error: {e}. Falling back to in-memory.")

    # Fallback in-memory
    if today != _in_memory_day:
        _in_memory_cost = 0.0
        _in_memory_day = today
        
    if _in_memory_cost >= settings.daily_budget_usd:
        raise HTTPException(status_code=503, detail="Daily budget exhausted.")
        
    _in_memory_cost += cost_to_add

def get_current_metrics():
    """Return current cost metrics."""
    today = time.strftime("%Y-%m-%d")
    current_cost = 0.0
    
    redis_conn = get_redis()
    if redis_conn:
        try:
            current_cost = float(redis_conn.get(f"daily_cost:{today}") or 0.0)
        except Exception:
            current_cost = _in_memory_cost
    else:
        current_cost = _in_memory_cost
        
    return {
        "daily_cost_usd": round(current_cost, 6),
        "daily_budget_usd": settings.daily_budget_usd,
        "budget_used_pct": round((current_cost / settings.daily_budget_usd) * 100, 2) if settings.daily_budget_usd > 0 else 0
    }
