from io import BytesIO
import pandas as pd
import jinja2
import pdfkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import PyPDF2
from database.db import db_uri 
from database.models import *
from ..utils.spatial_utils import *
from ..utils.graphing_utils import *
from ..utils.utils import *
from ..utils.data_report_utils import *
import sys
from reports_api.reports.pregame_report.pregame_report import PregameReport
import os

env = jinja2.Environment(loader = jinja2.FileSystemLoader("./reports_api/reports"))

def get_down_group(distance: int) -> str:
    if distance <= 3: return "Short"
    elif distance > 3 and distance <= 6: return "Med"
    elif distance > 6: return "Long"
# TODO - Make function to take the play type and make it either pass or run. (option = run), convert any of the given play types to the simply run or pass. Add it to a column on the dataframe and call it "generic_play_type"
# TODO - Convert man or zone variations to simple man or zone
# TODO - do a cross tab query on the data. 
# TODO - Write a function that does certain field sections

def get_play_type(playType: str) -> pd.DataFrame:
    run_plays = ["Inside Run", "Outside Run", "Option"] # inside, outside, option
    pass_plays = ["Boot Pass", "Pocket Pass"]
    # zone_formations = ["Zone 2", "Zone 3", "Zone 4", "Prevent"]
    if playType in run_plays:
        return "Run"
    elif playType in pass_plays:
         return "Pass"
    else:
         return None
# Make separate function for the defense coverage
def get_coverage(coverage: str) -> pd.DataFrame:
    zone_formations = ["Zone 2", "Zone 3", "Zone 4"]
    man_formations = ["Man 0", "Man 1"]
    if coverage in zone_formations:
        return "Zone"
    elif coverage in man_formations:
        return "Man"
    else:
        return None
    
def prep_data(df: pd.DataFrame) -> pd.DataFrame:
    df["Down_Group"] = ""
    df["Thunderbolt_Play"] = ""
    df["Thunderbolt_Coverage"] = ""
    for index, row in df.iterrows():
        df.loc[index, "Down_Group"] = get_down_group(df.loc[index, "Distance"])
        df.loc[index, "Thunderbolt_Play"] = get_play_type(df.loc[index, "Play_Type"])
        df.loc[index, "Thunderbolt_Coverage"] = get_coverage(df.loc[index, "Coverage"])
    df["Thunderbolt_Down"] = df["Down"].astype(str) + " - " + df["Down_Group"]
    return df

def crossTabQuery(df_x: pd.Series, df_y: pd.Series, down: str, report_type: str) -> pd.DataFrame:
    index_values = [] 
    column_values = []
    if down == 1: index_values = ['1 - Short', '1 - Med', '1 - Long'] 
    elif down == 2: index_values = ['2 - Short', '2 - Med', '2 - Long'] 
    elif down == 3: index_values = ['3 - Short', '3 - Med', '3 - Long'] 
    if report_type == 'Offense':
        column_values = ['Pass', 'Run']
    elif report_type == 'Defense':
        column_values = ['Man', 'Zone']
    crossTab = pd.crosstab(df_x, df_y, normalize="index")
    crossTab = crossTab * 100
    crossTab = crossTab.reindex(index_values, columns = column_values, fill_value=0)
    crossTab.reset_index(inplace=True)
    return crossTab


class PostgameReport():
    def __init__(self, team_of_interest: str, gameId: str, user_team_code: str) -> None: 
        self.team_of_interest = team_of_interest
        self.gameId = gameId
        self.user_team_code = user_team_code # Temp, placeholders, remove later
        self.team_of_interest = "Burnsville"
        self.team_code = "Endzone-System"
        self.gameId = "643ad3ef-8b71-422d-ba03-f150637f148e"
        self.pdf_write = PyPDF2.PdfWriter()
        self.pdfs = []
        self.get_data()
        self.split_data()
        # self.title_page()
        self.quarterback_page()
        # To-DO add for loop for ball carriers and receivers

        for ballCarrier in self.run_data["Ball_Carrier"].unique():
            self.runningBack_page(ballCarrier)
        for reciever in self.pass_data["Ball_Carrier"].unique():
            self.receiver_page(reciever)
         

    def template_to_pdf(self, html, appendToFront: bool = False) -> None:
        # Used for ease of development
        if sys.platform.startswith('win'):
            pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='dependencies/wkhtmltopdf.exe'), options={'margin-top': '0', 'margin-right': '0', 'margin-bottom': '0', 'margin-left': '0'})
        # Means it is being run on docker docker jr docker
        else:
            pdf = pdfkit.from_string(html, False)
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf))

        if appendToFront: self.pdfs.insert(0, pdf_reader)
        else: self.pdfs.append(pdf_reader)
                
    def combine_reports(self) -> None:
        return combine_pdf_pages(self.pdfs)

    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        
        self.game_data = pd.read_sql(session.query(Game).filter(Game.Team_Code == self.team_code).filter(Game.Game_ID == self.gameId).statement, db_engine)
        self.game_data['Game_Date'] = pd.to_datetime(self.game_data['Game_Date'])
        self.game_data['Game_Date'] = self.game_data['Game_Date'].dt.strftime('%A, %d %B %Y')

        df_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID == self.gameId).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Team_Code == self.team_code).statement, db_engine)
        df_plays = pd.merge(df_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')
        self.play_data = pd.merge(df_plays, self.game_data, on='Game_ID', how='inner')
    
    def split_data(self) -> None:
        #Filter to singular possession 
        report_data = self.play_data[(self.play_data["Possession"] == self.team_of_interest)]
        self.report_data = enrich_data(report_data, self.team_of_interest)
        self.run_data = self.report_data[(self.report_data["Play_Type"].isin(["Inside Run", "Outside Run", "Option"]))]
        self.pass_data = self.report_data[(self.report_data["Play_Type"].isin(["Pass", "Pocket Pass"]))]
    def overview_page(self) -> None:
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        title_template = env.get_template('postgame_report/report_pages/title.html')
        html = title_template.render(image_path = image_path)
        # Render
        self.template_to_pdf(html, True) 
    
    def quarterback_page(self) -> None:
        # To-Do Calculate Stats


        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/quarterback.html')
        html = title_template.render(image_path = image_path, svg_path = svg_path)
        self.template_to_pdf(html, False)

    ## THIS SHOULD BE DOWN FOR EACH RUNNING BACK! so you'll need to use a for loop on distinct ball_carriers
    def runningBack_page(self, ball_carrier: int) -> None:
        
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/runningBack.html')
        html = title_template.render(image_path = image_path, svg_path = svg_path, ball_carrier = ball_carrier)
        # Render
        self.template_to_pdf(html, False)

    ## THIS SHOULD BE DOWN FOR EACH RECEIVER! so you'll need to use a for loop on distinct ball_carriers
    def receiver_page(self, receiver: int) -> None:
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/receiver.html')
        html = title_template.render(image_path = image_path, svg_path = svg_path, receiver = receiver)
        # Render
        self.template_to_pdf(html, False)