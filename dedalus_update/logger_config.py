from loguru import logger
from datetime import datetime
import os
import sys

# Create the logs directory inside state
os.makedirs("state/logs", exist_ok=True)

# Generate a datetime-based log filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = f"state/logs/{timestamp}.log"

# Add file sink with rotation and retention if desired
logger.add(log_file_path, rotation="5 MB", retention="7 days", level="INFO")

# Also log to stdout (for docker logs)
logger.add(sys.stdout, level="INFO")

logger.info(f"Logging to {log_file_path}")