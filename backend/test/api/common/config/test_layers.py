import pytest
from pytest import MonkeyPatch

from api.common.config.layers import LAYERS, get_layers_from_environment


@pytest.mark.parametrize(
    "input, expected",
    [
        ("raw,curated", ["raw", "curated"]),
        ("RAW,CURATED", ["raw", "curated"]),
        ("Raw", ["raw"]),
    ],
)
def test_get_layers_from_environment_with_values(
    monkeypatch: MonkeyPatch, input: str, expected: str
):
    monkeypatch.setenv(LAYERS, input)
    res = get_layers_from_environment()
    assert res == expected


def test_get_layers_from_environment_when_empty(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(LAYERS)
    res = get_layers_from_environment()
    assert res == ["default"]
