class BaseSawtException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ProviderException(BaseSawtException):
    def __init__(self, message: str):
        super().__init__(code="PROVIDER_ERROR", message=message, status_code=500)

class RateLimitException(BaseSawtException):
    def __init__(self, message: str):
        super().__init__(code="RATE_LIMIT_EXCEEDED", message=message, status_code=429)