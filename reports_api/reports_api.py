from flask import Blueprint, send_file, make_response, url_for
from flask_login import login_required, current_user
from flask_executor import Executor
from io import BytesIO

from .reports.pregame_report import PregameReport
 
report_executor = Executor()
report_api = Blueprint("report_api", __name__)



@report_api.route("/endzone/reports/test")
#@report_executor.job
def TestReport():
    report = PregameReport()
    
    pdf = report.title_page()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response


