"""
Retry utility for asynchronous functions.
Provides exponential backoff and jitter for handling transient errors.
"""

import asyncio
import random
import functools
from typing import Type, Tuple, Callable, Any
import httpx
from src.utils.logger import logger
from src.config import settings

def async_retry(
    max_retries: int = settings.max_retries,
    base_delay: float = settings.retry_base_delay,
    max_delay: float = settings.retry_max_delay,
    retriable_statuses: Tuple[int, ...] = (500, 502, 503, 504),
    exceptions: Tuple[Type[Exception], ...] = (httpx.TimeoutException, httpx.NetworkError)
):
    """
    Decorator for retrying asynchronous functions with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        retriable_statuses: HTTP status codes that should trigger a retry
        exceptions: Exception types that should trigger a retry
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Determine if the error is retriable
                    is_retriable = False
                    is_rate_limit = False

                    if isinstance(e, httpx.HTTPStatusError):
                        if e.response.status_code == 429:
                            # Rate limit error - special handling with longer delays
                            is_retriable = True
                            is_rate_limit = True
                        elif e.response.status_code in retriable_statuses:
                            is_retriable = True
                    elif isinstance(e, exceptions):
                        is_retriable = True
                    # Also check for RuntimeError that might wrap status errors or contains status code info
                    elif isinstance(e, RuntimeError) and ("429" in str(e) or "rate limit" in str(e).lower()):
                        is_retriable = True
                        is_rate_limit = True

                    # If not retriable or we've exhausted retries, raise the last exception
                    if not is_retriable or attempt == max_retries:
                        if attempt > 0:
                            logger.error(f"Exhausted {max_retries} retries for {func.__name__}. Last error: {str(e)}")
                        raise last_exception

                    # Calculate exponential backoff with longer delays for rate limits
                    if is_rate_limit:
                        # Rate limits need longer waits - use 2x the normal delay
                        delay = min(base_delay * (3 ** attempt), max_delay * 2)
                    else:
                        # Normal exponential backoff: base * 2^attempt
                        delay = min(base_delay * (2 ** attempt), max_delay)

                    # Add jitter: ±10% random variation
                    jitter = random.uniform(-0.1 * delay, 0.1 * delay)
                    sleep_time = max(0, delay + jitter)

                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"in {sleep_time:.2f}s due to {type(e).__name__}: {str(e)}"
                    )

                    await asyncio.sleep(sleep_time)

            # This line should theoretically not be reached due to the raise in the loop
            raise last_exception

        return wrapper
    return decorator
