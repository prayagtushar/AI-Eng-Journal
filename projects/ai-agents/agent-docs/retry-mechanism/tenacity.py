# uv add tenacity
# https://tenacity.readthedocs.io/en/latest/

from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
    retry_if_exeception_type,
    retry_if_not_exception_type,
    retry_if_result,
)


@retry
def unlimited_retries():
    print("Retry forever, does't wait btw retries")
    raise Exception


# @retry(stop=stop_after_attempt(4))
# @retry(stop=stop_after_delay(10))

# Multiple Stop Conditions by using | operator
# @retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))


@retry(wait=wait_fixed(2))
def waitFunction():
    print("Wait 2 sec btw each retry")
    raise Exception


# wait randomly btw 1 or 2 sec btw each retry
# @retry(wait=wait_random(min=1, max=2))


class ClientError(Exception):
    @retry(retry=retry_if_exeception_type(IOError))
    def errorFunction():
        print("Retry forever with no wait if an IOError occurs, raise any other errors")

    raise Exception


@retry(retry=retry_if_not_exception_type(ClientError))
def might_client_error():
    print(
        "Retry forever with no wait if any error other than ClientError occurs. Immediately raise ClientError."
    )
    raise Exception


# Similar Example
# def is_none_p(value):
#     """Return True if value is None"""
#     return value is None

# @retry(retry=retry_if_result(is_none_p))
# def might_return_none():
#     print("Retry with no wait if return value is None")

