import os
import importlib

MODULES = {}

current_dir = os.path.dirname(__file__)

for file in os.listdir(current_dir):
    if file.endswith(".py") and file not in ["__init__.py"]:
        name = file.replace(".py", "")
        MODULES[name] = importlib.import_module(f"indicators.{name}")
