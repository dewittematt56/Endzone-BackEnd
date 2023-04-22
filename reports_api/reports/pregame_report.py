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

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')




class PregameReport():
    def __init__(self) -> None:
        self.pdfs = []
        self.team_of_interest = "Eastview"
        self.squad_code = "Endzone-System"
        self.game_ids = ["54751ec7-176a-4604-94f9-1d4bf6023fa4"]
        self.pages = ["Overview", "Play Type Personnel", "Play Type Down", "Play Type Field"]
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

    def template_to_pdf(self, html) -> None:
        pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
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
        #Prep Personnel
        down_playType = crossTabQuery(data.Down, data.Play_Type)
        distance_playType = crossTabQuery(data.Down_Group, data.Play_Type)
        down_personnel = crossTabQuery(data.Down, data.Personnel)
        distance_personnel = crossTabQuery(data.Down, data.Personnel)
        bar_plot = groupedBarGraph(data, "Down", "Play_Type", "Play Type")
        #formation_chart = categorical_pieChart("Frequency of Formations", personnel_pie_chart_data)

        ridge_plot = create_ridge_plot(data, "Play_Type", "Distance", "Play_Type")
        offense_overview_page = env.get_template('report_pages/offense_playType/playType_downDistance.html')
        html = offense_overview_page.render(team = self.team_of_interest, down_playType = down_playType, distance_playType = distance_playType, ridge_plot = ridge_plot, bar_plot = bar_plot)
        self.template_to_pdf(html)

    def play_type_field_page(self, data: pd.DataFrame) -> None:
        play_type_map = create_field_map(data, "Result_X", "Result_Y", "Play_Type")

        offense_overview_page = env.get_template('report_pages/offense_playType/playType_field.html')
        html = offense_overview_page.render(team = self.team_of_interest, play_type_map = play_type_map)
        self.template_to_pdf(html)


    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        self.game_data = pd.read_sql(session.query(Game).filter(Game.Squad_Code == self.squad_code).filter(Game.Game_ID.in_(self.game_ids)).statement, db_engine)
        self.game_data['Game_Date'] = self.game_data['Game_Date'].dt.strftime('%A, %d %B %Y')
        # Squad Code is linked via team_code
        df_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID.in_(self.game_ids)).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Squad_Code == self.squad_code).statement, db_engine)
        df_plays = pd.merge(df_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')
        self.play_data = pd.merge(df_plays, self.game_data, on='Game_ID', how='inner')
        
    def split_data(self) -> None:
        defense = self.play_data[(self.play_data["Possession"] != self.team_of_interest)]
        offense = self.play_data[(self.play_data["Possession"] == self.team_of_interest)]
        self.offensive_data = enrich_data(offense, self.team_of_interest)
        self.defensive_data = enrich_data(defense, self.team_of_interest)


if __name__ == "__main__":
    test = PregameReport()