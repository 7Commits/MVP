import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a basic format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

