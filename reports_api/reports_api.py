from flask import Blueprint, send_file, jsonify, Response, request
from flask_login import login_required, current_user
import json
import io
from flask import Blueprint, send_file
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

reports_api = Blueprint('reports_api', __name__)
report_executor = ThreadPoolExecutor()
thread_lock = Lock()

from reports_api.reports.pregame_report import PregameReport

def __run_pregame_report__(requested_pages: 'list[str]'):
    with thread_lock:
        report = PregameReport(requested_pages)
        pdf = report.combine_reports()
        return pdf

@reports_api.route("/endzone/reports/pregame/metadata")
def pregame_report():
    available_packs = {}
    available_packs["Packs"] = []
    available_packs["Packs"].append(create_pregame_o_packs())
    available_packs["Packs"].append(create_pregame_d_packs())
    return jsonify(available_packs)

def create_pregame_o_packs():
    offense_pack = {"name": "Offense"}
    offense_pack["packs"] = []
    offense_pack["packs"].append({"name": "Offensive Overview", 'id': 'o_overview', "isAutoEnabled": True, "packs": []})
    offense_pack["packs"].append({"name": "Play Type Pack", 'id': 'o_playType_pack', "isAutoEnabled": False, "packs": [{"name": "Personnel", 'id': 'o_playType_personnel', "isAutoEnabled": True},{"name": "Down and Distance", 'id': 'o_playType_downDistance', "isAutoEnabled": True}, {"name": "Field Position", 'id': 'o_playType_fieldPos', "isAutoEnabled": False}]})
    offense_pack["packs"].append({"name": "Formation Strength Analysis", 'id': 'o_formStrength', "isAutoEnabled": True, "packs": []})
    offense_pack["packs"].append({"name": "Ball Carrier Pack", 'id': 'o_ballCarrier_pack', "isAutoEnabled": False, "packs": [{"name": "Ball Carrier Overview", 'id': 'o_ballCarrier_overview', "isAutoEnabled": True},{"name": "Ball Carrier Detail", 'id': 'o_ballCarrier_detail', "isAutoEnabled": False}]})
    offense_pack["packs"].append({"name": "Boundary Analysis", 'id': 'o_boundary', "isAutoEnabled": True, "packs": []})
    offense_pack["packs"].append({"name": "Passing Pack", 'id': 'o_pass_pack', "isAutoEnabled": False, "packs": [{"name": "Passing Overview",'id': 'o_passing_overview', "isAutoEnabled": True},{"name": "Passing Detail",'id': 'o_passing_detail', "isAutoEnabled": False}, {"name": "Passing Targets",'id': 'o_passing_targets', "isAutoEnabled": True}]})
    offense_pack["packs"].append({"name": "Situational Pack", 'id': 'o_situational_pack', "isAutoEnabled": False, "packs": [{"name": "Redzone",'id': 'o_situational_redzone', "isAutoEnabled": False},{"name": "1st Down", 'id': 'o_situational_1', "isAutoEnabled": False}, {"name": "2nd Down", 'id': 'o_situational_2', "isAutoEnabled": False}, {"name": "3rd Down", 'id': 'o_situational_3', "isAutoEnabled": False}, {"name": "4th Down", 'id': 'o_situational_4', "isAutoEnabled": False}]})
    return offense_pack

def create_pregame_d_packs():
    defense_pack = {"name": "Defense"}
    defense_pack["packs"] = []
    defense_pack["packs"].append({"name": "Defensive Overview", 'id': 'd_overview', "isAutoEnabled": True, "packs": []})
    defense_pack["packs"].append({"name": "Defense Base Pack", 'id': 'd_base_pack', "isAutoEnabled": False, "packs": [{"name": "Personnel", 'id': 'd_base_personnel', "isAutoEnabled": True},{"name": "Down and Distance", 'id': 'd_base_downDistance', "isAutoEnabled": True}]})
    defense_pack["packs"].append({"name": "Pass Pack", 'id': 'd_pass', "isAutoEnabled": True, "packs": []})
    defense_pack["packs"].append({"name": "Boundary & Strength", 'id': 'd_boundary_strength', "isAutoEnabled": True, "packs": []})
    defense_pack["packs"].append({"name": "Field Position", 'id': 'd_fieldPos', "isAutoEnabled": False, "packs": []})
    defense_pack["packs"].append({"name": "Situational Pack", 'id': 'd_situational_pack', "isAutoEnabled": False, "packs": [{"name": "Redzone", 'id': 'd_situational_redzone', "isAutoEnabled": False},{"name": "1st Down", 'id': 'd_situational_1', "isAutoEnabled": False}, {"name": "2nd Down", 'id': 'd_situational_2', "isAutoEnabled": False}, {"name": "3rd Down", 'id': 'd_situational_3', "isAutoEnabled": False}, {"name": "4th Down", 'id': 'd_situational_4', "isAutoEnabled": False}]})
    return defense_pack

@reports_api.route("/endzone/reports/pregame/run", methods = ["GET"])
def pregame_report_run():
    requestedPages = request.args.get('requestedPages')
    if requestedPages:
        requestedPages_list = requestedPages.split(',')
        
        executor_job = report_executor.submit(__run_pregame_report__, requestedPages_list)
        response = executor_job.result()
        return send_file(
            io.BytesIO(response),
            mimetype='application/pdf',
            as_attachment=True,
            attachment_filename='output.pdf'
        )

