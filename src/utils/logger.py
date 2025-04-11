import logging
import os
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logger(name: str = "hospital_llm") -> logging.Logger:
    """Setup and configure the application logger"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Create handlers
    # File handler for JSON logs
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(json_formatter)
    
    # Console handler for human-readable logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 