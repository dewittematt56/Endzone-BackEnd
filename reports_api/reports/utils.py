
from io import BytesIO
import pandas as pd
from typing import Union
import PyPDF2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import warnings

import base64
from matplotlib.font_manager import fontManager, FontProperties
import matplotlib.cm as cm
from matplotlib.cm import RdYlBu
import numpy as np


warnings.filterwarnings('ignore')

def __save_matPlot__(plt: plt):
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')