import pytest
from orchestral_tutti_chord_database.color import (
    make_swatches,
    pitch_class_index_to_hue,
)


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


def test_note_to_color():
    assert [
        make_swatches(
            start=midinum_to_hue(i),
            rotations=0,
            numbers=3,
            min_sat=1,
            max_sat=2,
            reverse=True,
            hex=True,
        )[1]
        for i in range(12)
    ] == [
        "#39AC50",
        "#359AB5",
        "#5385D4",
        "#7871DD",
        "#9B61D5",
        "#B557C3",
        "#CF5297",
        "#CC6050",
        "#B77133",
        "#988423",
        "#7F9121",
        "#619E2A",
    ]
