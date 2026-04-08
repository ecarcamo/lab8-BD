import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock


def load_main_module():
    dotenv_module = ModuleType("dotenv")
    dotenv_module.load_dotenv = MagicMock()
    sys.modules["dotenv"] = dotenv_module

    neo4j_module = ModuleType("neo4j")
    neo4j_module.GraphDatabase = MagicMock()
    sys.modules["neo4j"] = neo4j_module

    if "main" in sys.modules:
        return importlib.reload(sys.modules["main"])
    return importlib.import_module("main")
