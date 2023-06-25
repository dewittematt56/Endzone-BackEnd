from io import BytesIO
import pandas as pd
import jinja2
import pdfkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import PyPDF2
from database.db import db_uri 
from database.models import *
from .d_report_utils import *
from ..utils.spatial_utils import *
from ..utils.graphing_utils import *
from ..utils.utils import *
from .d_report_utils import *
import sys
import datetime

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')

class PregameReport():
    def __init__(self, requested_pages: 'list[str]', team_of_interest: str, games: 'list[str]', user_team_code: str) -> None:
        self.pdfs = []
        self.team_of_interest = team_of_interest
        self.team_code = user_team_code
        self.requested_pages = requested_pages
        self.game_ids = games
        self.pages = []
        self.pdf_write = PyPDF2.PdfWriter()

        self.reportType = "Defense"

        # Temp Overriding
        self.team_of_interest = "Burnsville"
        self.team_code = "Endzone-System"
        self.game_ids = ["643ad3ef-8b71-422d-ba03-f150637f148e"]
        # Get game-based & play-based data from database.
        self.get_data()
        self.split_data()
        if "o_overview" in requested_pages: self.o_overview(self.offensive_data); self.pages.append("Offense Overview")
        if "o_playType_personnel" in requested_pages: self.o_play_type_personnel_page(self.offensive_data); self.pages.append("Offense Play Type - Personnel")
        if "o_playType_downDistance" in requested_pages: self.o_play_type_downDistance_page(self.offensive_data); self.pages.append("Offense Play Type - Down & Distance")
        if "o_playType_fieldPos" in requested_pages: self.o_play_type_field_page(self.offensive_data); self.pages.append("Offense Play Type - Field Position")
        if "o_formStrength" in requested_pages: self.o_strength_page(self.offensive_data); self.pages.append("Offense Play Type - Formation Strength")
        if "o_ballCarrier_overview" in requested_pages: self.o_ball_carrier_overview_page(self.offensive_data); self.pages.append("Offense Ball Carrier - Overview")
        if "o_ballCarrier_detail" in requested_pages: self.o_ball_carrier_detail_page(self.offensive_data); self.pages.append("Offense Ball Carrier - Detail")
        if "o_boundary" in requested_pages: self.o_boundary_page(self.offensive_data); self.pages.append("Offense - Field Boundary Analysis")
        if "o_passing_overview" in requested_pages: self.o_passing_overview_page(self.offensive_data); self.pages.append("Offense Passing - Overview")
        if "o_passing_detail" in requested_pages: self.o_passing_detail_page(self.offensive_data); self.pages.append("Offense Passing - Detail")
        if "o_passing_targets" in requested_pages: self.o_passing_targets_page(self.offensive_data); self.pages.append("Offense Passing - Targets")
        if "o_situational_redzone" in requested_pages: self.o_redzone_page(self.offensive_data); self.pages.append("Offense Situational - Redzone")
        if "o_situational_1" in requested_pages: self.o_down_1_page(self.offensive_data); self.pages.append("Offense Situational - 1st Down")
        if "o_situational_2" in requested_pages: self.o_down_2_page(self.offensive_data); self.pages.append("Offense Situational - 2nd Down")
        if "o_situational_3" in requested_pages: self.o_down_3_page(self.offensive_data); self.pages.append("Offense Situational - 3rd Down")
        if "o_situational_4" in requested_pages: self.o_down_4_page(self.offensive_data); self.pages.append("Offense Situational - 4th Down")
        if "d_overview" in requested_pages: self.d_overview(self.defensive_data); self.pages.append("Defense Overview")
        if "d_base_personnel" in requested_pages: self.d_formation_personnel(self.defensive_data); self.pages.append("Defense - Personnel")
        if "d_base_downDistance" in requested_pages: self.d_formation_down_distance(self.defensive_data); self.pages.append("Defense - Down & Distance")
        if "d_pass" in requested_pages: self.d_pass_page(self.defensive_data); self.pages.append("Defense - Passing")
        if "d_boundary_strength" in requested_pages: self.d_boundary_strength_page(self.defensive_data); self.pages.append("Defense Field Boundary & Formation Strength")
        if "d_fieldPos" in requested_pages: self.d_field_position(self.defensive_data); self.pages.append("Defense - Field Position")
        if "d_situational_redzone" in requested_pages: self.d_redzone_page(self.offensive_data); self.pages.append("Defense Situational - Redzone") 
        if "d_situational_1" in requested_pages: self.d_down_1_page(self.offensive_data); self.pages.append("Defense Situational - 1st Down")
        if "d_situational_2" in requested_pages: self.d_down_2_page(self.offensive_data); self.pages.append("Defense Situational - 2nd Down")
        if "d_situational_3" in requested_pages: self.d_down_3_page(self.offensive_data); self.pages.append("Defense Situational - 3rd Down")
        if "d_situational_4" in requested_pages: self.d_down_4_page(self.offensive_data); self.pages.append("Defense Situational - 4th Down")

        ## These are called last to push in front of other pages.
        self.overview_page()
        self.title_page()

    def template_to_pdf(self, html, appendToFront: bool = False) -> None:
        # Used for ease of development
        if sys.platform.startswith('win'):
            pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='dependencies/wkhtmltopdf.exe'))
        # Means it is being run on docker docker jr docker
        else:
            pdf = pdfkit.from_string(html, False)
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf))
        
        if appendToFront: self.pdfs.insert(0, pdf_reader)
        else: self.pdfs.append(pdf_reader)
        
    def combine_reports(self) -> None:
        return combine_pdf_pages(self.pdfs)

    def title_page(self) -> None:
        title_template = env.get_template('pregame_report/report_pages/title/title_page.html')
        html = title_template.render(title="Pregame Report", team=self.team_of_interest, games = self.game_data.to_dict(orient='records'), current_year = datetime.datetime.now().year)
        # Render this sucker!
        self.template_to_pdf(html, True)
    
    def overview_page(self) -> None:
        overview_page = env.get_template('pregame_report/report_pages/overview/overview_page.html')
        html = overview_page.render(pages = self.pages)
        self.template_to_pdf(html, True)

    def o_overview(self, data: pd.DataFrame) -> None:
        """Overview of an opponents offense
        """
        if len(data) == 0: return
        try:       
            offense_overview_page = env.get_template('pregame_report/report_pages/offense_overview/offense_overview.html')
            html = offense_overview_page.render(
                opponent_qbr = calculate_qbr(data),
                efficiency_data = get_efficiencies(data), 
                yardage_data = breakdown_yardage(data), 
                team = self.team_of_interest, 
                play_type_chart = categorical_pieChart_wrapper(data, "Play_Type", "Frequency of Plays Ran"),
                formation_chart = categorical_pieChart_wrapper(data, "O_Formation", "Frequency of Formations"),
                point_data = points_package(data, self.team_of_interest, self.game_data)
            )
            self.template_to_pdf(html)
        except Exception as e:
            print(e)
        
    def o_play_type_personnel_page(self, data: pd.DataFrame) -> None:
        """Overview of opponents offense through Personnel & Formation
        """
        if len(data) == 0: return
        try:
            data.rename({"O_Formation": "Formation"})
            #Prep Personnel
            personnel_playType= crossTabQuery(data.Personnel, data.Play_Type)
            personnel_pie_chart_data = group_by_df(data, "Personnel")
            personnel_chart = categorical_pieChart("Frequency of Personnel Groups", personnel_pie_chart_data)

            formation_playType = crossTabQuery(data.Formation, data.Play_Type)
            formation_pie_chart_data = group_by_df(data, "Formation")
            formation_chart = categorical_pieChart("Frequency of Formations", formation_pie_chart_data)

            bar_plot = groupedBarGraph(data, "Formation", "Play_Type", "Play Type")

            offense_overview_page = env.get_template('pregame_report/report_pages/offense_playType/playType_personnel.html')
            html = offense_overview_page.render(team = self.team_of_interest, personnel_playType = personnel_playType, formation_playType = formation_playType, personnel_chart = personnel_chart, formation_chart = formation_chart, bar_plot = bar_plot)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_play_type_downDistance_page(self, data: pd.DataFrame) -> None:
        """Overview of opponents offense through Personnel & Formation
        """
        if len(data) == 0: return
        try:
            data.rename({"O_Formation": "Formation"})
            down_playType = crossTabQuery(data.Down, data.Play_Type)
            distance_playType = crossTabQuery(data.Down_Group, data.Play_Type)
            bar_plot = groupedBarGraph(data, "Down", "Play_Type", "Play Type")

            ridge_plot = create_ridge_plot(data, "Play_Type", "Distance", "Play_Type")
            offense_overview_page = env.get_template('pregame_report/report_pages/offense_playType/playType_downDistance.html')
            html = offense_overview_page.render(team = self.team_of_interest, down_playType = down_playType, distance_playType = distance_playType, ridge_plot = ridge_plot, bar_plot = bar_plot)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_play_type_field_page(self, data: pd.DataFrame) -> None:
        if len(data) == 0: return
        try:
            data["Play_Detail"] = data["Play_Type"] + "-" + data["Play_Type_Dir"]
            play_type_map = FieldZone_PieChart(data, "Play_Type", "Play Type by Field Position").create_graph()
            play_type_hash = crossTabQuery(data.Hash, data.Play_Type)
            play_detail_hash = crossTabQuery(data.Hash, data.Play_Detail)
            bar_plot = groupedBarGraph(data, "Field_Group", "Play_Type", "Play Type by Field Position")
            offense_overview_page = env.get_template('pregame_report/report_pages/offense_playType/playType_field.html')
            html = offense_overview_page.render(team = self.team_of_interest, play_type_map = play_type_map, play_detail_hash = play_detail_hash, play_type_hash = play_type_hash, play_type_bar = bar_plot)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_strength_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            data_trim = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown'])]
            strength_chart_data = group_by_df(data_trim, "To_Strength")
            strength_chart = categorical_pieChart("Frequency of Plays to Formation Strength", strength_chart_data, True)
            strength_form_bar_plot = groupedBarGraph(data_trim, "Formation", "To_Strength", "Plays to Strength by Formation")
            strength_personnel_bar_plot = groupedBarGraph(data_trim, "Personnel", "To_Strength", "Plays to Strength by Personnel")
            strength_playType_bar_plot = groupedBarGraph(data_trim, "Play_Type", "To_Strength", "Play Type to Strength by Formation")
            pressure_into_strength = crossTabQueryAgg(data.Pressure_Into_Strength, data.Formation, data.Result, 'mean')
            pressure_into_strength = pressure_into_strength.rename({'Pressure_Into_Strength': 'Pressure into Strength of Formation'})
            pressure_away_strength = crossTabQueryAgg(data.Pressure_Away_Strength, data.Formation, data.Result, 'mean')
            offense_overview_page = env.get_template('pregame_report/report_pages/offense_playType/playType_strength.html')
            html = offense_overview_page.render(team = self.team_of_interest, pressure_into_strength = pressure_into_strength, pressure_away_strength = pressure_away_strength,  strength_chart = strength_chart, strength_form_bar_plot = strength_form_bar_plot, strength_playType_bar_plot = strength_playType_bar_plot, strength_personnel_bar_plot = strength_personnel_bar_plot)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_ball_carrier_overview_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            data = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown', 'Boot Pass'])]
            data["Play_Detail"] = data["Play_Type"] + "-" + data["Play_Type_Dir"]
            ball_carrier_data = ball_carrier_package(data)
            formation_ball_carrier_bar_plot = groupedBarGraph(data, "Formation", "Ball_Carrier", "Ball Carrier by Formation")
            personnel_ball_carrier_bar_plot = groupedBarGraph(data, "Personnel", "Ball_Carrier", "Ball Carrier by Personnel Group")
            ball_carrier_playType = crossTabQuery(data.Ball_Carrier, data.Play_Detail)
            o_ball_carrier_overview_page = env.get_template('pregame_report/report_pages/offense_ballCarrier/ball_carrier_overview.html')
            html = o_ball_carrier_overview_page.render(team = self.team_of_interest,  ball_carrier_data = ball_carrier_data, formation_ball_carrier_bar_plot=formation_ball_carrier_bar_plot, personnel_ball_carrier_bar_plot=personnel_ball_carrier_bar_plot, ball_Carrier_playType = ball_carrier_playType)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_ball_carrier_detail_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            data = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown', 'Boot Pass'])]
            ball_carrier_distance_ridge_plot = create_ridge_plot(data, "Ball_Carrier", "Distance", "Ball_Carrier")
            ball_carrier_field_position_ridge_plot = create_ridge_plot(data, "Ball_Carrier", "Yard", "Ball_Carrier")
            ball_carrier_by_hash = crossTabQuery(data.Ball_Carrier, data.Hash)
            ball_carrier_by_down = crossTabQuery(data.Ball_Carrier, data.Down)
            o_ball_carrier_detail_page = env.get_template('pregame_report/report_pages/offense_ballCarrier/ball_carrier_detail.html')
            html = o_ball_carrier_detail_page.render(team = self.team_of_interest, ball_carrier_distance_ridge_plot = ball_carrier_distance_ridge_plot, ball_carrier_field_position_ridge_plot= ball_carrier_field_position_ridge_plot, ball_carrier_by_down = ball_carrier_by_down, ball_carrier_by_hash = ball_carrier_by_hash)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_boundary_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            data['Into_Boundary'] = data['Play_Type_Dir'] == data['Hash']
            data_left = data[data["Hash"] == 'Left']
            data_right = data[data["Hash"] == 'Right']
            left_into_boundary_chart = categorical_pieChart_wrapper(data_left, "Into_Boundary", "Frequency of Plays to Formation Strength", True, useOther=False)
            right_into_boundary_chart = categorical_pieChart_wrapper(data_right, "Into_Boundary", "Frequency of Plays to Formation Strength", True, useOther=False)
            data_left_trim = data_left[~data_left["Play_Type"].isin(['Pocket Pass', 'Unknown', "Boot Pass"])]
            data_right_trim = data_right[~data_right["Play_Type"].isin(['Pocket Pass', 'Unknown', "Boot Pass"])]
            left_strength_boundary_chart = categorical_pieChart_wrapper(data_left_trim, "To_Strength", "Ran Ball to Strength of Formation", True, useOther=False)
            right_strength_boundary_chart = categorical_pieChart_wrapper(data_right_trim, "To_Strength", "Ran Ball to Strength of Formation", True, useOther=False)
            left_play_type_by_down = crossTabQuery(data_left.Down, data_left.Play_Type)
            right_play_type_by_down = crossTabQuery(data_right.Down, data_right.Play_Type)
            data_left_passZone = group_by_df(data_left, 'Pass_Zone')
            data_left_passZone_graph = PassZone(data_left_passZone, 'Value', number_of_classes=3).create_graph()
            data_right_passZone = group_by_df(data_right, 'Pass_Zone')
            data_right_passZone_graph = PassZone(data_right_passZone, 'Value', number_of_classes=3).create_graph()
            boundary_overview_page = env.get_template('pregame_report/report_pages/offensive_boundary/boundary_overview.html')
            html = boundary_overview_page.render(team = self.team_of_interest, left_into_boundary_chart = left_into_boundary_chart, right_into_boundary_chart = right_into_boundary_chart, left_play_type_by_down = left_play_type_by_down, right_play_type_by_down = right_play_type_by_down, left_strength_boundary_chart = left_strength_boundary_chart, right_strength_boundary_chart = right_strength_boundary_chart, data_left_passZone_graph = data_left_passZone_graph, data_right_passZone_graph = data_right_passZone_graph)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_passing_overview_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
            data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
            data['Complete_Pass'] = (~data['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (data["Result"] != 0)

            data_passing_overview = passing_package(data)
            pass_zone_by_down = crossTabQuery(data.Down, data.Pass_Zone)


            pass_zone_chart_data = group_by_df(data, "Pass_Zone")
            pass_zone_chart_pie = categorical_pieChart("Overall Pass Zone Breakdown", pass_zone_chart_data)

            pass_zone_by_formation = crossTabQuery(data.Formation, data.Pass_Zone)
            pass_zone_by_personnel = crossTabQuery(data.Personnel, data.Pass_Zone)

            o_passing_overview_page = env.get_template('pregame_report/report_pages/offense_passing/offense_passing_overview.html')
            html = o_passing_overview_page.render(team = self.team_of_interest, data_passing_overview = data_passing_overview, pass_zone_by_down = pass_zone_by_down, pass_zone_by_formation = pass_zone_by_formation, pass_zone_by_personnel = pass_zone_by_personnel, pass_zone_chart_pie=pass_zone_chart_pie)
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_passing_detail_page(self, data: pd.DataFrame):
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        if len(data) == 0: return
        try: 
            data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
            data['Did_Scramble'] = (data['Pass_Zone'].isin(['Non-Passing-Play'])) & (data["Result"] > 0)
            data['Non_Passing_Play'] = data['Did_Scramble'].map({True: 'Scramble', False: 'Sack'})
            pass_zone_distance_ridge_plot = create_ridge_plot(data, "Pass_Zone", "Distance", "Pass_Zone")
            pass_zone_map = FieldZone_PieChart(data, "Pass_Zone", "Pass Zones by Field Position").create_graph()
            o_passing_detail_page = env.get_template('pregame_report/report_pages/offense_passing/offense_passing_detail.html')

            thrown_passes = (data[data['Pass_Zone'] != 'Not Thrown'])
            thrown_passes['Complete_Pass'] = (~thrown_passes['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (thrown_passes["Result"] != 0)
            df_completions_group_by = thrown_passes.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: x.sum()).reset_index()
            df_qbr = thrown_passes.groupby("Pass_Zone").apply(calculate_qbr).reset_index()
            df_yards = thrown_passes.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: int((x.sum() / len(x)) * 100)).reset_index()
            data_passZone = group_by_df(data, 'Pass_Zone')

            df_yards.columns = ["Category", "Value"]
            df_qbr.columns = ["Category", "Value"]
            df_completions_group_by.columns = ["Category", "Value"]
            completion_chart = PassZone(df_completions_group_by, 'Value', number_of_classes=3, title="Completions Per Pass Zone").create_graph()
            yards_chart = PassZone(df_yards, 'Value', number_of_classes=3, title="Yards Per Pass Zone").create_graph()
            qbr_chart = PassZone(df_qbr, 'Value', number_of_classes=3, title="QBR Per Pass Zone").create_graph()
            pass_zone_chart = PassZone(data_passZone, 'Value', number_of_classes=3).create_graph()

            # df_qbr = thrown_passes.groupby("Pass_Zone").apply(calculate_qbr).reset_index()
            html = o_passing_detail_page.render(
                team = self.team_of_interest, 
                completion_chart = completion_chart,
                yards_chart = yards_chart,
                pass_zone_chart = pass_zone_chart,
                qbr_chart = qbr_chart,
                pass_zone_map = pass_zone_map
            )
            self.template_to_pdf(html)
        except Exception as e:
            print(e)

    def o_passing_targets_page(self, data: pd.DataFrame):
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        if len(data) == 0: return
        try:
            receiver_data = receiver_package(data)
            data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
            data['Did_Scramble'] = (data['Pass_Zone'].isin(['Non-Passing-Play'])) & (data["Result"] > 0)
            data['Non_Passing_Play'] = data['Did_Scramble'].map({True: 'Scramble', False: 'Sack'})
            data_slim = data[~data["Pass_Zone"].isin(['Unknown', 'Not Thrown'])]
            receiver_pass_zone = crossTabQuery(data_slim.Ball_Carrier, data_slim.Pass_Zone)
            personnel_receiver_bar_plot = groupedBarGraph(data_slim, "Personnel", "Ball_Carrier", "Targeted Receiver by Formation")
            o_passing_detail_page = env.get_template('pregame_report/report_pages/offense_passing/offense_passing_passZone_targets.html')
            html = o_passing_detail_page.render(team = self.team_of_interest, receiver_data = receiver_data, receiver_pass_zone = receiver_pass_zone, personnel_receiver_bar_plot = personnel_receiver_bar_plot)
            self.template_to_pdf(html)        
        except Exception as e:
            print(e)

    def o_redzone_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            redzone_data = subset_redzone_data(data)
            redzone_data_detail_position = crossTabQuery(redzone_data.Redzone_Position, redzone_data.Play_Type)
            redzone_data_detail_down = crossTabQuery(redzone_data.Down, redzone_data.Play_Type)
            personnel_pie_chart_data = group_by_df(data, "Personnel")
            personnel_chart = categorical_pieChart("Frequency of Personnel Groups", personnel_pie_chart_data)
            formation_pie_chart_data = group_by_df(data, "Formation")
            formation_chart = categorical_pieChart("Frequency of Formations", formation_pie_chart_data)
            redzone_data_detail_formation = crossTabQuery(redzone_data.Formation, redzone_data.Play_Type)
            redzone_data_detail_personnel = crossTabQuery(redzone_data.Personnel, redzone_data.Play_Type)
            o_redzone_page = env.get_template('pregame_report/report_pages/offense_situational/offense_redzone.html')
            html = o_redzone_page.render(team = self.team_of_interest, redzone_data_detail_position = redzone_data_detail_position, redzone_data_detail_down = redzone_data_detail_down, personnel_chart = personnel_chart, formation_chart = formation_chart,redzone_data_detail_formation = redzone_data_detail_formation, redzone_data_detail_personnel= redzone_data_detail_personnel )
            self.template_to_pdf(html)   
        except Exception as e:
            print(e)

    def o_down_page(self, data: pd.DataFrame, situation: str):
        """Abstraction of O Down Pages (1, 2, 3)"""
        if len(data) == 0: return
        try:
            data["Detailed_Field_Group"] = data["Field_Group"] + "-" + data["Hash"]
            play_type_by_down_group = crossTabQuery(data.Down_Group, data.Play_Type)
            personnel_pie_chart = categorical_pieChart_wrapper(data, "Personnel", "Personnel Frequency")
            formation_pie_chart = categorical_pieChart_wrapper(data, "Formation", "Formation Frequency")
            play_pie_chart = categorical_pieChart_wrapper(data, "Play_Type", "Play Frequency", useOther=False)
            o_passing_detail_page = env.get_template('pregame_report/report_pages/offense_situational/offense_base_situation.html')
            situational_dict = get_situational_efficiencies(data)
            html = o_passing_detail_page.render(team = self.team_of_interest, situation = situation, situational_dict = situational_dict, play_type_by_down_group = play_type_by_down_group, personnel_pie_chart = personnel_pie_chart, formation_pie_chart = formation_pie_chart, play_pie_chart = play_pie_chart)
            self.template_to_pdf(html)  
        except Exception as e:
            print(e)

    def o_down_1_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.o_down_page(data[data["Down"] == 1], "1st Down")

    def o_down_2_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.o_down_page(data[data["Down"] == 2], "2nd Down")

    def o_down_3_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.o_down_page(data[data["Down"] == 3], "3rd Down")

    def o_down_4_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.o_down_page(data[data["Down"] == 4], "4th Down")

    def d_overview(self, data: pd.DataFrame) -> None:
        """Overview of an opponents defense
        """
        if len(data) == 0: return
        coverage_pie_chart_data = group_by_df(data, "Coverage_Type")
        d_formation_pie_chart_data = group_by_df(data, "D_Formation")
        defense_overview_page = env.get_template('pregame_report/report_pages/defense/defense_overview.html')
        html = defense_overview_page.render(
            team = self.team_of_interest,
            coverage_chart = categorical_pieChart("Variety of Coverage", coverage_pie_chart_data), 
            d_formation_chart = categorical_pieChart("Variety of D-Formation", d_formation_pie_chart_data),
            d_yards_data = d_yards_package(data), 
            d_overview_dict = d_overview_package(data, self.team_of_interest, self.game_data)
        )
        self.template_to_pdf(html)

    def d_formation_personnel(self, data: pd.DataFrame) -> None:
        """Overview of an opponents defense
        """
        if len(data) == 0: return
        defense_formation_personnel_page = env.get_template('pregame_report/report_pages/defense/defense_formation_personnel.html')
        html = defense_formation_personnel_page.render(
            team = self.team_of_interest, 
            formation_bar_chart = groupedBarGraph(data, "Formation", "Coverage", "Coverage"),
            personnel_bar_chart = groupedBarGraph(data, "Personnel", "Coverage", "Coverage"),
            coverage_pie_chart = categorical_pieChart_wrapper(data, "Coverage", "Coverage Baseline", True, False),
            pressure_pie_chart = categorical_pieChart_wrapper(data, "Pressure_Existence", "Pressure Baseline", True, True),
            pressure_formation_bar = stackedBarGraph(data, 'Formation', ['Pressure_Left', 'Pressure_Middle', 'Pressure_Right'], 'Pressure by Formation', include_total_plays = True, total_plays_label = 'No Pressure')
        )
        self.template_to_pdf(html)    

    def d_formation_down_distance(self, data: pd.DataFrame) -> None:
        if len(data) == 0: return
        try:
            defense_formation_down_page_page = env.get_template('pregame_report/report_pages/defense/defense_down_distance.html')
            html = defense_formation_down_page_page.render(
                team = self.team_of_interest, 
                distance_playType_data = crossTabQuery(data.Down_Group, data.Coverage),
                coverage_distance_plot = create_ridge_plot(data, "Coverage", "Distance", "Coverage"),
                pressure_distance_plot = create_ridge_plot(data, "Pressure_Existence", "Distance", "Pressure_Existence"),
                pressure_down_bar = stackedBarGraph(data, 'Down', ['Pressure_Left', 'Pressure_Middle', 'Pressure_Right'], 'Pressure by Down', include_total_plays = True, total_plays_label = 'No Pressure')
            )
            self.template_to_pdf(html)          
        except Exception as e:
            print(e)
        
    def d_pass_page(self, data: pd.DataFrame) -> None:
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        if len(data) == 0: return
        try:
            data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
            data['Sack'] = (data["Pass_Zone"] == 'Not Thrown') & (data["Result"] < 0)
            data['Did_Scramble'] = (data['Pass_Zone'] == 'Not Thrown') & (data["Result"] > 0)
            thrown_passes = (data[data['Pass_Zone'] != 'Not Thrown'])
            thrown_passes['Complete_Pass'] = (~thrown_passes['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (thrown_passes["Result"] != 0)
            
            df_completions = (thrown_passes[thrown_passes['Complete_Pass'] != False])
            df_completions_group_by = thrown_passes.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: x.sum()).reset_index()
            # df_qbr = thrown_passes.groupby("Pass_Zone").apply(calculate_qbr).reset_index()
            df_yards = thrown_passes.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: int((x.sum() / len(x)) * 100)).reset_index()
            df_yards.columns = ["Category", "Value"]
            df_completions_group_by.columns = ["Category", "Value"]
            defense_pass_page = env.get_template('pregame_report/report_pages/defense/defense_passing.html')
            html = defense_pass_page.render(
                team = self.team_of_interest,
                d_passing_data = d_passing_pack(thrown_passes),
                pass_zone_chart = PassZone(df_completions_group_by, 'Value', number_of_classes=3, title="Completions Per Pass Zone").create_graph(),
                pass_zone_yards_chart = PassZone(df_yards, 'Value', number_of_classes=3, legend_labels=['Low Completion %', 'Medium Completion %', 'High Completion %'], title="Completion Percentage Per Pass Zone").create_graph(),
                pass_zone_distance = groupedBarGraph(df_completions, "Down_Group", "Pass_Zone", "Completions by Distance"),
                d_sack_chart = categorical_pieChart("Sack Rate", group_by_df(data, "Sack", False), True),
                d_scramble_chart = categorical_pieChart("Successful Scrambles", group_by_df(data, "Did_Scramble", False), True),
                d_formation_data = d_formation_pack(thrown_passes)
            )
            self.template_to_pdf(html)            
        except Exception as e:
            print(e)
    def d_boundary_strength_page(self, data: pd.DataFrame) -> None:
        if len(data) == 0: return
        try:
            data_left = data[data["Hash"] == 'Left']
            data_right = data[data["Hash"] == 'Right']
            defense_overview_page = env.get_template('pregame_report/report_pages/defense/defense_strength_boundary.html')
            html = defense_overview_page.render(
                team = self.team_of_interest,
                left_pie_into_p_left = categorical_pieChart_wrapper(data_left, "Pressure_Left", "Pressure from Boundary (left)", True, useOther=False),
                left_pie_into_p_middle = categorical_pieChart_wrapper(data_left, "Pressure_Middle", "Pressure from Middle", True, useOther=False),
                left_pie_into_p_right = categorical_pieChart_wrapper(data_left, "Pressure_Right", "Pressure from Wide-side (right)", True, useOther=False),
                right_pie_into_p_left = categorical_pieChart_wrapper(data_right, "Pressure_Right", "Pressure from Boundary (right)", True, useOther=False),
                right_pie_into_p_middle = categorical_pieChart_wrapper(data_right, "Pressure_Middle", "Pressure from Middle", True, useOther=False),
                right_pie_into_p_right = categorical_pieChart_wrapper(data_right, "Pressure_Left", "Pressure from Wide-side (left)", True, useOther=False),
                left_bar_plot = groupedBarGraph(data_left, "Formation", "Pressure_Existence", "Pressure by Formation (left)"),
                right_bar_plot = groupedBarGraph(data_right, "Formation", "Pressure_Existence", "Pressure by Formation (right)"),
                left_strength_bar_plot = groupedBarGraph(data_left, "Formation", "Pressure_Into_Strength", "Pressure by into Strength of Formation (left)"),
                right_strength_bar_plot = groupedBarGraph(data_right, "Formation", "Pressure_Into_Strength", "Pressure by into Strength of Formation (right)")
            )
            self.template_to_pdf(html)  
        except Exception as e:
            print(e)

    def d_field_position(self, data: pd.DataFrame) -> None:
        if len(data) == 0: return
        try:
            defense_overview_page = env.get_template('pregame_report/report_pages/defense/defense_field_position.html')
            html = defense_overview_page.render(
                team = self.team_of_interest,
                field_zone_coverage = FieldZone_PieChart(data, 'Coverage', 'Coverage by Field Position').create_graph(),
                field_zone_pressure = FieldZone_PieChart(data, 'Pressure_Existence', 'Any Pressure by Field Position', True).create_graph(),
            )
            self.template_to_pdf(html)  
        except Exception as e:
            print(e)

    def d_down_page(self, data: pd.DataFrame, title: str) -> None:
        if len(data) == 0: return
        try:
            pressure_down_group_bar = stackedBarGraph(data, 'Down_Group', ['Pressure_Left', 'Pressure_Middle', 'Pressure_Right'], 'Pressure by Distance to First Down', include_total_plays = True, total_plays_label = 'No Pressure')
            defense_overview_page = env.get_template('pregame_report/report_pages/defense/defense_base_situational.html')
            d_yards_data = d_yards_package(data)
            d_yards_data = d_yards_data[d_yards_data["Play Type"].isin(['Inside Run', 'Outside Run', 'Pocket Pass', 'Boot Pass'])]
            html = defense_overview_page.render(
                team = self.team_of_interest,
                title = title,
                count = len(data), 
                coverage_by_down_group = crossTabQuery(data.Down_Group, data.Coverage),
                pressure_pie_chart = categorical_pieChart_wrapper(data, "Pressure_Existence", "Pressure Frequency", isBooleanGraph=True),
                coverage_pie_chart = categorical_pieChart_wrapper(data, "Coverage", "Coverage Frequency"),
                pressure_down_group_bar = pressure_down_group_bar,
                d_yards_data = d_yards_data
            )
            self.template_to_pdf(html)          
        except Exception as e:
            print(e)

    def d_down_1_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.d_down_page(data[data["Down"] == 1], "1st Down")

    def d_down_2_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.d_down_page(data[data["Down"] == 2], "2nd Down")

    def d_down_3_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.d_down_page(data[data["Down"] == 3], "3rd Down")

    def d_down_4_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        self.d_down_page(data[data["Down"] == 4], "4th Down")

    def d_redzone_page(self, data: pd.DataFrame):
        if len(data) == 0: return
        try:
            redzone_data = subset_redzone_data(data)
            pressure_down_bar = stackedBarGraph(redzone_data, 'Down', ['Pressure_Left', 'Pressure_Middle', 'Pressure_Right'], 'Pressure by Down', include_total_plays = True, total_plays_label = 'No Pressure')
            pressure_redzone_bar = stackedBarGraph(redzone_data, 'Redzone_Position', ['Pressure_Left', 'Pressure_Middle', 'Pressure_Right'], 'Pressure by Redzone Position', include_total_plays = True, total_plays_label = 'No Pressure')
            d_redzone_page = env.get_template('pregame_report/report_pages/defense/defense_redzone_situational.html')
            html = d_redzone_page.render(
                team = self.team_of_interest, 
                count = len(redzone_data),
                redzone_data_detail_position_coverage = crossTabQuery(redzone_data.Redzone_Position, redzone_data.Coverage),
                redzone_data_detail_down_coverage = crossTabQuery(redzone_data.Down, redzone_data.Coverage),
                pressure_pie_chart = categorical_pieChart_wrapper(data, "Pressure_Existence", "Pressure Frequency", isBooleanGraph=True),
                coverage_pie_chart = categorical_pieChart_wrapper(data, "Coverage", "Coverage Frequency"),
                pressure_redzone_bar = pressure_redzone_bar,
                pressure_down_bar = pressure_down_bar
            )
            self.template_to_pdf(html)   
        except Exception as e:
            print(e)

    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        self.game_data = pd.read_sql(session.query(Game).filter(Game.Team_Code == self.team_code).filter(Game.Game_ID.in_(self.game_ids)).statement, db_engine)
        self.game_data['Game_Date'] = pd.to_datetime(self.game_data['Game_Date'])
        self.game_data['Game_Date'] = self.game_data['Game_Date'].dt.strftime('%A, %d %B %Y')
        # Team Code is linked via team_code
        df_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID.in_(self.game_ids)).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Team_Code == self.team_code).statement, db_engine)
        df_plays = pd.merge(df_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')

        self.play_data = pd.merge(df_plays, self.game_data, on='Game_ID', how='inner')
        
    def split_data(self) -> None:
        defense = self.play_data[(self.play_data["Possession"] != self.team_of_interest)]
        offense = self.play_data[(self.play_data["Possession"] == self.team_of_interest)]
        self.offensive_data = enrich_data(offense, self.team_of_interest)
        self.defensive_data = enrich_data(defense, self.team_of_interest)


if __name__ == "__main__":
    test = PregameReport()