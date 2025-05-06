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
    
    logger = logging.getLogger()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Captura todo, filtramos abajo
    logger.handlers.clear()  # Evita logs duplicados si se llama más de una vez

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        f"[%(asctime)s] - [{color}{action}{COLOR_END} %(levelname)s] - %(message)s",
        "%Y/%m/%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    class LevelFilter(logging.Filter):
        def filter(self, record):
            # Siempre mostrar errores
            if record.levelno >= logging.ERROR:
                return True
            # Si el nivel de debug es INFO o DEBUG, mostramos los menores
            return record.levelno >= debug_level

    handler.addFilter(LevelFilter())
    logger.addHandler(handler)

    logger.debug(f"Logger initialized with level: {debug_level}")

    return logger