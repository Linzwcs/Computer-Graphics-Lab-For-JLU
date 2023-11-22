from PIL import Image
import numpy as np


CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 600

STUDENT_ID = "1027"
WATERMARK = (255 - np.array(Image.open(f"./asserts/{STUDENT_ID}.png"))) > 0
