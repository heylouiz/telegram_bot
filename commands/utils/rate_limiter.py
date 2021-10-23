import math
import logging
import time

from functools import wraps


rate_limit_logger = logging.getLogger(__name__)
rate_limit_logger.setLevel(logging.DEBUG)


GCP_TTS_CHAR_LIMIT = math.floor(1000000 / 31 / 24) - 1  # Max chars per hour
RATE_LIMIT = 60 * 60  # 1 hour
used_chars = 0


def rate_limited(max):
    """
    Decorator that makes functions not be called more than `max` times per second.
    """

    # Minimum interval between each call of decorated function
    min_interval = 1.0 / float(max)

    def decorate(func):
        # Initializate first and last time function was called, respectively
        first_time_called = [0.0]
        last_time_called = [0.0]

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            # Time since first and last call, respectively
            elapsed_first = time.perf_counter() - first_time_called[0]
            elapsed_last = time.perf_counter() - last_time_called[0]

            global used_chars

            rate_limit_logger.warning(f"{used_chars}, {round(elapsed_first, 1)}, {round(elapsed_last, 1)}, {round(time.perf_counter(), 1)}, {round(last_time_called[0], 1)}")

            # If char limit was exceeded within the time limit, stop
            if used_chars > GCP_TTS_CHAR_LIMIT and elapsed_first < RATE_LIMIT:
                rate_limit_logger.warning(f'Char limit exceeded within the time limit (used: {used_chars} under {round(elapsed_first, 2)} seconds, max: {GCP_TTS_CHAR_LIMIT} under {RATE_LIMIT} seconds).')
                raise ValueError(f"Char limit exceeded within the time limit.")
            else:
                if elapsed_first >= RATE_LIMIT:  # The time limit has expired,
                    # Reset counters
                    rate_limit_logger.debug(f'More than {RATE_LIMIT} seconds have passed, resetting rate limit counters...')
                    first_time_called[0] = time.perf_counter()
                    used_chars = 0

                # Update when function was last called
                last_time_called[0] = time.perf_counter()

                left_to_wait = min_interval - elapsed_last
                # Too many calls for the given max number of calls per second
                if left_to_wait > 0:
                    rate_limit_logger.warning(f'Rate limit ({max}) exceeded.')
                    raise ValueError(f"Rate limit ({max}) exceeded.")
                    return
                else:
                    # All rate limits have been satisfied, proceed
                    ret = func(*args, **kwargs)

                    return ret

        return rate_limited_function

    return decorate


@rate_limited(max=10)
def print_num(num):
    time.sleep(0.1)
    pass


print("send print requests to decorated function")
for i in range(1, 100):
    try:
        print_num(i)
    except ValueError as e:
        print(e)
    else:
        used_chars += i
