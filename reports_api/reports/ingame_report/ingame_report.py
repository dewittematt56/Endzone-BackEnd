from io import BytesIO
from database.db import db
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
from ..utils.data_report_utils import *
from ..utils.graphing_utils import *
from ..utils.spatial_utils import *
import sys
import datetime

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')

class IngameReport():
    def __init__(self, team_of_interest: str, game: str, team_code: str) -> None:
        self.team_of_interest = team_of_interest ## either self team or opponent
        self.game_id = game
        self.team_code = team_code
        self.pdfs = []
        self.pages = []
        self.pdf_write = PyPDF2.PdfWriter()
        self.oData = []
        self.dData = []

        # Temp Overriding
        self.reportType = "Offense"
        self.team_of_interest = "Burnsville"
        self.team_code = "Endzone-System"
        self.game_id = "643ad3ef-8b71-422d-ba03-f150637f148e"


        self.get_data()
        self.split_data()
        self.run_report()

    def get_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        self.game_data = pd.read_sql(session.query(Game).filter(Game.Game_ID == self.game_id).statement, db_engine)
        self.game_data['Game_Date'] = pd.to_datetime(self.game_data['Game_Date'])
        self.game_data['Game_Date'] = self.game_data['Game_Date'].dt.strftime('%A, %d %B %Y')
        # Team Code is linked via team_code
        temp_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID == self.game_id).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Team_Code == self.team_code).statement, db_engine)
        df_plays = pd.merge(temp_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')
        self.play_data = pd.merge(df_plays, self.game_data, on='Game_ID', how='inner')
        
    def split_data(self) -> None:
        dPlays = self.play_data[(self.play_data["Possession"] != self.team_of_interest)]
        oPlays = self.play_data[(self.play_data["Possession"] == self.team_of_interest)]
        self.oData = enrich_data(oPlays, self.team_of_interest)
        self.dData = enrich_data(dPlays, self.team_of_interest)


    def combine_reports(self) -> None:
        return combine_pdf_pages(self.pdfs)
    
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

    def getYardage(self) -> list:
        oTotalYards = sum(self.oData["Result"])
        dTotalYards = sum(self.dData["Result"])

        oRushPlays = self.oData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        dRushPlays = self.dData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        oRushYards = sum(oRushPlays["Result"])
        dRushYards = sum(dRushPlays["Result"])

        oPassPlays = self.oData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        dPassPlays = self.dData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        oPassYards = sum(oPassPlays["Result"])
        dPassYards = sum(dPassPlays["Result"])

        bothTotal = oTotalYards + dTotalYards
        rushTotal = oRushYards + dRushYards
        passTotal = oPassYards + dPassYards
        oBarTotal = self.getBar(oTotalYards, bothTotal)
        dBarTotal = self.getBar(dTotalYards, bothTotal)
        oBarRush = self.getBar(oRushYards, rushTotal) 
        dBarRush = self.getBar(dRushYards, rushTotal)
        oBarPass = self.getBar(oPassYards, passTotal)
        dBarPass = self.getBar(dPassYards, passTotal)

        totalDict = {"stat": "Total Yards", "val1": oTotalYards, "val2": dTotalYards, "bar1": oBarTotal, "bar2": dBarTotal}
        rushDict = {"stat": "Rush Yards", "val1": oRushYards, "val2": dRushYards, "bar1": oBarRush, "bar2": dBarRush}
        passDict = {"stat": "Pass Yards", "val1": oPassYards, "val2": dPassYards, "bar1": oBarPass, "bar2": dBarPass}

        return [totalDict, rushDict, passDict]
    
    def getBar(self, val, total) -> str:
        if total <= 0:
            return "0%"
        return str((val / total) * 100) + "%"
    
    def getEfficiency(self) -> list:
        oTotalEff = get_nfl_efficiency(self.oData)[0]
        dTotalEff = get_nfl_efficiency(self.dData)[0]

        oRushPlays = self.oData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        dRushPlays = self.dData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        oPassPlays = self.oData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        dPassPlays = self.dData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

        oRushEff = get_nfl_efficiency(oRushPlays)[0]
        dRushEff = get_nfl_efficiency(dRushPlays)[0]
        oPassEff = get_nfl_efficiency(oPassPlays)[0]
        dPassEff = get_nfl_efficiency(dPassPlays)[0]

        bothTotal = oTotalEff + dTotalEff
        rushTotal = oRushEff + dRushEff
        passTotal = oPassEff + dPassEff

        oBarTotal = self.getBar(oTotalEff, bothTotal)
        dBarTotal = self.getBar(dTotalEff, bothTotal)
        oBarRush = self.getBar(oRushEff, rushTotal)
        dBarRush = self.getBar(dRushEff, rushTotal)
        oPassBar = self.getBar(oPassEff, passTotal)
        dPassBar = self.getBar(dPassEff, passTotal)

        totalDict = {"stat": "Overall Efficiency", "val1": oTotalEff, "val2": dTotalEff, "bar1": oBarTotal, "bar2": dBarTotal}
        rushDict = {"stat": "Run Efficiency", "val1": oRushEff, "val2": dRushEff, "bar1": oBarRush, "bar2": dBarRush}
        passDict = {"stat": "Pass Efficiency", "val1": oPassEff, "val2": dPassEff, "bar1": oPassBar, "bar2": dPassBar}

        return [totalDict, rushDict, passDict]
    
    def getSackRate(self) -> list:
        temp = self.dData.query('Pass_Zone == "Not Thrown"')
        print(len(temp))
        teamSackPlays = self.dData.query('Pass_Zone == "Not Thrown" & Result < 0')
        enemySackPlays = self.oData.query('Pass_Zone == "Not Thrown" & Result < 0')
        teamPassPlays = self.oData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        enemyPassPlays = self.dData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

        try:
            teamSackRate = (len(teamSackPlays) / len(enemyPassPlays)) * 100
            teamSackRateStr = str(teamSackRate) + "%"
        except ZeroDivisionError as err:
            teamSackRateStr = "Invalid"

        try:
            enemySackRate = (len(enemySackPlays) / len(teamPassPlays)) * 100
            enemySackRateStr = str(enemySackRate) + "%"
        except ZeroDivisionError as err:
            enemySackRateStr = "Invalid"

        totalSackRate = teamSackRate + enemySackRate
    
        teamBar = self.getBar(teamSackRate, totalSackRate)
        enemyBar = self.getBar(enemySackRate, totalSackRate)

        sackDict = {"stat": "Sack Rate", "val1": teamSackRateStr, "val2": enemySackRateStr, "bar1": teamBar, "bar2": enemyBar}
        # Returning list in case we want to add stuff later on down the road to this function
        return [sackDict]


        
    
    def title_page(self) -> None:
        """_summary_

        Args:
            hi (_type_): _description_

        Returns:
            _type_: _description_
        """
        title_template = env.get_template('ingame_report/report_pages/title.html')

        yardList = self.getYardage()
        effList = self.getEfficiency()
        sackRateList = self.getSackRate()
        data_list = yardList + effList + sackRateList

        html = title_template.render(title="Ingame Report", img_path="images/endzone_shield.png", data_list=data_list)
        # Render this sucker!
        self.template_to_pdf(html, True)

    def run_report(self):
        self.title_page()

        
if __name__ == "__main__":
    test = IngameReport("team", "game", "team_code")
