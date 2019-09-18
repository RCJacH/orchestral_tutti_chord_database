import pytest
from orchestral_tutti_chord_database import pitch


class TestAccidentalIndex:
    def test_empty_input(self):
        assert pitch.get_accidental_index("") == 0

    def test_sharp(self):
        assert pitch.get_accidental_index("#") == 1
        assert pitch.get_accidental_index("##") == 2

    def test_flat(self):
        assert pitch.get_accidental_index("b") == -1
        assert pitch.get_accidental_index("bbb") == -3

    def test_double_sharp(self):
        assert pitch.get_accidental_index("x") == 2

    def test_combined(self):
        assert pitch.get_accidental_index("x#") == 3
        assert pitch.get_accidental_index("#b") == 0

    def test_others_type(self):
        assert pitch.get_accidental_index(None) == 0
        assert pitch.get_accidental_index(9) == 0

    def test_string_with_no_accidental(self):
        with pytest.raises(ValueError, match="Error in accidental"):
            pitch.get_accidental_index("0")

    def test_nonsense_with_accidental(self):
        with pytest.raises(ValueError, match="Error in accidental"):
            pitch.get_accidental_index("Czb#aAr")


class TestPitchClass:
    pass


class TestPitchProperties:
    def test_empty_input(self):
        with pytest.raises(IndexError):
            pitch.get_properties("")

    def test_no_pitch_class(self):
        with pytest.raises(ValueError, match="No pitch class"):
            pitch.get_properties("#b")

    def test_C(self):
        assert pitch.get_properties("C") == {
            "name": "C",
            "class": "C",
            "class_index": 0,
            "index": 0,
            "accidental": "",
            "accidental_index": 0,
        }

    def test_G_sharp(self):
        assert pitch.get_properties("G#") == {
            "name": "G#",
            "class": "G",
            "class_index": 4,
            "index": 8,
            "accidental": "#",
            "accidental_index": 1,
        }

    def test_F_double_flat(self):
        assert pitch.get_properties("Fbb") == {
            "name": "Fbb",
            "class": "F",
            "class_index": 3,
            "index": 3,
            "accidental": "bb",
            "accidental_index": -2,
        }


def test_get_midinum():
    assert pitch.get_midinum("C", 0) == 0
    assert pitch.get_midinum("G", 0) == 7
    assert pitch.get_midinum("D", 4) == 50
    assert pitch.get_midinum("Bb", 5) == 70


class TestInterval:
    class TestSingleInterval:
        def test_natural_major_seconds(self):
            assert (
                pitch.detect_interval("C", "D")
                == pitch.detect_interval("D", "E")
                == pitch.detect_interval("F", "G")
                == pitch.detect_interval("G", "A")
                == pitch.detect_interval("A", "B")
                == (2, 0)
            )

        def test_natural_major_thirds(self):
            assert (
                pitch.detect_interval("C", "E")
                == pitch.detect_interval("F", "A")
                == pitch.detect_interval("G", "B")
                == (3, 0)
            )

        def test_natural_major_six(self):
            assert (
                pitch.detect_interval("C", "A")
                == pitch.detect_interval("D", "B")
                == pitch.detect_interval("F", "D")
                == pitch.detect_interval("G", "E")
                == (6, 0)
            )

        def test_natural_major_seven(self):
            assert (
                pitch.detect_interval("C", "B")
                == pitch.detect_interval("F", "E")
                == (7, 0)
            )

        def test_accidental(self):
            assert pitch.detect_interval("C#", "B") == (7, -1)
            assert pitch.detect_interval("C#", "Bb") == (7, -2)
            assert pitch.detect_interval("G", "Eb") == (6, -1)
            assert pitch.detect_interval("A", "C#") == (3, 0)

    class TestIntervals:
        def test_Major_Root(self):
            assert (
                pitch.get_intervals(["C", "E", "G"])
                == pitch.get_intervals(["E", "G#", "B"])
                == [(3, 0), (3, -1)]
            )

        def test_Minor_Root(self):
            assert (
                pitch.get_intervals(["C", "Eb", "G"])
                == pitch.get_intervals(["A", "C", "E"])
                == [(3, -1), (3, 0)]
            )

        def test_Major_1st_inversion(self):
            assert (
                pitch.get_intervals(["F#", "A", "D"])
                == pitch.get_intervals(["A#", "C#", "F#"])
                == [(3, -1), (4, 0)]
            )

        def test_Minor_1st_inversion(self):
            assert (
                pitch.get_intervals(["Bb", "D", "G"])
                == pitch.get_intervals(["Ab", "C", "F"])
                == [(3, 0), (4, 0)]
            )

        def test_Major_2nd_inversion(self):
            assert (
                pitch.get_intervals(["Bb", "Eb", "G"])
                == pitch.get_intervals(["G#", "C#", "E#"])
                == [(4, 0), (3, 0)]
            )

        def test_Minor_2nd_inversion(self):
            assert (
                pitch.get_intervals(["Eb", "Ab", "Cb"])
                == pitch.get_intervals(["D#", "G#", "B"])
                == [(4, 0), (3, -1)]
            )

        def test_seventh(self):
            assert pitch.get_intervals(["C", "Eb", "G", "Bb"]) == [
                (3, -1),
                (3, 0),
                (3, -1),
            ]

        def test_from_root(self):
            assert pitch.get_intervals(["C", "A", "D#", "G#"], from_root="C") == [
                (6, 0),
                (2, 1),
                (5, 1),
            ]


class TestInversion:
    class TestTriad:
        def test_triad_root(self):
            assert pitch.identify_inversion([(3, 0), (3, -1)]) == 0
            assert pitch.identify_inversion([(3, -1), (3, -2)]) == 0

        def test_triad_inversion(self):
            assert pitch.identify_inversion([[x] for x in (3, 4)]) == 2
            assert pitch.identify_inversion([[x] for x in (4, 3)]) == 1

        def test_seventh_root_no3(self):
            assert pitch.identify_inversion([[x] for x in (3, 5)]) == 0

        def test_seventh_root_no5(self):
            assert pitch.identify_inversion([[x] for x in (5, 3)]) == 0

        def test_seventh_inversion_no5(self):
            assert pitch.identify_inversion([[x] for x in (5, 2)]) == 2
            assert pitch.identify_inversion([[x] for x in (2, 3)]) == 1

        def test_seventh_inversion_no3(self):
            assert pitch.identify_inversion([[x] for x in (3, 2)]) == 2
            assert pitch.identify_inversion([[x] for x in (2, 5)]) == 1

        def test_ambiguous(self):
            assert pitch.identify_inversion([[4] * 2]) == None
            assert pitch.identify_inversion([[2], [4]]) == None
            assert pitch.identify_inversion([[4], [2]]) == None

    class TestSeventh:
        def test_root(self):
            assert pitch.identify_inversion([[x] for x in (3, 3, 3)]) == 0

        def test_1st_inversion(self):
            assert pitch.identify_inversion([[x] for x in (3, 3, 2)]) == 3

        def test_2nd_inversion(self):
            assert pitch.identify_inversion([[x] for x in (3, 2, 3)]) == 2

        def test_3rd_inversion(self):
            assert pitch.identify_inversion([[x] for x in (2, 3, 3)]) == 1

        def test_ambiguous(self):
            assert pitch.identify_inversion([[x] for x in {2, 4, 4}]) == None
            assert pitch.identify_inversion([[x] for x in {4, 2, 4}]) == None


class TestChordDetection:
    class TestRootDetection:
        def test_C_triad_root(self):
            assert pitch.detect_root([[x] for x in ("C", "E", "G")]) == "C"

        def test_C_triad_open(self):
            assert pitch.detect_root([[x] for x in ("C", "G", "E")]) == "C"

        def test_C_triad_inversions(self):
            assert pitch.detect_root([[x] for x in ("E", "G", "C")]) == "C"
            assert pitch.detect_root([[x] for x in ("E", "C", "G")]) == "C"

        def test_other_triad_root(self):
            assert pitch.detect_root([[x] for x in ("D", "F#", "A")]) == "D"
            assert pitch.detect_root([[x] for x in ("F#", "A", "C#")]) == "F#"
            assert pitch.detect_root([[x] for x in ("Ab", "C", "E")]) == "Ab"

        def test_other_triad_inversions(self):
            assert pitch.detect_root([[x] for x in ("Eb", "Ab", "C")]) == "Ab"
            assert pitch.detect_root([[x] for x in ("E#", "C#", "G#")]) == "C#"

        def test_seventh_inversions(self):
            assert pitch.detect_root([[x] for x in ("Eb", "Ab", "C", "G")]) == "Ab"
            assert pitch.detect_root([[x] for x in ("F", "Bb", "Db", "Ab")]) == "Bb"
            assert pitch.detect_root([[x] for x in ("G", "Db", "Bb", "F")]) == "G"

        def test_ambiguous(self):
            assert pitch.detect_root([("C", 0), ("A", 9), ("D", 14), ("G", 19)]) == "C"

    class TestChordName:
        @pytest.mark.parametrize(
            "intervals, name",
            [
                pytest.param([[], [], [0], [], [0], [], []], "", id="Major"),
                pytest.param([[], [], [-1], [], [0], [], []], "m", id="Minor"),
                pytest.param([[], [], [-1], [], [-1], [], []], "o", id="Diminished"),
                pytest.param([[], [], [0], [], [1], [], []], "+", id="Augmented"),
                pytest.param([[], [0], [], [], [0], [], []], "sus2", id="Sus2"),
                pytest.param([[], [], [], [0], [0], [], []], "sus", id="Sus4"),
                pytest.param([[], [0], [], [0], [0], [], []], "sus24", id="Sus24"),
            ],
        )
        def test_triad(self, intervals, name):
            assert pitch.gen_chord_name(5, intervals) == name

        @pytest.mark.parametrize(
            "intervals, name",
            [
                pytest.param([[], [], [0], [], [0], [], [0]], "Maj7", id="Major7"),
                pytest.param([[], [], [-1], [], [0], [], [-1]], "m7", id="Minor7"),
                pytest.param([[], [], [0], [], [0], [], [-1]], "7", id="Dominant7"),
                pytest.param([[], [], [-1], [], [-1], [], [-1]], "m7b5", id="Minor7b5"),
                pytest.param(
                    [[], [], [-1], [], [-1], [], [-2]], "o7", id="Diminished7"
                ),
                pytest.param([[], [], [0], [], [1], [], [0]], "Maj7+", id="Major7+"),
                pytest.param(
                    [[], [], [0], [], [-1], [], [-1]], "7b5", id="Dominant7b5"
                ),
                pytest.param([[], [], [0], [], [1], [], [-1]], "7+", id="Dominant7#5"),
                pytest.param(
                    [[], [], [], [0], [0], [], [-1]], "7sus", id="Dominant7sus"
                ),
                pytest.param(
                    [[], [0], [], [], [-1], [], [-1]], "7sus2b5", id="Dominant7sus2b5"
                ),
            ],
        )
        def test_quatrad(self, intervals, name):
            assert pitch.gen_chord_name(7, intervals) == name

        @pytest.mark.parametrize(
            "extension, intervals, name",
            [
                pytest.param(
                    13, [[], [0], [0], [1], [0], [0], [0]], "Maj13lyd", id="Major13#11"
                ),
                pytest.param(
                    11, [[], [0], [-1], [0], [0], [], [-1]], "m11", id="Minor11"
                ),
                pytest.param(9, [[], [0], [0], [], [0], [], [-1]], "9", id="Dominant9"),
                pytest.param(
                    13, [[], [0], [0], [], [0], [0], [-1]], "13", id="Dominant13"
                ),
                pytest.param(
                    7, [[], [-1], [0], [], [0], [], [-1]], "7b9", id="Dominant7b9"
                ),
                pytest.param(
                    13, [[], [0], [0], [1], [0], [0], [-1]], "13lyd", id="Dominant13#11"
                ),
                pytest.param(
                    9, [[], [0], [0], [], [0], [-1], [-1]], "9b13", id="Dominant9b13"
                ),
                pytest.param(
                    7,
                    [[], [1], [0], [], [0], [-1], [-1]],
                    "7#9b13",
                    id="Dominant7#9b13",
                ),
                pytest.param(
                    7,
                    [[], [-1, 1], [0], [], [-1, 1], [], [-1]],
                    "7alt",
                    id="Dominant7alt",
                ),
            ],
        )
        def test_Extension(self, extension, intervals, name):
            assert pitch.gen_chord_name(extension, intervals) == name

        # def test_Edge_Cases(self, extension, intervals, name):
        # pass

    def test_empty_list(self):
        with pytest.raises(IndexError):
            assert pitch.detect_chord([])

    def test_major(self):
        assert pitch.detect_chord([("C", 0), ("G", 7), ("E", 16)]) == "C"
        assert pitch.detect_chord([("E", 28), ("C#", 61), ("A", 9)]) == "A"

    def test_minor(self):
        assert pitch.detect_chord([("C", 0), ("G", 7), ("Eb", 16)]) == "Cm"
        assert pitch.detect_chord([("F#", 42), ("B", 35), ("D", 38)]) == "Bm"
