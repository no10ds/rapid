from strenum import StrEnum
import os


LAYERS = "LAYERS"
DEFAULT = "default"


def get_layers_from_environment():
    """
    Fetches the layers from the environment variables passed by the user. Will be set to 'default' if none are passed
    """
    input = os.environ.get(LAYERS, DEFAULT)
    layers = [layer.lower() for layer in input.split(",")]
    return layers


# Dynamically creates the Layer Enum from the environment variables
Layer = StrEnum(
    "Layer", dict([(layer, layer) for layer in get_layers_from_environment()])
)
