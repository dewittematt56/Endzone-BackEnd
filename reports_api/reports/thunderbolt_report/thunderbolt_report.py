from io import BytesIO
import pandas as pd
import jinja2
import pdfkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import PyPDF2
from database.db import db_uri 
from database.models import *
from ..utils.spatial_utils import *
from ..utils.graphing_utils import *
from ..utils.utils import *
import sys
from reports_api.reports.pregame_report.pregame_report import PregameReport
# To-Do make class of Thunderbolt

env = jinja2.Environment(loader = jinja2.FileSystemLoader("./reports_api/reports"))

def get_down_group(distance: int) -> str:
    if distance <= 3: return "Short"
    elif distance > 3 and distance <= 6: return "Medium"
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
def get_defensive_formation(coverage: str) -> pd.DataFrame:
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
        df.loc[index, "Thunderbolt_Coverage"] = get_play_type(df.loc[index, "Coverage"])
    df["Thunderbolt_Down"] = df["Down"].astype(str) + " - " + df["Down_Group"]
    return df

def crossTabQuery(df_x: pd.Series, df_y: pd.Series) -> pd.DataFrame:
    crossTab = pd.crosstab(df_x, df_y, normalize="index")
    crossTab = crossTab * 100
    return crossTab




class ThunderboltReport():
    def __init__(self, team_of_interest: str, game_IDs: 'list[str]', user_team_code: str, report_type: str) -> None: 
        self.team_of_interest = team_of_interest
        self.game_IDs = game_IDs
        self.user_team_code = user_team_code
        self.report_type = report_type
        self.pdf_write = PyPDF2.PdfWriter()
        self.pdfs = []
        self.team_of_interest = "Burnsville"
        self.team_code = "Endzone-System"
        self.game_IDs = ["643ad3ef-8b71-422d-ba03-f150637f148e"]
        self.get_data()
        self.base_thunderbolt_page()

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

    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        self.play_data = pd.read_sql(session.query(Play).filter(Play.Game_ID.in_(self.game_IDs)).statement, db_engine)
        self.play_data = prep_data(self.play_data)
        
    
    def base_thunderbolt_page(self) -> None:
        thunderbolt_tables = self.generate_thunderbolt_tables(self.play_data)
        self.arrayTest(thunderbolt_tables)
        page = env.get_template("thunderbolt_report/thunderbolt_pages/base_report/thunderbolt_base.html")
        html = page.render(team = self.team_of_interest, thunderbolt_tables = thunderbolt_tables)
        self.template_to_pdf(html)
    
    def generate_thunderbolt_tables(self, df :pd.DataFrame)-> 'list[list[list[pd.DataFrame]]]': 
        thunderbolt_field_positions = []
        thunderbolt_field_positions.append(self.process_field_position(df.query("Yard >= 66")))
        thunderbolt_field_positions.append(self.process_field_position(df.query("Yard < 66 & Yard > 33")))
        thunderbolt_field_positions.append(self.process_field_position(df.query("Yard <= 33")))
        return thunderbolt_field_positions
    
    def process_field_position(self, df: pd.DataFrame)-> 'list[list[pd.DataFrame]]':
        thunderbolt_hashes = []
        # Left Hash
        thunderbolt_hashes.append(self.process_hash(df.query("Hash == 'Left'")))
        # Middle Hash
        thunderbolt_hashes.append(self.process_hash(df.query("Hash == 'Middle'")))
        # Right Hash
        thunderbolt_hashes.append(self.process_hash(df.query("Hash == 'Right'")))
        return thunderbolt_hashes
    def process_hash(self, df: pd.DataFrame)-> 'list[pd.DataFrame]':
        thunderbolt_downs = [] 
         # 1st down
        thunderbolt_downs.append(self.process_down(df.query("Down == 1")))
         # 2nd down
        thunderbolt_downs.append(self.process_down(df.query("Down == 2")))
         # 3rd down
        thunderbolt_downs.append(self.process_down(df.query("Down == 3")))
        return thunderbolt_downs
        
    
    def process_down(self, df: pd.DataFrame) -> pd.DataFrame:
        return crossTabQuery(df.Thunderbolt_Down, df.Thunderbolt_Play)
        
    def arrayTest(self, thunderbolt_tables):
        for field_position in thunderbolt_tables:
            for hash in field_position:
                for down in hash:
                    print(down)
# Cross tab query from thunderbolt tables
    
    
              


