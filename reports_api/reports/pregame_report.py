from io import BytesIO
from .utils import *
import pandas as pd
import jinja2
import pdfkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import PyPDF2
from database.db import db_uri 
from database.models import *
import io
import numpy as np
from .base_report_utils import *
from .spatial_utils import *

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')

class PregameReport():
    def __init__(self) -> None:
        self.pdfs = []
        self.team_of_interest = "Eastview"
        self.team_code = "Endzone-System"
        self.game_ids = ["f492782c-a04f-43f6-af18-65d51d033803"]
        self.pages = ["Overview", "Play Type Personnel", "Play Type Down", "Play Type Field", "Strength of Formation", "Ball Carrier Overview", "Ball Carrier Detailed", "Passing Overview", "Passing Detail", "Passing Targets", "Redzone Situational"]
        self.pdf_write = PyPDF2.PdfWriter()
        # Get game-based & play-based data from database.
        self.get_data()
        self.split_data()
        self.title_page()
        self.overview_page()
        self.offense_overview(self.offensive_data)
        self.play_type_personnel_page(self.offensive_data)
        self.play_type_downDistance_page(self.offensive_data)
        self.play_type_field_page(self.offensive_data) 
        self.strength_page(self.offensive_data)
        self.ball_carrier_overview_page(self.offensive_data)
        self.ball_carrier_detail_page(self.offensive_data)
        self.boundary_page(self.offensive_data)
        self.passing_overview_page(self.offensive_data)
        self.passing_detail_page(self.offensive_data)
        self.passing_targets_page(self.offensive_data)
        self.o_redzone_page(self.offensive_data)
        self.o_down_1_page(self.offensive_data)
        self.o_down_2_page(self.offensive_data)
        self.o_down_3_page(self.offensive_data)

    def template_to_pdf(self, html) -> None:
        pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='reports_api\wkhtmltopdf.exe'))
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf))
        self.pdfs.append(pdf_reader)

    def combine_reports(self) -> None:
        return combine_pdf_pages(self.pdfs)

    def title_page(self) -> None:
        title_template = env.get_template('report_pages/title/title_page.html')
        html = title_template.render(title="Pregame Report", team="Eastview", games = self.game_data.to_dict(orient='records'))
        # Render this sucker!
        self.template_to_pdf(html)
    
    def overview_page(self) -> None:
        overview_page = env.get_template('report_pages/overview/overview_page.html')
        html = overview_page.render(pages = self.pages)
        self.template_to_pdf(html)

    def offense_overview(self, data: pd.DataFrame) -> None:
        """Overview of an opponents offense
        """
        efficiency_dict = get_efficiencies(data)
        yardage_dict = breakdown_yardage(data)
        play_type_pie_chart_data = group_by_df(data, "Play_Type")
        play_type_chart = categorical_pieChart("Frequency of Plays Ran", play_type_pie_chart_data)
        offense_overview_page = env.get_template('report_pages/offense_overview/offense_overview.html')
        html = offense_overview_page.render(efficiency_data = efficiency_dict, yardage_data = yardage_dict, team = self.team_of_interest, play_type_chart = play_type_chart)
        self.template_to_pdf(html)

    def play_type_personnel_page(self, data: pd.DataFrame) -> None:
        """Overview of opponents offense through Personnel & Formation
        """
        data.rename({"O_Formation": "Formation"})
        #Prep Personnel
        personnel_playType= crossTabQuery(data.Personnel, data.Play_Type)
        personnel_pie_chart_data = group_by_df(data, "Personnel")
        personnel_chart = categorical_pieChart("Frequency of Personnel Groups", personnel_pie_chart_data)

        formation_playType = crossTabQuery(data.Formation, data.Play_Type)
        formation_pie_chart_data = group_by_df(data, "Formation")
        formation_chart = categorical_pieChart("Frequency of Formations", formation_pie_chart_data)

        bar_plot = groupedBarGraph(data, "Formation", "Play_Type", "Play Type")

        offense_overview_page = env.get_template('report_pages/offense_playType/playType_personnel.html')
        html = offense_overview_page.render(team = self.team_of_interest, personnel_playType = personnel_playType, formation_playType = formation_playType, personnel_chart = personnel_chart, formation_chart = formation_chart, bar_plot = bar_plot)
        self.template_to_pdf(html)

    def play_type_downDistance_page(self, data: pd.DataFrame) -> None:
        """Overview of opponents offense through Personnel & Formation
        """
        data.rename({"O_Formation": "Formation"})
        down_playType = crossTabQuery(data.Down, data.Play_Type)
        distance_playType = crossTabQuery(data.Down_Group, data.Play_Type)
        bar_plot = groupedBarGraph(data, "Down", "Play_Type", "Play Type")

        ridge_plot = create_ridge_plot(data, "Play_Type", "Distance", "Play_Type")
        offense_overview_page = env.get_template('report_pages/offense_playType/playType_downDistance.html')
        html = offense_overview_page.render(team = self.team_of_interest, down_playType = down_playType, distance_playType = distance_playType, ridge_plot = ridge_plot, bar_plot = bar_plot)
        self.template_to_pdf(html)

    def play_type_field_page(self, data: pd.DataFrame) -> None:
        data["Play_Detail"] = data["Play_Type"] + "-" + data["Play_Type_Dir"]

        play_type_map = create_xy_map(data, "Yard", "Hash", "Play_Type", "Result")
        play_type_hash = crossTabQuery(data.Hash, data.Play_Type)
        play_detail_hash = crossTabQuery(data.Hash, data.Play_Detail)

        bar_plot = groupedBarGraph(data, "Field_Group", "Play_Type", "Play Type by Field Position")

        offense_overview_page = env.get_template('report_pages/offense_playType/playType_field.html')
        html = offense_overview_page.render(team = self.team_of_interest, play_type_map = play_type_map, play_detail_hash = play_detail_hash, play_type_hash = play_type_hash, play_type_bar = bar_plot)
        self.template_to_pdf(html)

    def strength_page(self, data: pd.DataFrame):
        data_trim = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown'])]
        strength_chart_data = group_by_df(data_trim, "To_Strength")
        strength_chart = categorical_pieChart("Frequency of Plays to Formation Strength", strength_chart_data)
        strength_form_bar_plot = groupedBarGraph(data_trim, "Formation", "To_Strength", "Plays to Strength by Formation")
        strength_personnel_bar_plot = groupedBarGraph(data_trim, "Personnel", "To_Strength", "Plays to Strength by Personnel")
        strength_playType_bar_plot = groupedBarGraph(data_trim, "Play_Type", "To_Strength", "Play Type to Strength by Formation")
        pressure_into_strength = crossTabQueryAgg(data.Pressure_Into_Strength, data.Formation, data.Result, 'mean')
        pressure_into_strength = pressure_into_strength.rename({'Pressure_Into_Strength': 'Pressure into Strength of Formation'})
        pressure_away_strength = crossTabQueryAgg(data.Pressure_Away_Strength, data.Formation, data.Result, 'mean')
        offense_overview_page = env.get_template('report_pages/offense_playType/playType_strength.html')
        html = offense_overview_page.render(team = self.team_of_interest, pressure_into_strength = pressure_into_strength, pressure_away_strength = pressure_away_strength,  strength_chart = strength_chart, strength_form_bar_plot = strength_form_bar_plot, strength_playType_bar_plot = strength_playType_bar_plot, strength_personnel_bar_plot = strength_personnel_bar_plot)
        self.template_to_pdf(html)

    def ball_carrier_overview_page(self, data: pd.DataFrame):
        data = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown', 'Boot Pass'])]
        data["Play_Detail"] = data["Play_Type"] + "-" + data["Play_Type_Dir"]

        ball_carrier_data = ball_carrier_package(data)

        formation_ball_carrier_bar_plot = groupedBarGraph(data, "Formation", "Ball_Carrier", "Ball Carrier by Formation")
        personnel_ball_carrier_bar_plot = groupedBarGraph(data, "Personnel", "Ball_Carrier", "Ball Carrier by Personnel Group")
        ball_carrier_playType = crossTabQuery(data.Ball_Carrier, data.Play_Detail)
        ball_carrier_overview_page = env.get_template('report_pages/offense_ballCarrier/ball_carrier_overview.html')
        html = ball_carrier_overview_page.render(team = self.team_of_interest,  ball_carrier_data = ball_carrier_data, formation_ball_carrier_bar_plot=formation_ball_carrier_bar_plot, personnel_ball_carrier_bar_plot=personnel_ball_carrier_bar_plot, ball_Carrier_playType = ball_carrier_playType)
        self.template_to_pdf(html)

    def ball_carrier_detail_page(self, data: pd.DataFrame):
        data = data[~data["Play_Type"].isin(['Pocket Pass', 'Unknown', 'Boot Pass'])]
        ball_carrier_distance_ridge_plot = create_ridge_plot(data, "Ball_Carrier", "Distance", "Ball_Carrier")
        ball_carrier_field_position_ridge_plot = create_ridge_plot(data, "Ball_Carrier", "Yard", "Ball_Carrier")
        ball_carrier_by_hash = crossTabQuery(data.Ball_Carrier, data.Hash)
        ball_carrier_by_down = crossTabQuery(data.Ball_Carrier, data.Down)

        ball_carrier_detail_page = env.get_template('report_pages/offense_ballCarrier/ball_carrier_detail.html')
        html = ball_carrier_detail_page.render(team = self.team_of_interest, ball_carrier_distance_ridge_plot = ball_carrier_distance_ridge_plot, ball_carrier_field_position_ridge_plot= ball_carrier_field_position_ridge_plot, ball_carrier_by_down = ball_carrier_by_down, ball_carrier_by_hash = ball_carrier_by_hash)
        self.template_to_pdf(html)

    def boundary_page(self, data: pd.DataFrame):
        try:
            # Set Data
            data['Into_Boundary'] = data['Play_Type_Dir'] == data['Hash']
            data_left = data[data["Hash"] == 'Left']
            data_right = data[data["Hash"] == 'Right']

            left_into_boundary_chart = categorical_pieChart_wrapper(data_left, "Into_Boundary", "Frequency of Plays to Formation Strength")
            right_into_boundary_chart = categorical_pieChart_wrapper(data_right, "Into_Boundary", "Frequency of Plays to Formation Strength")

            data_left_trim = data_left[~data_left["Play_Type"].isin(['Pocket Pass', 'Unknown', "Boot Pass"])]
            data_right_trim = data_right[~data_right["Play_Type"].isin(['Pocket Pass', 'Unknown', "Boot Pass"])]
            left_strength_boundary_chart = categorical_pieChart_wrapper(data_left_trim, "To_Strength", "Ran Ball to Strength of Formation")
            right_strength_boundary_chart = categorical_pieChart_wrapper(data_right_trim, "To_Strength", "Ran Ball to Strength of Formation")

            left_play_type_by_down = crossTabQuery(data_left.Down, data_left.Play_Type)
            right_play_type_by_down = crossTabQuery(data_right.Down, data_right.Play_Type)

            data_left_passZone = group_by_df(data_left, 'Pass_Zone')
            data_left_passZone_graph = PassZone(data_left_passZone, 'Value', number_of_classes=3).create_graph()

            data_right_passZone = group_by_df(data_right, 'Pass_Zone')
            data_right_passZone_graph = PassZone(data_right_passZone, 'Value', number_of_classes=3).create_graph()
            
            boundary_overview_page = env.get_template('report_pages/offensive_boundary/boundary_overview.html')
            html = boundary_overview_page.render(team = self.team_of_interest, left_into_boundary_chart = left_into_boundary_chart, right_into_boundary_chart = right_into_boundary_chart, left_play_type_by_down = left_play_type_by_down, right_play_type_by_down = right_play_type_by_down, left_strength_boundary_chart = left_strength_boundary_chart, right_strength_boundary_chart = right_strength_boundary_chart, data_left_passZone_graph = data_left_passZone_graph, data_right_passZone_graph = data_right_passZone_graph)
            self.template_to_pdf(html)
        except KeyError:
            print('No Data')

    def passing_overview_page(self, data: pd.DataFrame):
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
        data['Complete_Pass'] = (~data['Pass_Zone'].isin(['Non-Passing-Play', 'Unknown'])) & (data["Result"] != 0)

        data_passing_overview = passing_package(data)
        pass_zone_by_down = crossTabQuery(data.Down, data.Pass_Zone)
        data_right_passZone = group_by_df(data, 'Pass_Zone')
        pass_zone_chart = PassZone(data_right_passZone, 'Value', number_of_classes=3).create_graph()



        pass_zone_chart_data = group_by_df(data, "Pass_Zone")
        pass_zone_chart_pie = categorical_pieChart("Overall Pass Zone Breakdown", pass_zone_chart_data)

        pass_zone_by_formation = crossTabQuery(data.Formation, data.Pass_Zone)
        pass_zone_by_personnel = crossTabQuery(data.Personnel, data.Pass_Zone)

        passing_overview_page = env.get_template('report_pages/offense_passing/offense_passing_overview.html')
        html = passing_overview_page.render(team = self.team_of_interest, data_passing_overview = data_passing_overview, pass_zone_by_down = pass_zone_by_down, pass_zone_by_formation = pass_zone_by_formation, pass_zone_by_personnel = pass_zone_by_personnel, pass_zone_chart_pie=pass_zone_chart_pie, pass_zone_chart=pass_zone_chart)
        self.template_to_pdf(html)

    def passing_detail_page(self, data: pd.DataFrame):
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
        data['Did_Scramble'] = (data['Pass_Zone'].isin(['Non-Passing-Play'])) & (data["Result"] > 0)
        data['Non_Passing_Play'] = data['Did_Scramble'].map({True: 'Scramble', False: 'Sack'})

        pass_zone_distance_ridge_plot = create_ridge_plot(data, "Pass_Zone", "Distance", "Pass_Zone")

        data_slim = data[~data["Pass_Zone"].isin(['Unknown', 'Not Thrown'])]
        pass_zone_map = create_xy_map(data_slim, "Yard", "Hash", "Pass_Zone", "Result")
        scramble_chart_data = group_by_df(data, "Non_Passing_Play")
        scramble_chart = categorical_pieChart("Frequency of Quarterback Scrambles", scramble_chart_data)

        passing_detail_page = env.get_template('report_pages/offense_passing/offense_passing_detail.html')
        html = passing_detail_page.render(team = self.team_of_interest, pass_zone_distance_ridge_plot = pass_zone_distance_ridge_plot, pass_zone_map = pass_zone_map)
        self.template_to_pdf(html)

    def passing_targets_page(self, data: pd.DataFrame):
        data = data[data["Play_Type"].isin(['Pocket Pass', 'Boot Pass'])]
        receiver_data = receiver_package(data)
        data['Pass_Zone'] = data['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
        data['Did_Scramble'] = (data['Pass_Zone'].isin(['Non-Passing-Play'])) & (data["Result"] > 0)
        data['Non_Passing_Play'] = data['Did_Scramble'].map({True: 'Scramble', False: 'Sack'})

        data_slim = data[~data["Pass_Zone"].isin(['Unknown', 'Not Thrown'])]

        receiver_pass_zone = crossTabQuery(data_slim.Ball_Carrier, data_slim.Pass_Zone)
        personnel_receiver_bar_plot = groupedBarGraph(data_slim, "Personnel", "Ball_Carrier", "Targeted Receiver by Formation")

        passing_detail_page = env.get_template('report_pages/offense_passing/offense_passing_passZone_targets.html')
        html = passing_detail_page.render(team = self.team_of_interest, receiver_data = receiver_data, receiver_pass_zone = receiver_pass_zone, personnel_receiver_bar_plot = personnel_receiver_bar_plot)
        self.template_to_pdf(html)        

    def o_redzone_page(self, data: pd.DataFrame):
        redzone_data = subset_redzone_data(data)
        
        redzone_data_detail_position = crossTabQuery(redzone_data.Redzone_Position, redzone_data.Play_Type)
        redzone_data_detail_down = crossTabQuery(redzone_data.Down, redzone_data.Play_Type)

        personnel_pie_chart_data = group_by_df(data, "Personnel")
        personnel_chart = categorical_pieChart("Frequency of Personnel Groups", personnel_pie_chart_data)
        formation_pie_chart_data = group_by_df(data, "Formation")
        formation_chart = categorical_pieChart("Frequency of Formations", formation_pie_chart_data)

        redzone_data_detail_formation = crossTabQuery(redzone_data.Formation, redzone_data.Play_Type)
        redzone_data_detail_personnel = crossTabQuery(redzone_data.Personnel, redzone_data.Play_Type)
        
        passing_detail_page = env.get_template('report_pages/offense_situational/offense_redzone.html')
        html = passing_detail_page.render(team = self.team_of_interest, redzone_data_detail_position = redzone_data_detail_position, redzone_data_detail_down = redzone_data_detail_down, personnel_chart = personnel_chart, formation_chart = formation_chart,redzone_data_detail_formation = redzone_data_detail_formation, redzone_data_detail_personnel= redzone_data_detail_personnel )
        self.template_to_pdf(html)   

    def o_down_1_page(self, data: pd.DataFrame):
        data_1 = data[data["Down"] == 1]
        data_1["Detailed_Field_Group"] = data_1["Field_Group"] + "-" + data_1["Hash"]
        play_type_by_down_group = crossTabQuery(data_1.Down_Group, data_1.Play_Type)
        left_strength_boundary_chart = categorical_pieChart_wrapper(data_1, "To_Strength", "Ran Ball to Strength of Formation")
        right_strength_boundary_chart = categorical_pieChart_wrapper(data_1, "To_Strength", "Ran Ball to Strength of Formation")


        # df_inside_run = data[data["Play_Type"] == "Inside Run"]
        # df_outside_run = data[data["Play_Type"] == "Outside Run"]
        # df_pass = data[(data["Play_Type"] == "Pocket Pass") | (data["Play_Type"] == "Boot Pass")]
        # data_inside_run_field_zone = FieldZone(group_by_df(df_inside_run, 'Detailed_Field_Group'), 'Value', number_of_classes=3, title="Field Map: Play Type - Inside Run").create_graph()
        # data_outside_run_field_zone = FieldZone(group_by_df(df_outside_run, 'Detailed_Field_Group'), 'Value', number_of_classes=3, title="Field Map: Play Type - Outside Run").create_graph()
        # data_pass_field_zone = FieldZone(group_by_df(df_outside_run, 'Detailed_Field_Group'), 'Value', number_of_classes=3, title="Field Map: Play Type - Outside Run").create_graph()

        passing_detail_page = env.get_template('report_pages/offense_situational/offense_down_1.html')
        html = passing_detail_page.render(team = self.team_of_interest, play_type_by_down_group = play_type_by_down_group)
        self.template_to_pdf(html)   

    def o_down_2_page(self, data: pd.DataFrame):
        passing_detail_page = env.get_template('report_pages/offense_situational/offense_down_2.html')
        html = passing_detail_page.render(team = self.team_of_interest)
        self.template_to_pdf(html)   

    def o_down_3_page(self, data: pd.DataFrame):
        passing_detail_page = env.get_template('report_pages/offense_situational/offense_down_3.html')
        html = passing_detail_page.render(team = self.team_of_interest)
        self.template_to_pdf(html)   

    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        self.game_data = pd.read_sql(session.query(Game).filter(Game.Team_Code == self.team_code).filter(Game.Game_ID.in_(self.game_ids)).statement, db_engine)
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