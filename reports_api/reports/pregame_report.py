from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from io import BytesIO
from .utils import *

import jinja2
import pdfkit

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')

class PregameReport():
    def __init__(self) -> None:
        self.pdfs = []
        self.team = "Eastview"
        #self.title_page()

    def save_report(self) -> BytesIO:
        output = BytesIO()
        self.document.save(output)
        return output

    def title_page(self) -> None:
        title_template = env.get_template('report_pages/title/title_page.html')
        html = title_template.render(title="Pregame Report", team="Eastview", games = [{"homeTeam": "Eastview", "awayTeam": "Rosemount", "Date": "October 1, 2023"}])
        pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
        return pdf
    
if __name__ == "__main__":
    test = PregameReport()