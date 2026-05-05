import os
import json
import importlib


def pandera_custom_checks_load():
    pandera_files = os.getenv("PANDERA_FILES", None)
    if pandera_files is None:
        return

    pandera_files = json.loads(pandera_files)

    for file in pandera_files:
        file_path = os.path.join("api", "pandera_checks", file)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(pandera_files[file])

        importlib.import_module(file_path.replace("/", ".").replace("\\", ".")[:-3])
