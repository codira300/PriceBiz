from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "pricebiz_http_requests_total",
    "Total number of HTTP requests.",
    ["method", "route", "status"],
)


HTTP_ERRORS_TOTAL = Counter(
    "pricebiz_http_errors_total",
    "Total number of HTTP 4xx and 5xx responses.",
    ["method", "route", "status"],
)


HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "pricebiz_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
)


HEALTH_CHECKS_TOTAL = Counter(
    "pricebiz_health_checks_total",
    "Total number of health and readiness checks.",
    ["check"],
)


HEALTH_CHECK_FAILURES_TOTAL = Counter(
    "pricebiz_health_check_failures_total",
    "Total number of failed health and readiness checks.",
    ["check"],
)


QUEUE_TASKS_SUBMITTED_TOTAL = Counter(
    "pricebiz_queue_tasks_submitted_total",
    "Total number of tasks submitted to the asynchronous task queue.",
    ["task"],
)


QUEUE_TASKS_COMPLETED_TOTAL = Counter(
    "pricebiz_queue_tasks_completed_total",
    "Total number of successfully completed queued tasks.",
    ["task"],
)


QUEUE_TASKS_FAILED_TOTAL = Counter(
    "pricebiz_queue_tasks_failed_total",
    "Total number of failed queued tasks.",
    ["task"],
)


QUEUE_SIZE = Gauge(
    "pricebiz_queue_size",
    "Current number of tasks waiting in the asynchronous task queue.",
)


QUEUE_TASK_DURATION_SECONDS = Histogram(
    "pricebiz_queue_task_duration_seconds",
    "Queued task processing duration in seconds.",
    ["task"],
)


AUTH_EVENTS_TOTAL = Counter(
    "pricebiz_auth_events_total",
    "Total number of authentication and authorization events.",
    ["event"],
)


AUTH_FAILURES_TOTAL = Counter(
    "pricebiz_auth_failures_total",
    "Total number of failed authentication attempts.",
    ["method", "reason"],
)


RATE_LIMIT_EXCEEDED_TOTAL = Counter(
    "pricebiz_rate_limit_exceeded_total",
    "Total number of requests rejected by rate limiting.",
    ["rule"],
)


CACHE_HITS_TOTAL = Counter(
    "pricebiz_cache_hits_total",
    "Total number of cache hits.",
    ["namespace"],
)


CACHE_MISSES_TOTAL = Counter(
    "pricebiz_cache_misses_total",
    "Total number of cache misses.",
    ["namespace"],
)


CACHE_SIZE = Gauge(
    "pricebiz_cache_size",
    "Current number of entries stored in the application cache.",
)