import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configura il logger root con un formato di base."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
