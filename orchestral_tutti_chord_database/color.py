import numpy as np
from math import pi


def make_swatches(
    start=0.5,
    rotations=0,
    min_sat=1.2,
    max_sat=1.2,
    min_light=0.0,
    max_light=1.0,
    gamma=1.0,
    numbers=256.0,
    reverse=False,
    float=False,
    hex=False,
) -> list:
    """Generates a list of RGB values with the cubehelix color scheme.
    
    Cubehelix is intended to create color schemes spanning from black
    to white, traversing through red, green, and blue using a tapered
    helix in the colour cube with increasing perceived intensity. See
    http://www.mrao.cam.ac.uk/~dag/CUBEHELIX/

    Args:
        start: The central hue at the middle of the scheme, ranging
            from 0.0 to 3.0.
        rotations: Deviation from the central hue with rotations of the
            helix. Defaults to 0 being monochrome. Can be negative.
        min_sat: The saturation at the start of the scheme.
        max_sat: The saturation at the end of the scheme.
        min_light: The lightness at the start of the scheme.
        max_light: The lightness at the end of the scheme.
        gamma: Emphasis of low or high intensity.
        numbers: The number of colors within the scheme.
        reverse: Return color list reversed.
        float: Convert return values to float rather than 8-bit int.
        hex: Convert none-float values to #xxxxxx format.
    """
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
    if not float:
        color_list = (255 * np.clip(transformed_color, 0.0, 1.0)).astype(np.uint8)
        if hex:
            color_list = [
                "#" + "".join(map(lambda i: "{0:#0{1}X}".format(i, 4)[2:], x))
                for x in color_list
            ]
    else:
        color_list = np.clip(transformed_color, 0.0, 1.0)

    # Reverse the color list if requested
    if reverse:
        color_list = color_list[::-1]

    return color_list


def pitch_class_index_to_hue(midinum):
    hue_range = [0, 24, 48, 65, 85, 120, 185, 214, 240, 264, 284, 315]
    return hue_range[midinum % 12] / 120


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
