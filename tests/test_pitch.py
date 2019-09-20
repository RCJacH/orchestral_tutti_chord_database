import pytest
from orchestral_tutti_chord_database import pitch
from orchestral_tutti_chord_database.pitch import Pitch, Interval


class TestAccidental:
    @pytest.mark.parametrize(
        "s, x",
        [
            pytest.param("", 0, id="empty"),
            pytest.param(["#", "##"], [1, 2], id="sharp"),
            pytest.param(["b", "bbb"], [-1, -3], id="flat"),
            pytest.param("x", 2, id="double_sharp"),
            pytest.param(["x#", "#b"], [3, 0], id="combined"),
            pytest.param([None, 9], [0, 0], id="other_type"),
        ],
    )
    def test_accidental_index(self, s, x):
        try:
            for s1, x1 in zip(s, x):
                assert pitch.get_accidental_index(s1) == x1
        except TypeError:
            assert pitch.get_accidental_index(s) == x

    @pytest.mark.parametrize(
        "s, error, match",
        [
            pytest.param("0", ValueError, "Error in accidental", id="no_accidental"),
            pytest.param("Czb#aAr", ValueError, "Error in accidental", id="non_sense"),
        ],
    )
    def test_accidental_edge(self, s, error, match):
        with pytest.raises(error, match=match):
            pitch.get_accidental_index(s)

    @pytest.mark.parametrize(
        "i, s",
        [
            pytest.param(0, "", id="neutral"),
            pytest.param(1, "#", id="sharp"),
            pytest.param(-1, "b", id="flat"),
            pytest.param(2, "x", id="double sharp"),
            pytest.param(-2, "bb", id="double flat"),
            pytest.param(3, "x#", id="triple sharp"),
            pytest.param(-3, "bbb", id="triple flat"),
        ],
    )
    def test_accidental(self, i, s):
        assert pitch.get_accidental(i) == s


class TestPitchClass:
    def test_empty_input(self):
        with pytest.raises(IndexError):
            Pitch("")

    def test_no_pitch_class(self):
        with pytest.raises(ValueError, match="No pitch class"):
            Pitch("#b")

    @pytest.mark.parametrize(
        "pit, keys",
        [
            pytest.param("C", ["C", 0, "C", 0, "", 0], id="C"),
            pytest.param("G#", ["G#", 8, "G", 4, "#", 1], id="G#"),
            pytest.param("Fbb", ["Fbb", 3, "F", 3, "bb", -2], id="Fbb"),
            pytest.param("E#b", ["E#b", 4, "E", 2, "#b", 0], id="E#b_neutralize"),
            pytest.param("H", ["A", 9, "A", 5, "", 0], id="H==A"),
            pytest.param("Pb", ["Bb", 10, "B", 6, "b", -1], id="Pb==Bb"),
        ],
    )
    def test_single_pitch(self, pit, keys):
        obj = Pitch(pit)
        assert obj.name == keys[0]
        assert obj.index == keys[1]
        assert obj.pitch_class == keys[2]
        assert obj.pitch_class_index == keys[3]
        assert obj.accidental == keys[4]
        assert obj.accidental_index == keys[5]

    @pytest.mark.parametrize(
        "s, i, midi",
        [
            pytest.param("C", 0, 0, id="C0"),
            pytest.param("G", 0, 7, id="G0"),
            pytest.param("D", 4, 50, id="D4"),
            pytest.param("Bb", 5, 70, id="Bb5"),
            pytest.param("F#4", None, 54, id="F#4_direct"),
            pytest.param("Cb5", 3, 59, id="Cb5_direct_with_octave"),
        ],
    )
    def test_midinum(self, s, i, midi):
        assert Pitch(s, i).midinum == midi

    def test_midinum_default_octave(self):
        assert Pitch("G#").midinum == 56

    @pytest.mark.parametrize(
        "pit, enharmonics",
        [
            pytest.param("C", ["C", "B#", "Dbb"], id="C_enharmonics"),
            pytest.param("F#", ["F#", "Gb", "Ex"], id="F#_enharmonics"),
            pytest.param("E#", ["E#", "F", "Gbb"], id="E#_enharmonics"),
            pytest.param("Ab", ["Ab", "G#"], id="Ab_enharmonics"),
        ],
    )
    def test_enharmonics(self, pit, enharmonics):
        obj = Pitch(pit)
        assert obj.enharmonics() == enharmonics

    @pytest.mark.parametrize(
        "base, other",
        [
            pytest.param("C", "B#", id="C==B#"),
            pytest.param("F#", "Gb", id="F#==Gb"),
            pytest.param("E#", "F", id="E#==F"),
            pytest.param("G", "Abb", id="G==Abb"),
        ],
    )
    def test__eq__(self, base, other):
        assert Pitch(base) == Pitch(other)
        assert not Pitch(base) != Pitch(other)

    @pytest.mark.parametrize(
        "base, interval, result",
        [
            pytest.param("C", "b3", "Eb", id="C_tranpose_to_Eb"),
            pytest.param("A", "5", "E", id="A_transpose_to_E"),
            pytest.param("Db", "#2", "E", id="Db_transpose_to_E"),
            pytest.param("B#", "b2", "C#", id="B#_transpose_to_C#"),
            pytest.param("C", "-2", "Bb", id="C_transpose_down_to_Bb"),
            pytest.param("Db", "-b4", "A#", id="Db_transpose_down_to_A#"),
        ],
    )
    def test_transpose(self, base, interval, result):
        assert Pitch(base).transpose(interval) == Pitch(result)


class TestIntervalClass:
    @pytest.mark.parametrize("numbers", [(1, 0), (2, -1), (4, 1), (5, -1), (7, -2)])
    def test_direct_init(self, numbers):
        assert Interval(*numbers).values() == numbers

    @pytest.mark.parametrize(
        "pairs, result",
        [
            pytest.param(
                [("C", "D"), ("D", "E"), ("F", "G"), ("G", "A"), ("A", "B")],
                (2, 0),
                id="natural_j2",
            ),
            pytest.param([("C", "E"), ("F", "A"), ("G", "B")], (3, 0), id="natural_j3"),
            pytest.param(
                [("C", "A"), ("D", "B"), ("F", "D"), ("G", "E")],
                (6, 0),
                id="natural_j6",
            ),
            pytest.param([("C", "B"), ("F", "E")], (7, 0), id="natural_j7"),
            pytest.param(
                [("C#", "B"), ("D#", "C#"), ("Fb", "Ebb")], (7, -1), id="accidental_b7"
            ),
            pytest.param(
                [("C#", "Bb"), ("D#", "C"), ("F", "Ebb"), ("A", "Gb"), ("B#", "A")],
                (7, -2),
                id="accidental_bb7",
            ),
            pytest.param(
                [("G", "Eb"), ("Bb", "Gb"), ("C#", "A"), ("Dx", "B#")],
                (6, -1),
                id="accidental_m6",
            ),
            pytest.param(
                [("A", "C#"), ("Bb", "D"), ("Db", "F"), ("E", "G#")],
                (3, 0),
                id="accidental_j3",
            ),
        ],
    )
    def test_single_interval(self, pairs, result):
        for each in pairs:
            assert Interval(*each).values() == result

    @pytest.mark.parametrize(
        "interval, result",
        [("b3", (3, -1)), ("5", (5, 0)), ("#4", (4, 1)), ("bb7", (7, -2))],
    )
    def test_interpret(self, interval, result):
        assert Interval(interval).values() == result

    @pytest.mark.parametrize(
        "interval, result",
        [("b3", 3), ("5", 7), ("#4", 6), ("bb7", 9), ("#9", 15), ("b13", 20)],
    )
    def test__abs__(self, interval, result):
        assert abs(Interval(interval)) == result

    @pytest.mark.parametrize(
        "interval, result",
        [
            pytest.param("b3", (6, 0), id="b3"),
            pytest.param("5", (4, 0), id="5"),
            pytest.param("#4", (5, -1), id="#4"),
            pytest.param("bb7", (2, 1), id="bb7"),
            pytest.param("#1", (8, -1), id="#1"),
            pytest.param("#3", (6, -2), id="#3"),
        ],
    )
    def test__neg__(self, interval, result):
        assert (-Interval(interval)).values() == result

    @pytest.mark.parametrize(
        "base, other",
        [
            pytest.param((3, 1), (4, 0), id="#3==4"),
            pytest.param((4, 1), (5, -1), id="#4==b5"),
            pytest.param((9, -1), (8, 1), id="b9==#8"),
        ],
    )
    def test__eq__(self, base, other):
        assert Interval(*base) == Interval(*other)
        assert not Interval(*base) != Interval(*other)

    @pytest.mark.parametrize(
        "base, other, result",
        [
            pytest.param("3", "b3", (5, 0), id="3+b3==5"),
            pytest.param("2", "b2", (3, -1), id="2+b2==b3"),
            pytest.param("4", "#2", (5, 1), id="4+#2==#5"),
            pytest.param("7", "3", (9, 1), id="7+3==#9"),
            pytest.param("6", "b3", (8, 0), id="6+b3==8"),
            pytest.param("#11", "b3", (13, 0), id="#11+b3==13"),
            pytest.param("1", "#1", (1, 1), id="1+#1==#1"),
        ],
    )
    def test__add__(self, base, other, result):
        assert (Interval(base) + Interval(other)).values() == result

    @pytest.mark.parametrize(
        "base, other, result",
        [
            pytest.param("5", "b3", (3, 0), id="5-b3==3"),
            pytest.param("3", "2", (2, 0), id="3-2==2"),
            pytest.param("#5", "4", (2, 1), id="#5-4==#2"),
            pytest.param("#9", "b7", (3, 1), id="#9-b7==#3"),
            pytest.param("8", "6", (3, -1), id="8-6==b3"),
            pytest.param("13", "b3", (11, 1), id="13-b3==#11"),
            pytest.param("2", "#1", (2, -1), id="2-#1==b2"),
        ],
    )
    def test__sub__(self, base, other, result):
        assert (Interval(base) - Interval(other)).values() == result


# class TestIntervalsClass:
#     def test_triad_inversion(self, tuplets, result):
#         for each in tuplets:
#             obj = Intervals(*tuplets)
#             pass


class TestInterval:
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

    # def test_ambiguous(self):
    # assert pitch.detect_chord([('C', 0), ('C#', 0), ('D', 0)]) == None
