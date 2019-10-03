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
            start=pitch_class_index_to_hue(i),
            rotations=0,
            numbers=3,
            min_sat=1,
            max_sat=2,
            reverse=True,
            hex=True,
        )[1]
        for i in range(12)
    ] == [
        "#CC6050",
        "#B77133",
        "#988423",
        "#7F9121",
        "#619E2A",
        "#39AC50",
        "#359AB5",
        "#5385D4",
        "#7871DD",
        "#9B61D5",
        "#B557C3",
        "#CF5297",
    ]


def test_color_float():
    scheme = make_swatches(
        start=pitch_class_index_to_hue(0),
        rotations=1,
        numbers=3,
        min_sat=1,
        max_sat=2,
        min_light=0.2,
        max_light=0.90,
        reverse=True,
        float=True,
    ).tolist()
    tester = [0.81611328, 0.62227518, 0.23794825]
    assert [
        scheme[i][1] == pytest.approx(tester[i], 0.0000001) for i in range(len(scheme))
    ]


def test_d():
    # print(
    #     make_swatches(
    #         start=pitch_class_index_to_hue(0),
    #         rotations=1,
    #         numbers=21,
    #         min_sat=1,
    #         max_sat=2,
    #         min_light=0.2,
    #         max_light=0.90,
    #         float=True,
    #     )
    # )
    # for i in range(12):
    # print(make_swatches(start=pitch_class_index_to_hue(i), rotations=0.75, numbers=3, min_sat=1, max_sat=2, min_light=0.2, max_light=0.9, float=True)[1])
    # print([tuple(x) for x in make_swatches(start=pitch_class_index_to_hue(2), rotations=0.75, numbers=17, min_sat=1, max_sat=2, min_light=0.2, max_light=0.9,float=True)])
    assert 0
