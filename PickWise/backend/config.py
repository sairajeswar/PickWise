import os

class Config:
    CACHE_DEFAULT_TTL = int(os.environ.get("CACHE_DEFAULT_TTL", 1800))  # 30 minutes
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 10))  # 10 seconds
    MAX_PRODUCTS = 5
    MIN_PRODUCTS = 2
    RATE_LIMIT_PER_MINUTE = 60
