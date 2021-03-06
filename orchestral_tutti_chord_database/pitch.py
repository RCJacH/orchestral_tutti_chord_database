import re
from typing import Union, Optional

PITCHCLASSES = "CDEFGAB"
PITCHID = (0, 2, 4, 5, 7, 9, 11)
DEFAULT_PITCH = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B")


def get_accidental_index(accidental: Optional[str]) -> int:
    """Returns the index of accidental string, e.g. #->1."""
    if not accidental or type(accidental) != str:
        return 0
    if not all(x in "#bx" for x in accidental):
        raise ValueError(f"Error in accidental {accidental}.")
    flat = accidental.count("b")
    sharp = accidental.count("#")
    double_sharp = accidental.count("x")
    return sharp + double_sharp * 2 - flat


def get_accidental(i: int) -> str:
    """Returns the accidental string from its index, e.g. 1->#."""
    s: str = ""
    if i > 0:
        s = "x" * (i // 2) + "#" * (i % 2)
    elif i < 0:
        s = "b" * abs(i)
    return s


class Pitch(object):
    """A musical pitch.

    Attributes:
        name: Displaying string of pitch, e.g. C#.
        octave: The sounding octave of a pitched note.
        pitch_class: The alphabet part of a pitch.
        pitch_class_index: The index of the pitch class, with C=0, B=6.
        accidental: The accidental modifier string of a pitch.
        accidental_index: The offset integer from its pitch class.
        index: The semitones within an octave with C=0, B=11.
        midinum: The corresponding midi number.
    """

    __slots__ = [
        "name",
        "octave",
        "midinum",
        "pitch_class",
        "pitch_class_index",
        "accidental",
        "accidental_index",
        "index",
    ]

    def __init__(self, in_str: Union[str, int] = "B", octave_in: int = 4):
        """Parse an input, integer or string, to create its properties.

        An integer input is taken as midi number and will be assigned
        pre-defined pitch names from C major with chromatic alternations
        from secondary dominant chords - all sharps except for flat 7th
        degree of V7/IV.

        A string input is taken as pitch names if it matches the format
        of: (pitch class)(accidental)(octave). Only the pitch class is
        required, and can be any of the 26 alphabet, capitalized. Any
        alphabet after G will be converted to A to G in groups of seven,
        thus H is A (not Bb), I is B and so on.

        The number of accidental modifiers is not restricted. Allowed
        accidental strings are: # = sharp; x = double sharp; b = flat.

        Args:
            in_str: The input to be parsed, can be int or str.
            octave_in: The explicit octave assignment, overrides any
                implicit octave values parsed from in_str.
        """
        octave = None
        if not in_str:
            raise IndexError("Pitch name cannot be empty.")
        if isinstance(in_str, int):
            in_str = DEFAULT_PITCH[in_str % 12] + str(in_str // 12)
        if isinstance(in_str, str):
            try:
                pitch_class, accidental, octave = re.findall(
                    r"([A-Z])([#bx]*)?(\d*)?", in_str
                )[0]
                if pitch_class not in PITCHCLASSES:
                    pitch_class = chr((ord(pitch_class) - 65) % 7 + 65)
                self.set_properties(pitch_class, accidental)
            except IndexError:
                raise ValueError(f"No pitch class found in {in_str}.")
        if not octave:
            octave = octave_in
        else:
            octave = int(octave)
        self.name: str = self.pitch_class + self.accidental
        self.octave: int = octave
        self.midinum: int = octave * 12 + PITCHID[
            self.pitch_class_index
        ] + self.accidental_index

    def __abs__(self):
        return self.midinum

    def __eq__(self, other):
        return self.index == other.index

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name + str(self.octave)

    def set_properties(self, pitch_class: str, accidental: str):
        """Assign musical properties from pitch class and accidental."""
        self.pitch_class: str = pitch_class
        self.pitch_class_index: int = PITCHCLASSES.index(pitch_class)
        self.accidental: str = accidental
        self.accidental_index: int = get_accidental_index(accidental)
        self.index: int = (PITCHID[self.pitch_class_index] + self.accidental_index) % 12

    def enharmonics(self) -> list:
        """Creates a list of enharmonics with maximum of two accidentals."""

        def sortlist(x):
            if x == self.name:
                return -1
            else:
                return abs(get_accidental_index(x[1:]))

        adjacent_indice = [x for x in range(-2, 3)]
        enharmonics = []
        for adjacent_index in adjacent_indice:
            pitch_class_index = self.pitch_class_index + adjacent_index
            pitch_class = PITCHCLASSES[pitch_class_index % 7]
            oct_diff = pitch_class_index // 7
            diff = self.diff(Pitch(pitch_class, self.octave + oct_diff))
            if abs(diff) > 2:
                continue
            enharmonics.append(pitch_class + get_accidental(-diff))
        return sorted(enharmonics, key=sortlist)

    def transpose(self, interval):
        """Returns a new Pitch object a set interval away from original."""
        descending = False
        if isinstance(interval, str):
            if interval[0] == "-":
                descending = True
                interval = interval.replace("-", "")
            interval = Interval(interval)
        if descending:
            pitch_class_index = (self.pitch_class_index - interval.quantity + 1) % 7
        else:
            pitch_class_index = (self.pitch_class_index + interval.quantity - 1) % 7
        oct_diff = (
            PITCHID[self.pitch_class_index]
            + self.accidental_index
            + abs(interval) * (-1 if descending else 1)
        ) // 12
        octave = self.octave + oct_diff
        pitch_class = PITCHCLASSES[pitch_class_index]
        new_pitch_class = Pitch(pitch_class, octave)
        diff = self.diff(new_pitch_class)
        accidental_index = (-abs(interval) if descending else abs(interval)) - diff
        accidental = get_accidental(accidental_index)
        return Pitch(pitch_class + accidental + str(octave))

    def diff(self, other, class_only=True):
        """Returns the difference in semitones between two pitches.
        
        Args:
            other: A Pitch object to be compared with self.
            class_only: Ignore accidental modification of the other.
        """
        self_index = PITCHID[self.pitch_class_index] + self.accidental_index
        other_index = PITCHID[other.pitch_class_index] if class_only else other.index
        diff = other_index - self_index
        diff += 12 * (other.octave - self.octave)
        return diff


class Interval:
    """An interval, the musical distance, between two musical pitches.
    
    Args:
        quantity: The numeric representation of the difference between
            the pitch class of two pitches.
        quality: The offset from a perfect/major interval.
    """

    __slots__ = ["quantity", "quality"]

    def __init__(self, lower, upper=None):
        """Analyze intervalic relationship between lower and upper Pitch.

        When both inputs are integers, the result is a direct assignment
        with lower number being quantity and upper number being quality.

        When both inputs are strings or Pitch classes, analysis is done
        to detect the musical interval between two pitches.

        When lower is string and upper received no input, it is assumed
        to take lower input as scale degree, e.g. 'b3', and will analyze
        and create representing interval.
        
        Args:
            lower: The lower pitch of an interval.
            upper: The upper pitch of an interval.
        """
        if isinstance(lower, int) and isinstance(upper, int):
            self.quantity, self.quality = lower, upper
        elif isinstance(lower, str) and isinstance(upper, str):
            self.quantity, self.quality = self.detect_interval(lower, upper)
        elif isinstance(lower, str) and not upper:
            self.quantity, self.quality = self.interpret(lower)

    def __abs__(self):
        pitch_class_index = self.quantity - 1
        return (
            (pitch_class_index // 7) * 12
            + PITCHID[pitch_class_index % 7]
            + self.quality
        )

    def __neg__(self):
        quantity, quality = self.inversion(self.quantity, self.quality).values()
        return Interval(quantity, quality)

    def __eq__(self, other):
        return abs(self) == abs(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        quantity = self.quantity + other.quantity - 1
        quality = (abs(self) + abs(other)) % 12 - PITCHID[(quantity - 1) % 7]
        return Interval(quantity, quality)

    def __sub__(self, other):
        quantity = self.quantity - other.quantity + 1
        quality = (abs(self) - abs(other)) % 12 - PITCHID[(quantity - 1) % 7]
        return Interval(quantity, quality)

    def values(self):
        return (self.quantity, self.quality)

    def interpret(self, interval: str):
        """Interpret scale degree string as an interval."""
        accidental, degree = re.findall(r"([#xb]*)(\d+)", interval)[0]
        quantity, quality = int(degree), get_accidental_index(accidental)
        return (quantity, quality)

    def detect_interval(self, lower, upper):
        """Analyze interval between lower pitch and upper pitch."""
        if type(lower) is str:
            lower = Pitch(lower)
        if type(upper) is str:
            upper = Pitch(upper)
        quantity = (upper.pitch_class_index - lower.pitch_class_index) % 7
        quality = (upper.index - lower.index) % 12 - PITCHID[quantity]
        return (quantity + 1, quality)

    def inversion(self, quantity: int, quality: int):
        """Create an interval object that is the inversion of input."""
        quantity = 9 - (quantity - 1) % 7 - 1
        quality = -quality if quantity in (1, 4, 5, 8) else -1 - quality
        return Interval(quantity, quality)


class Intervals(object):
    @staticmethod
    def get_intervals(pitch_names: list, from_root=None):
        intervals = []
        for i in range(len(pitch_names) - 1):
            intervals.append(
                Interval(from_root if from_root else pitch_names[i], pitch_names[i + 1])
            )
        return intervals


def detect_interval(lower, upper):
    if type(lower) is str:
        lower = Pitch(lower)
    if type(upper) is str:
        upper = Pitch(upper)
    quantity = (upper.pitch_class_index - lower.pitch_class_index) % 7
    quality = (upper.index - lower.index) % 12 - PITCHID[quantity]
    return (quantity + 1, quality)


def get_intervals(pitch_names: list, from_root=None):
    intervals = []
    for i in range(len(pitch_names) - 1):
        intervals.append(
            detect_interval(
                from_root if from_root else pitch_names[i], pitch_names[i + 1]
            )
        )
    return intervals


def identify_inversion(intervals: list):
    root_on_1 = [
        [4, 3],  # Triad
        [2, 3, 3],  # Seventh
        [2, 3],  # Seventh no5
        [2, 5],  # Seventh no3
    ]
    root_on_2 = [
        [3, 4],  # Triad
        [3, 2, 3],  # Seventh
        [5, 2],  # Seventh no5
        [3, 2],  # Seventh no3
    ]
    root_on_3 = [[3, 3, 2]]
    quantities = [x[0] for x in intervals]
    if set(quantities) == {3} or set(quantities) == {3, 5}:
        return 0
    elif quantities in root_on_1:
        return 1
    elif quantities in root_on_2:
        return 2
    elif quantities in root_on_3:
        return 3
    else:
        return None


def detect_root(note_list: list):
    pitch_names = [x[0] for x in note_list]
    filtered_pitch_names = sorted(set(pitch_names), key=lambda x: x[0])
    if len(filtered_pitch_names) < 5:
        intervals = get_intervals(filtered_pitch_names)
        root = identify_inversion(intervals)
        if root is not None:
            return filtered_pitch_names[root]
    midinums = [x[1] for x in note_list]
    return pitch_names[midinums.index(sorted(midinums)[0])]


def gen_chord_name(extension, interval_list):
    def quality(i):
        return interval_list[i - 1][0]

    def only_one(i):
        return len(interval_list[i - 1]) == 1

    def chk_quality(i, alt):
        return only_one(i) and quality(i) == alt

    def get_function():
        function = suspension = ""
        if not interval_list[2]:
            if chk_quality(2, 0):
                suspension += "sus2"
            if chk_quality(4, 0):
                if not suspension:
                    suspension = "sus"
                else:
                    suspension += "4"
        elif -1 in interval_list[2]:
            function = "m"
        return function, suspension

    major7 = False
    dim7 = False
    lyd = False

    if only_one(7):
        if quality(7) == 0:
            major7 = True
        elif quality(7) == -2:
            dim7 = True
    if chk_quality(4, 1):
        lyd = True

    chord_name = ""
    function, suspension = get_function()
    chord_name += function

    if dim7:
        chord_name += "o"
    if major7:
        chord_name += "Maj"
    if extension > 5:
        chord_name += str(extension)
    if lyd:
        chord_name += "lyd"

    chord_name += suspension
    print(chord_name)
    alts = [2, 5, 6]
    alt_degrees = [9, 5, 13]
    for i in range(0, 3):
        for alt in sorted(interval_list[alts[i] - 1], reverse=True):
            if alt > 0:
                chord_name += "#" + str(alt_degrees[i])
            elif alt < 0:
                chord_name += "b" * -alt + str(alt_degrees[i])

    if chord_name == "7#9b9#5b5":
        chord_name = "7alt"
    if "o" in chord_name:
        chord_name = chord_name.replace("m", "").replace("b5", "")
    if chord_name == "mb5":
        chord_name = "o"
    if chord_name[-2:] == "#5":
        chord_name = chord_name.replace("#5", "+")

    return chord_name


def detect_chord(note_list: list):
    def filter_mixolydian(interval):
        comparee = -1 if interval[0] == 7 else 0
        return interval[0] if interval[1] == comparee else 0

    if not len(note_list):
        raise IndexError("Cannot detect chord with no input.")
    root = detect_root(note_list)
    pitch_names = [x[0] for x in note_list]
    filtered_pitch_names = sorted(set(pitch_names), key=lambda x: x[0])
    intervals = sorted(x for x in get_intervals(filtered_pitch_names, root))
    print(intervals)
    extension = max(intervals, key=filter_mixolydian, default=(5, 0))[0]

    chord_name = gen_chord_name(
        extension, [[x[1] for x in intervals if x[0] == y] for y in range(1, 8)]
    )

    if chord_name is not None:
        return root + chord_name
    else:
        return None
