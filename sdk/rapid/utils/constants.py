import os
from strenum import StrEnum

TIMEOUT_PERIOD = 30

LAYERS = "LAYERS"
DEFAULT = "default"


def get_layers_from_environment():
    input = os.environ.get(LAYERS, DEFAULT)
    layers = [layer.lower() for layer in input.split(",")]
    return layers


# Dynamically creates the Layer Enum from the environment variables
Layer = StrEnum(
    "Layer", dict([(layer, layer) for layer in get_layers_from_environment()])
)
