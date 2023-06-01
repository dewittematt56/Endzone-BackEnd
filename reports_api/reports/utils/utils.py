
from io import BytesIO
import PyPDF2
import matplotlib.pyplot as plt
import warnings
import base64

warnings.filterwarnings('ignore')


def save_matPlot(plt: plt):
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def combine_pdf_pages(pages: list):
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pages:
        for page in pdf.pages:
            pdf_writer.add_page(page)

    combined_pdf = BytesIO()
    pdf_writer.write(combined_pdf)

    # Reset Bytes Position
    combined_pdf.seek(0)
    return combined_pdf.getvalue()
