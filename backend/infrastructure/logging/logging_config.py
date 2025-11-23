import logging

def list_all_loggers():
    loggers = [name for name in logging.root.manager.loggerDict]
    print("\n🔍 Registered Loggers:")
    for name in sorted(loggers):
        logger = logging.getLogger(name)
        logger.info(f"{name} - level: {logging.getLevelName(logger.level)}")

def configure_logging():
    """Configure logging to silence verbose libraries and show only application logs."""
    
    # Silence verbose third-party libraries
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM Router").setLevel(logging.WARNING)
    logging.getLogger("dspy").setLevel(logging.WARNING)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # list_all_loggers()
