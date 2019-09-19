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

    def parse_info(self, k: str, v: str) -> tuple:
        if k in self.short:
            k = self.long[self.short.index(k)]
        if k == "composer":
            v = ",_".join(v.rsplit(" ", 1)[::-1])
        if k == 'opus':
            v = v.replace(' ', '').replace('Opus', 'Op.')
        return (k, int(v) if v.lstrip("-").isdigit() else v)

    def parse_line(self, line: str):
        k, v = line.split(":")
        k = k.lower()
        v = v.strip()
        if any(k not in x for x in (self.long, self.short)) and v:
            setattr(self, *self.parse_info(k, v))

    def parse_instrument(self):
        pass
