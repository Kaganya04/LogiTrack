import contextvars
import logging

request_id_var = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Attach the current request id to every log record."""

    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def setup_logging():
    """Send all logitrack.* logs to the console with a request id."""
    logger = logging.getLogger("logitrack")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
