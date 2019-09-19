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
    def parse_instrument(cls, k: str, v: str) -> tuple:
        if "{" in v and "}" in v:
            detection, v = v.split("}", 1)
        values = v.split(",", 3)
        if "<" in values[0] and ">" in values[0]:
            notes = values[0].translate(str.maketrans("", "", "<>")).strip().split(" ")
        else:
            notes = [values[0]]
        dynamic = values[1] if (len(values) > 1 and values[1]) else None
        technique = values[2] if (len(values) > 2 and values[2]) else None
        return (k, notes, dynamic, technique)
