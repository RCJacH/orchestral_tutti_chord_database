import pytest
from orchestral_tutti_chord_database.color import make_swatches


@pytest.mark.parametrize(
    "params, result",
    [
        pytest.param(
            {"numbers": 5},
            [[0, 0, 0], [68, 72, 7], [133, 138, 52], [195, 199, 134], [255, 255, 255]],
            id="default",
        ),
        pytest.param(
            {"start": 1.5, "rotations": 0, "numbers": 5},
            [[0, 0, 0], [17, 82, 92], [65, 151, 165], [144, 209, 219], [255, 255, 255]],
            id="blue",
        ),
        pytest.param(
            {"start": 2, "rotations": 0, "numbers": 3, "reverse": True},
            [[255, 255, 255], [121, 116, 202], [0, 0, 0]],
            id="reverse",
        ),
    ],
)
def test_make_swatches(params, result):
    assert (make_swatches(**params) == result).all()


def test_make_swatches_hex():
    assert make_swatches(start=2, rotations=0, numbers=3, reverse=True, hex=True) == [
        "#FFFFFF",
        "#7974CA",
        "#000000",
    ]
