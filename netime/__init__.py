import logging

logging.root.handlers = []
logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s",
    level=logging.DEBUG,
    filename="debug.log",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger(__name__).addHandler(console)

stream_formatter = logging.Formatter("%(levelname)s: %(message)s")
console.setFormatter(stream_formatter)

logger = logging.getLogger(__name__)
