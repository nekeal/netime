import logging
from logging.handlers import SysLogHandler
logger = logging.getLogger(__name__)

logging.root.handlers = []
logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s",
    level=logging.DEBUG,
    filename="debug.log",
)
main_formatter = logging.Formatter("%(levelname)s: %(message)s")

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(main_formatter)
logger.addHandler(console)

_syslog_handler = SysLogHandler(address="/dev/log")
_syslog_handler.setFormatter(main_formatter)
logger.addHandler(_syslog_handler)


