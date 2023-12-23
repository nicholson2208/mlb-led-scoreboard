#!/usr/bin/env python

import numpy as np
import pandas as pd
import requests as re
from PIL import Image
from scipy.ndimage import convolve
from io import BytesIO

import sys
import time
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from RGBMatrixEmulator import RGBMatrixOptions, graphics
from matrix.matrix import RGBMatrix
from RGBMatrixEmulator.graphics.color import Color

mlb_logos = pd.read_csv("MLB_Colors_Logos.csv")

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

canvas1 = matrix.CreateFrameCanvas()

font = graphics.Font()
font.LoadFont("assets/fonts/patched/5x8.bdf")
textColor = graphics.Color(255, 255, 0)
pos = canvas1.width
my_text = "hi champ"

try:
    print("Press CTRL-C to stop.")
    file_path = "./assets/team_logos/"

    while True:

        for team_abbr in mlb_logos.team_abbr.values:
            print(team_abbr)
            
             # IDK which size over here!
            for base_width in [14, 30]:

                for neighbors in [1, 2, 3]:
                    file_name = "{}-w{}n{}.png".format(team_abbr, base_width, neighbors)

                    img = Image.open(file_path + team_abbr + "/" + file_name)

                    # this is a gray background
                    matrix.Fill(84, 121, 109)
                    
                    matrix.SetImage(img, offset_x=1, offset_y=1)
                    # matrix.SetImage(img.convert("RGB"))

                    message = "w{}n{}".format(base_width, neighbors)
                    
                    # let's see if this one works
                    len = graphics.DrawText(matrix, font, 33, 10, textColor, message)
                    time.sleep(0.5)
                    matrix.Clear()

except KeyboardInterrupt:
    sys.exit(0)

