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
                "Picc.:D6,fff", ("Picc.", ["D6"], "fff", None), id="Piccolo_D5_fff"
            ),
            pytest.param(
                "Flute:<F#5 A5>,fff",
                ("Flute", ["F#5", "A5"], "fff", None),
                id="Flute_F#5-A5_fff",
            ),
            pytest.param(
                "Oboes:<F#4 A4>,fff,Fermata",
                ("Oboes", ["F#4", "A4"], "fff", "Fermata"),
                id="Oboes_F#4-A4_fff_fermata",
            ),
            pytest.param(
                "Clarinets:<D4 D5>,,Fermata",
                ("Clarinets", ["D4", "D5"], None, "Fermata"),
                id="Clarinets_D4-D5_fermata",
            ),
            pytest.param(
                "Flute:,,Fermata", ("Flute", [""], None, "Fermata"), id="No_notes==rest"
            ),
            pytest.param("Flute:", ("Flute", [""], None, None), id="No_value==rest"),
        ],
    )
    def test_parse_instrument_direct(self, line, result):
        assert ChordInfo.parse_instrument(*line.split(":")) == result
