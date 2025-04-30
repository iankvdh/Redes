import logging

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
COLOR_END = "\033[0m"

def initialize_logger(debug_level, action):
    color = BLUE
    if action == "upload":
        color = GREEN
    elif action == "download":
        color = YELLOW

    logging.basicConfig(
        level=debug_level,
        format=f"[%(asctime)s] - [{color}{action}{COLOR_END} %(levelname)s] - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    logging.debug(f"Logger initialized with level: {debug_level}")
    
    logger = logging.getLogger()

    return logger