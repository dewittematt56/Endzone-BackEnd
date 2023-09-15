from flask import Blueprint, send_file, jsonify, Response, request
from flask_login import login_required, current_user
import json
import io
from flask import Blueprint, send_file
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from reports_api.reports.thunderbolt_report.thunderbolt_report import ThunderboltReport
from reports_api.reports.ingame_report.ingame_report import EmptyDataException, IngameReport
from reports_api.reports.postgame_report.postgame_report import PostgameReport

reports_api = Blueprint('reports_api', __name__)
report_executor = ThreadPoolExecutor()
thread_lock = Lock()

from reports_api.reports.pregame_report.pregame_report import PregameReport

def __run_pregame_report__(requested_pages: 'list[str]', requested_team: str, requested_games: 'list[str]', team_code: str):
    with thread_lock:
        report = PregameReport(requested_pages, requested_team, requested_games, team_code)
        pdf = report.combine_reports()
        return pdf

def __run_thunderbolt_report__(team_of_interest: str, game_IDs: str, user_team_code: str, report_type: str):
    with thread_lock:
        report = ThunderboltReport(team_of_interest, game_IDs, user_team_code, report_type)
        pdf = report.combine_reports()
        return pdf
    
def __run_ingame_report__(team_of_interest: str, game_ID: str, user_team_code: str, game_ids: list):
    with thread_lock:
        report = IngameReport(team_of_interest, game_ID, user_team_code, game_ids)
        pdf = report.combine_reports()
        return pdf

def __run_postgame_report__(team_of_interest: str, gameId: str, user_team_code: str):
    with thread_lock:
        report = PostgameReport(team_of_interest, gameId, user_team_code)
        pdf = report.combine_reports()
        return pdf

@reports_api.route("/endzone/reports/pregame/metadata")
@login_required
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
@login_required
def pregame_report_run():
    current_team = current_user.Current_Team
    requestedPages = request.args.get('requestedPages')
    requestedTeamOfInterest = request.args.get('requestedTeamOfInterest')
    requestedGames = request.args.get('requestedGames')
    if requestedPages:
        requestedPages_list = requestedPages.split(',')
        requestedTeamOfInterest_str = requestedTeamOfInterest
        requestedGame_list = requestedGames.split(",")
        
        executor_job = report_executor.submit(__run_pregame_report__, requestedPages_list, requestedTeamOfInterest_str, requestedGame_list, current_team)
        response = executor_job.result()
        return send_file(
            io.BytesIO(response),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='output.pdf'
        )

@reports_api.route("/endzone/reports/thunderbolt/run", methods = ["GET"]) # confirm with mater
@login_required
def thunderbolt_report_run():
    try:
        current_team = current_user.Current_Team
        requestedTeamOfInterest = request.args.get('requestedTeamOfInterest')
        requestedGameIDs = request.args.get('requestedGames')
        requestedGame_list = requestedGameIDs.split(",")
        requested_report_type = request.args.get("requestedReportType")

        executor_job = report_executor.submit(__run_thunderbolt_report__, requestedTeamOfInterest, requestedGame_list, current_team, requested_report_type)
        response = executor_job.result()
        return send_file( 
                io.BytesIO(response),
                mimetype='application/pdf',
                as_attachment=True,
                download_name="pog.pdf"
            )
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

# To-Do create route for /endzone/reports/thunderbolt/run


@reports_api.route("/endzone/reports/ingame/run", methods = ["GET"]) # confirm with mater
@login_required
def ingame_report_run():
    try:
        current_team = current_user.Current_Team
        requestedTeamOfInterest = request.args.get('requestedTeamOfInterest')
        requestedGame= request.args.get('requestedGame')
        requestedPriorGames = request.args.get('requestedPriorGames')

        executor_job = report_executor.submit(__run_ingame_report__, requestedTeamOfInterest, requestedGame, current_team, requestedPriorGames.split(','))
        response = executor_job.result()
        return send_file( 
                io.BytesIO(response),
                mimetype='application/pdf',
                as_attachment=True,
                download_name="pog.pdf"
        )
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
@reports_api.route("/endzone/reports/postgame/run", methods = ["GET"]) 
# @login_required
def postgame_report_run():
    try:
        # current_team = current_user.Current_Team\
        current_team = current_user.Current_Team
        requestedTeamOfInterest = request.args.get('requestedTeamOfInterest')
        requestedGameId = request.args.get('requestedGame')

        executor_job = report_executor.submit(__run_postgame_report__, requestedTeamOfInterest, requestedGameId, current_team)
        response = executor_job.result()
        return send_file( 
                io.BytesIO(response),
                mimetype='application/pdf',
                as_attachment=True,
                download_name="pog.pdf"
            )
    except EmptyDataException as e:
        return Response(e.message, status=500)
        
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
