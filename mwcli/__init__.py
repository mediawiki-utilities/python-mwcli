from .streamer import Streamer
from .router import Router
from .about import (__name__, __version__, __author__, __author_email__,
                    __description__, __license__, __url__)

read_json = Streamer.read_json
__all__ = [Router, Streamer, read_json,
           __name__, __version__, __author__, __author_email__,
           __description__, __license__, __url__]

__version__ = "0.0.2"
