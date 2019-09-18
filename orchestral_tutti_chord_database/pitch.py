PITCHCLASSES = "CDEFGAB"
PITCHID = [0, 2, 4, 5, 7, 9, 11]


def get_accidental_index(accidental):
    if not accidental or type(accidental) != str:
        return 0
    if not all(x in "#bx" for x in accidental):
        raise ValueError(f"Error in accidental {accidental}.")
    flat = accidental.count("b")
    sharp = accidental.count("#")
    double_sharp = accidental.count("x")
    return sharp + double_sharp * 2 - flat


def get_properties(pitch_name: str):
    if not pitch_name:
        raise IndexError("Pitch name cannot be empty.")
    if any(x in pitch_name for x in PITCHCLASSES):
        pitch_class = pitch_name[0]
        class_index = PITCHCLASSES.index(pitch_class)
        index = PITCHID[class_index]

        accidental = pitch_name[1:] if len(pitch_name) else ""
        accidental_index = get_accidental_index(accidental)

        return {
            "name": pitch_name,
            "class": pitch_class,
            "class_index": class_index,
            "index": index + accidental_index,
            "accidental": accidental,
            "accidental_index": accidental_index,
        }
    else:
        raise ValueError(f"No pitch class found in {pitch_name}.")


def get_midinum(pitch_name: str, octave: int):
    return octave * 12 + get_properties(pitch_name)["index"]


def detect_interval(lower, upper):
    if type(lower) is str:
        lower = get_properties(lower)
    if type(upper) is str:
        upper = get_properties(upper)
    quantity = (upper["class_index"] - lower["class_index"]) % 7
    quality = (upper["index"] - lower["index"]) % 12 - PITCHID[quantity]
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
        try:
            return interval_list[i-1][0]
        except IndexError:
            return 0

    def only_one(i):
        return len(interval_list[i-1]) == 1

    def chk_quality(i, alt):
        return only_one(i) and quality(i) == alt

    def is_empty(i):
        return not interval_list[i-1]

    def get_function():
        function = suspension = ''
        if not interval_list[2]:
            if chk_quality(2, 0):
                suspension += 'sus2'
            if chk_quality(4, 0):
                if not suspension:
                    suspension = 'sus'
                else:
                    suspension += '4'
        elif -1 in interval_list[2]:
            function = 'm'
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
    if 'o' in chord_name:
        chord_name = chord_name.replace('m', '').replace('b5', '')
    if chord_name == 'mb5':
        chord_name = 'o'
    if chord_name[-2:] == "#5":
        chord_name = chord_name.replace("#5", "+")
    if chord_name == "Maj":
        chord_name = ""

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
    intervals = sorted(
        x[0] * 2 if (x[0] % 2) == 0 else x
        for x in get_intervals(filtered_pitch_names, root)
    )
    extension = max(intervals, key=filter_mixolydian, default=(5, 0))[0]

    chord_name = gen_chord_name(
        extension,
        [[x[1] for x in intervals if x[0] == y] for y in range(1, 8)]
        )

    if chord_name is not None:
        return root + chord_name
    else:
        return None
