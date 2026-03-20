import logging
import sys

def setup_logging(level=logging.INFO):
    """Configure basic logging for the application"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('payroll')
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger
