class ChordInfo:
    long = [
        "composer",
        "year",
        "opus",
        "name",
        "movement",
        "measure",
        "tempo",
        "orchestra_size",
        "performer",
        "imslp",
        "chord",
    ]
    short = ["c", "y", "o", "n", "m", "b", "t", "s", "p", "i", "h"]

    def __init__(self):
        pass

    def parse_line(self, line: str):
        k, v = line.split(":")
        v = v.strip()
        if not v:
            return
        k = k.strip().lower()
        if any(k not in x for x in (self.long, self.short)):
            setattr(self, *self.parse_info(k, v))
        else:
            setattr(self, *self.parse_instrument(k, v))

    @classmethod
    def parse_info(cls, k: str, v: str) -> tuple:
        if k in cls.short:
            k = cls.long[cls.short.index(k)]
        if k == "composer":
            v = ",_".join(v.rsplit(" ", 1)[::-1])
        if k == "opus":
            v = v.replace(" ", "").replace("Opus", "Op.")
        return (k, int(v) if v.lstrip("-").isdigit() else v)

    @classmethod
    def parse_instrument(cls, instrument: str, v: str) -> tuple:
        def get_note(note):
            clefs = {"treble": 4, "t": 4, "g": 4, "bass": 2, "f": 2, "c": 3, "alto": 3}
            number: int = note.count("'") - note.count(",")
            if clef in clefs:
                number += clefs[clef]
            return note.replace("'", "").replace(",", "") + str(number)

        if "{" in v and "}" in v:
            detection, v = v.replace("{", "").split("}", 1)
        else:
            detection = None
        values = v.split("|", 3)
        if "<" in values[0] and ">" in values[0]:
            notes = values[0].replace("<", "").replace(">", "").strip().split(" ")
        else:
            notes = [values[0]]
        if detection:
            clef, mode = detection.split("|")
            notes = list(map(get_note, notes))
        dynamic = values[1] if (len(values) > 1 and values[1]) else None
        technique = values[2] if (len(values) > 2 and values[2]) else None
        return (instrument, notes, dynamic, technique)
