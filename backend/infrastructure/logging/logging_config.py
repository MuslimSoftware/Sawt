import logging

def configure_logging():
    """Configure logging to silence verbose libraries and show only application logs."""
    
    # Silence verbose third-party libraries
    logging.getLogger("litellm").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("dspy").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("edge_tts").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set our application loggers to INFO
    app_loggers = [
        "features",
        "infrastructure",
        "main"
    ]
    
    for logger_name in app_loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO) 