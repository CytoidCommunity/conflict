from typing import Any, Dict, Optional

from conflict.schema.config import Config

config: Optional[Config] = None


def load_conf(conf_dict: Dict[str, Any]):
    global config
    config = Config(**conf_dict)
