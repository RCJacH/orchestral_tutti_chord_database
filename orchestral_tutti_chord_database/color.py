import colorsys
import numpy as np
from math import pi


def make_swatches(
    start=0.5,
    rotations=0,
    min_sat=1.2,
    max_sat=1.2,
    gamma=1.0,
    numbers=256.0,
    min_light=0.0,
    max_light=1.0,
    reverse=False,
    hex=False,
) -> list:

    # Clip some of the passed values into ranges that make sense.
    start = np.clip(start, 0.0, 3.0)
    min_sat = np.clip(min_sat, 0, 2)
    max_sat = np.clip(max_sat, 0, 2)
    min_light = np.clip(min_light, 0, 2)
    max_light = np.clip(max_light, 0, 2)
    numbers = np.clip(numbers, 1, 1024)

    # Define transform scalars
    fract = np.linspace(min_light, max_light, numbers)
    phi = 2.0 * pi * ((start + 1) / 3.0 + rotations * fract)
    fract **= gamma

    satar = np.linspace(min_sat, max_sat, numbers)
    amp = satar * fract * (1.0 - fract) / 2.0

    # Define transform vectors/matrices
    transform_matrix = np.array(
        [[-0.14861, +1.78277], [-0.29227, -0.90649], [+1.97249, +0.00000]]
    )
    rotation_vector = np.array([np.cos(phi), np.sin(phi)])

    # Perform transformation
    transformed_color = (
        fract + amp * np.einsum("jk, ij->ik", rotation_vector, transform_matrix)
    ).T

    # Clip and normalize to 8bit
    color_list = (255 * np.clip(transformed_color, 0.0, 1.0)).astype(np.uint8)

    # Reverse the color list if requested
    if reverse:
        color_list = color_list[::-1]

    if hex:
        color_list = [
            "#" + "".join(map(lambda i: "{0:#0{1}X}".format(i, 4)[2:], x))
            for x in color_list
        ]

    return color_list


def tohex(x):
    return "{0:#0{1}X}".format(x, 4)[2:]


def midinum_to_freq(midinum, A4=440):
    return A4 * (2 ** (1 / 12)) ** (midinum - 48)


def rgb_to_hsl(r, g, b):
    r, g, b = [x / 255.0 for x in (r, g, b)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def color_from_wavelength(wavelength):
    def factorAdjust(color, factor, intensityMax, gamma):
        if color == 0.0:
            return 0
        else:
            return intensityMax * (color * factor) ** gamma // 1

    Gamma = 1
    IntensityMax = 255
    w = int(wavelength)

    # colour
    if w >= 380 and w < 440:
        R = -(w - 440.0) / (440.0 - 350.0)
        G = 0.0
        B = 1.0
    elif w >= 440 and w < 490:
        R = 0.0
        G = (w - 440.0) / (490.0 - 440.0)
        B = 1.0
    elif w >= 490 and w < 510:
        R = 0.0
        G = 1.0
        B = -(w - 510.0) / (510.0 - 490.0)
    elif w >= 510 and w < 580:
        R = (w - 510.0) / (580.0 - 510.0)
        G = 1.0
        B = 0.0
    elif w >= 580 and w < 645:
        R = 1.0
        G = -(w - 645.0) / (645.0 - 580.0)
        B = 0.0
    elif w >= 645 and w <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # Intensity factor goes through the range:
    # 0.1 (350-420 nm) 1.0 (420-645 nm) 1.0 (645-780 nm) 0.2

    if w >= 350 and w < 420:
        Factor = 0.1 + 0.9 * (w - 350) / (420 - 350)
    elif w >= 420 and w < 645:
        Factor = 1.0
    elif w >= 645 and w <= 780:
        Factor = 0.2 + 0.8 * (780 - w) / (780 - 645)
    else:
        Factor = 0.0

    R = factorAdjust(R, Factor, IntensityMax, Gamma)
    G = factorAdjust(G, Factor, IntensityMax, Gamma)
    B = factorAdjust(B, Factor, IntensityMax, Gamma)

    colors = rgb_to_hsl(R, G, B)
    return colors  # (R,G,B)


lightFreqRedLower = 400000000000000
lightFreqOrangeLower = 484000000000000
lightFreqYellowLower = 508000000000000
lightFreqGreenLower = 526000000000000
lightFreqCyanLower = 606000000000000
lightFreqBlueLower = 631000000000000
lightFreqVioletLower = 668000000000000
lightFreqVioletUpper = (
    800000000000000
)  # really 789 THz, but we fudge to guarantee success in finding a consonant color


def resonant_color(freq):
    def wavelength(freq, speedofSound=299792458):
        return speedofSound / freq

    lightfreq = freq
    lightOctave = 0
    while lightfreq < lightFreqRedLower:
        lightfreq *= 2
        lightOctave += 1

    lightfreqTHz = lightfreq / 1000000000000
    lightWavelength = wavelength(lightfreqTHz)
    lightWavelengthNM = lightWavelength * 1000000000

    return color_from_wavelength(lightWavelengthNM)


ratios = [
    36 / 25,
    16 / 15,
    8 / 5,
    6 / 5,
    9 / 5,
    4 / 3,
    1 / 1,
    3 / 2,
    9 / 8,
    5 / 3,
    5 / 4,
    15 / 8,
    25 / 18,
    25 / 24,
    25 / 16,
    75 / 64,
    225 / 128,
]
intervals = [
    "b5",
    "b2",
    "b6",
    "b3",
    "b7",
    "4",
    "1",
    "5",
    "2",
    "6",
    "3",
    "7",
    "#4",
    "#1",
    "#5",
    "#2",
    "#6",
]


def to_str(x, i=1):
    return "hsl(" + ",".join(map(str, map(int, x))) + ")"


# a = []
# for i in range(0,12):
# a.append((i, [(intervals[ratios.index(x)], to_str(resonant_color(x * midinum_to_freq(i, 440)))) for x in ratios]))
# a
