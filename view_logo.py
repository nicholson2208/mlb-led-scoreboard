#!/usr/bin/env python

import numpy as np
import pandas as pd
import requests as re
from PIL import Image
from scipy.ndimage import convolve
from io import BytesIO

import sys
import time
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions


def drop_pixels(image, num_neighbors):
    image_copy = np.copy(image)
    print(np.sum(image_copy), image_copy.shape)
    
    non_zero_pixels = np.where(np.sum(image_copy, axis=2) > 0, 1, 0)
    
    # count the number of adjacent pixels
    neighborhood_filter = np.array([[0, 1, 0],
                                    [1, 0, 1],
                                    [0, 1, 0]])

    neighbors_count = convolve(non_zero_pixels, neighborhood_filter, mode='constant', cval=0.0)
    
    mask = neighbors_count > num_neighbors

    print("how many pixel with more than {} neighbors".format(num_neighbors), np.sum(mask), mask.shape)
    
    image_copy[~mask, :] = 0

    print(np.sum(image_copy), image_copy.shape)
    
    return image_copy


mlb_logos = pd.read_csv("MLB_Colors_Logos.csv")

base_img_url = mlb_logos.loc[mlb_logos["team_abbr"] == "SEA", "team_scoreboard_logo_espn"].values[0]

# IDK which size over here!
base_width= 14
img_resp = re.get(base_img_url)

img = Image.open(BytesIO(img_resp.content))

wpercent = (base_width / float(img.size[0]))
hsize = int((float(img.size[1]) * float(wpercent)))
small_img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
img_as_array = np.array(small_img.convert('RGB'))
# img.thumbnail((base_width, base_width), Image.Resampling.LANCZOS)

cleaned_img = Image.fromarray(drop_pixels(img_as_array, 2), "RGB")

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

# Make image fit our screen.

matrix.SetImage(cleaned_img)
# matrix.SetImage(cleaned_img.convert('RGB'))

try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)

