import pytest
from orchestral_tutti_chord_database.parser import ChordInfo


class TestParseInfo:
    @pytest.mark.parametrize(
        "key, value, result",
        [
            pytest.param(
                "composer", "Benjamin Britten", "Britten,_Benjamin", id="Composer"
            ),
            pytest.param("year", "1945", 1945, id="Year"),
            pytest.param("opus", "Opus 34", "Op.34", id="Opus"),
            pytest.param(
                "name",
                "The Young Person's Guide to the Orchestra",
                "The Young Person's Guide to the Orchestra",
                id="Name",
            ),
            pytest.param("movement", "Fugue", "Fugue", id="Movement"),
            pytest.param("measure", "-1", -1, id="Measure"),
            pytest.param("tempo", "Allegro molto", "Allegro molto", id="Tempo"),
            pytest.param("chord", "D", "D", id="Chord"),
        ],
    )
    def test_parse_info_long(self, key, value, result):
        assert ChordInfo.parse_info(key, value) == (key, result)

    @pytest.mark.parametrize(
        "short, key, value, result",
        [
            pytest.param(
                "c", "composer", "Benjamin Britten", "Britten,_Benjamin", id="Composer"
            ),
            pytest.param("y", "year", "1945", 1945, id="Year"),
            pytest.param("o", "opus", "Opus 34", "Op.34", id="Opus"),
            pytest.param(
                "n",
                "name",
                "The Young Person's Guide to the Orchestra",
                "The Young Person's Guide to the Orchestra",
                id="Name",
            ),
            pytest.param("m", "movement", "Fugue", "Fugue", id="Movement"),
            pytest.param("b", "measure", "-1", -1, id="Measure"),
            pytest.param("t", "tempo", "Allegro molto", "Allegro molto", id="Tempo"),
            pytest.param("h", "chord", "D", "D", id="Chord"),
        ],
    )
    def test_parse_info_short(self, short, key, value, result):
        assert ChordInfo.parse_info(short, value) == (key, result)

    @pytest.mark.parametrize(
        "line, key, value",
        [
            pytest.param(
                "Composer: Benjamin Britten",
                "composer",
                "Britten,_Benjamin",
                id="Composer:Britten",
            ),
            pytest.param("Year: 1945", "year", 1945, id="Year"),
            pytest.param("Opus: Opus 34", "opus", "Op.34", id="Opus"),
            pytest.param(
                "Name: The Young Person's Guide to the Orchestra",
                "name",
                "The Young Person's Guide to the Orchestra",
                id="Name",
            ),
            pytest.param("Movement: Fugue", "movement", "Fugue", id="Movement"),
            pytest.param("Measure: -1", "measure", -1, id="Measure"),
            pytest.param("Tempo: Allegro molto", "tempo", "Allegro molto", id="Tempo"),
            pytest.param("IMSLP: ", "Imslp", None, id="IMSLP_empty"),
            pytest.param("Chord: D", "chord", "D", id="Chord"),
            pytest.param("H: D", "chord", "D", id="Chord_short"),
        ],
    )
    def test_parse_line(self, line, key, value):
        obj = ChordInfo()
        obj.parse_line(line)
        assert getattr(obj, key, None) == value


class TestParseInstrument:
    @pytest.mark.parametrize(
        "line, result",
        [
            pytest.param(
                "picc.:D6|fff", ("picc.", "treble", ["D6"], "fff", None), id="Piccolo_D5_fff"
            ),
            pytest.param(
                "flute:<F#5 A5>|fff",
                ("flute", "treble", ["F#5", "A5"], "fff", None),
                id="Flute_F#5-A5_fff",
            ),
            pytest.param(
                "oboes:<F#4 A4>|fff|fermata",
                ("oboes", "treble", ["F#4", "A4"], "fff", "fermata"),
                id="Oboes_F#4-A4_fff_fermata",
            ),
            pytest.param(
                "clarinets:<D4 D5>||fermata",
                ("clarinets", "treble", ["D4", "D5"], None, "fermata"),
                id="Clarinets_D4-D5_fermata",
            ),
            pytest.param(
                "flute:||fermata", ("flute", "treble", [""], None, "fermata"), id="No_notes==rest"
            ),
            pytest.param("flute:", ("flute", "treble", [""], None, None), id="No_value==rest"),
        ],
    )
    def test_parse_instrument_direct(self, line, result):
        assert ChordInfo.parse_instrument(*line.split(":")) == result

    @pytest.mark.parametrize(
        "line, result",
        [
            pytest.param(
                "harp-rh:{treble|}<D F# A D'>",
                ('harp-rh', "treble", ['D4', 'F#4', 'A4', 'D5'], None, None),
                id="Treble_No_transposition"
            ),
            pytest.param(
                "harp-lh:{bass|}<D F# A D'>",
                ('harp-lh', "bass", ['D2', 'F#2', 'A2', 'D3'], None, None),
                id="Bass_No_transposition"
            ),
            pytest.param(
                "vln.I:{tva8|}<D D'>",
                ('vln.I', "tva8", ['D5', 'D6'], None, None),
                id="vb8_No_transposition"
            ),
            pytest.param(
                "bass:{fvb8|}<D D'>",
                ('bass', "fvb8", ['D1', 'D2'], None, None),
                id="vb8_No_transposition"
            ),
            pytest.param(
                "inst:{t|2}<C C'>",
                ('inst', "t", ['D4', 'D5'], None, None),
                id="t+2"
            ),
            pytest.param(
                "inst:{t|-3}<D D'>",
                ('inst', "t", ['Bb3', 'Bb4'], None, None),
                id="t+2"
            ),
        ],
    )
    def test_parse_instrument_detection(self, line, result):
        assert ChordInfo.parse_instrument(*line.split(':')) == result
