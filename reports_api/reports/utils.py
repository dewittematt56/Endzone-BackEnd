from docx.shared import Pt
from docx.shared import RGBColor

def endzone_heading(heading, accent: bool = False, underline: bool = False, bold: bool = False):
    """
    Create a custom font object using the specified TTF file and size.
    """
    font = heading.style.font
    font.name = "Calibri"
    font.bold = bold
    font.underline = underline
    if accent:
        font.color.rgb = RGBColor(9, 132, 227)
    else: 
        font.color.rgb = RGBColor(10, 13, 20)