"""
logger.py — High-visibility telemetry logger with elapsed time profiling.
"""
import time
import sys
from contextlib import contextmanager

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"

def log_info(module: str, message: str):
    print(f"{Color.CYAN}[{module.upper()}]{Color.RESET} {message}")

def log_success(module: str, message: str):
    print(f"{Color.GREEN}[{module.upper()} SUCCESS]{Color.RESET} {message}")

def log_warn(module: str, message: str):
    print(f"{Color.YELLOW}[{module.upper()} WARNING]{Color.RESET} {message}")

def log_error(module: str, message: str):
    print(f"{Color.RED}[{module.upper()} ERROR]{Color.RESET} {message}", file=sys.stderr)

@contextmanager
def log_duration(section_name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000.0
        print(f"{Color.MAGENTA}[TIMING]{Color.RESET} {section_name} finished in {elapsed:.2f} ms")
