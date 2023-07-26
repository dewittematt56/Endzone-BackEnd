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
import os

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/ingame_report/static')

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
        temp_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID == self.game_id).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Team_Code == self.team_code).statement, db_engine)
        df_plays = pd.merge(temp_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')
        self.play_data = pd.merge(df_plays, self.game_data, on='Game_ID', how='inner')
        self.penalties = pd.read_sql(session.query(Penalty).filter(Penalty.Game_ID == self.game_id).statement, db_engine)
        
        
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
            pdf = pdfkit.from_string(html, False, configuration = pdfkit.configuration(wkhtmltopdf='dependencies/wkhtmltopdf.exe'), options={'margin-top': '0', 'margin-right': '0', 'margin-bottom': '0', 'margin-left': '0'})
        # Means it is being run on docker docker jr docker
        else:
            pdf = pdfkit.from_string(html, False)
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf))
        
        if appendToFront: self.pdfs.insert(0, pdf_reader)
        else: self.pdfs.append(pdf_reader)

    def getBar(self, val, total) -> str:
        try:
            val = str((val / total) * 100) + "%"
        except:
            val = "0%"
        return val
    
    def getTotalPlays(self) -> list:
        teamPlays = len(self.oData)
        enemyPlays = len(self.dData)
        totalPlays = teamPlays + enemyPlays
        teamPlaysBar = self.getBar(teamPlays, totalPlays)
        enemyPlaysBar = self.getBar(enemyPlays, totalPlays)
        playsDict = {"stat": "Total Plays", "teamVal": teamPlays, "enemyVal": enemyPlays, "teamBar": teamPlaysBar, "enemyBar": enemyPlaysBar}
        return [playsDict]

    def getYardage(self) -> list:
        oTotalYards = sum(self.oData["Result"])
        dTotalYards = sum(self.dData["Result"])

        oRushPlays = self.oData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run" | Play_Type == "Option"')
        dRushPlays = self.dData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run" | Play_Type == "Option"')
        oRushYards = sum(oRushPlays["Result"])
        dRushYards = sum(dRushPlays["Result"])

        try:
            oAvgRush = round(oRushYards / len(oRushPlays), 1)
        except ZeroDivisionError:
            oAvgRush = "Invalid"

        try:    
            dAvgRush = round(dRushYards / len(dRushPlays), 1)
        except ZeroDivisionError:
            dAvgRush = "Invalid"

        totalAvgRush = oAvgRush + dAvgRush

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
        oBarAvgRush = self.getBar(oAvgRush, totalAvgRush)
        dBarAvgRush = self.getBar(dAvgRush, totalAvgRush)

        totalDict = {"stat": "Total Yards", "teamVal": oTotalYards, "enemyVal": dTotalYards, "teamBar": oBarTotal, "enemyBar": dBarTotal}
        rushDict = {"stat": "Rush Yards", "teamVal": oRushYards, "enemyVal": dRushYards, "teamBar": oBarRush, "enemyBar": dBarRush}
        passDict = {"stat": "Pass Yards", "teamVal": oPassYards, "enemyVal": dPassYards, "teamBar": oBarPass, "enemyBar": dBarPass}
        avgRushDict = {"stat": "Yards Per Carry", "teamVal": oAvgRush, "enemyVal": dAvgRush, "teamBar": oBarAvgRush, "enemyBar": dBarAvgRush}

        return [totalDict, rushDict, passDict, avgRushDict]
    
    
    def getEfficiency(self) -> list:
        oTotalEff = get_nfl_efficiency(self.oData)[0]
        dTotalEff = get_nfl_efficiency(self.dData)[0]
        oTotalEffStr = str(oTotalEff) + "%"
        dTotalEffStr = str(dTotalEff) + "%"

        oRushPlays = self.oData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        dRushPlays = self.dData.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        oPassPlays = self.oData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        dPassPlays = self.dData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

        oRushEff = get_nfl_efficiency(oRushPlays)[0]
        dRushEff = get_nfl_efficiency(dRushPlays)[0]
        oPassEff = get_nfl_efficiency(oPassPlays)[0]
        dPassEff = get_nfl_efficiency(dPassPlays)[0]
        oRushEffStr = str(oRushEff) + "%"
        dRushEffStr = str(dRushEff) + "%"
        oPassEffStr = str(oPassEff) + "%"
        dPassEffStr = str(dPassEff) + "%"
        

        bothTotal = oTotalEff + dTotalEff
        rushTotal = oRushEff + dRushEff
        passTotal = oPassEff + dPassEff

        oBarTotal = self.getBar(oTotalEff, bothTotal)
        dBarTotal = self.getBar(dTotalEff, bothTotal)
        oBarRush = self.getBar(oRushEff, rushTotal)
        dBarRush = self.getBar(dRushEff, rushTotal)
        oPassBar = self.getBar(oPassEff, passTotal)
        dPassBar = self.getBar(dPassEff, passTotal)

        totalDict = {"stat": "Overall Efficiency", "teamVal": oTotalEffStr, "enemyVal": dTotalEffStr, "teamBar": oBarTotal, "enemyBar": dBarTotal}
        rushDict = {"stat": "Run Efficiency", "teamVal": oRushEffStr, "enemyVal": dRushEffStr, "teamBar": oBarRush, "enemyBar": dBarRush}
        passDict = {"stat": "Pass Efficiency", "teamVal": oPassEffStr, "enemyVal": dPassEffStr, "teamBar": oPassBar, "enemyBar": dPassBar}

        return [totalDict, rushDict, passDict]
    
    def getSackRate(self) -> list:
        temp = self.dData.query('Pass_Zone == "Not Thrown"')
        teamSackPlays = self.dData.query('Pass_Zone == "Not Thrown" & Result < 0')
        enemySackPlays = self.oData.query('Pass_Zone == "Not Thrown" & Result < 0')
        teamPassPlays = self.oData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        enemyPassPlays = self.dData.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

        try:
            teamSackRate = round((len(teamSackPlays) / len(enemyPassPlays)) * 100)
            teamSackRateStr = str(teamSackRate) + "%"
        except ZeroDivisionError:
            teamSackRateStr = "Invalid"

        try:
            enemySackRate = round((len(enemySackPlays) / len(teamPassPlays)) * 100)
            enemySackRateStr = str(enemySackRate) + "%"
        except ZeroDivisionError:
            enemySackRateStr = "Invalid"

        totalSackRate = teamSackRate + enemySackRate
    
        teamSackBar = self.getBar(teamSackRate, totalSackRate)
        enemySackBar = self.getBar(enemySackRate, totalSackRate)

        sackDict = {"stat": "Sack Rate", "teamVal": teamSackRateStr, "enemyVal": enemySackRateStr, "teamBar": teamSackBar, "enemyBar": enemySackBar}
        # Returning list in case we want to add stuff later on down the road to this function
        return [sackDict]
    
    def getBlitzRate(self) -> list:
        enemyPressurePlays = self.oData.query('Pressure_Existence == True')
        teamPressurePlays = self.dData.query('Pressure_Existence == True')

        try:
            teamBlitzRate = round((len(teamPressurePlays) / len(self.dData)) * 100)
            teamBlitzRateStr = str(teamBlitzRate) + "%"
        except ZeroDivisionError:
            teamBlitzRateStr = "Invalid"

        try:
            enemyBlitzRate = round((len(enemyPressurePlays) / len(self.oData)) * 100)
            enemyBlitzRateStr = str(enemyBlitzRate) + "%"
        except ZeroDivisionError:
            teamBlitzRateStr = "Invalid"

        totalBlitzRate = teamBlitzRate + enemyBlitzRate

        teamBlitzBar = self.getBar(teamBlitzRate, totalBlitzRate)
        enemyBlitzBar = self.getBar(enemyBlitzRate, totalBlitzRate)

        sackDict = {"stat": "Blitz Rate", "teamVal": teamBlitzRateStr, "enemyVal": enemyBlitzRateStr, "teamBar": teamBlitzBar, "enemyBar": enemyBlitzBar}
        # Returning list in case we want to add stuff later on down the road to this function
        return [sackDict]
    

    def getForcedTurnovers(self) -> list:
        teamTurnovers = len(self.oData.query('Event == "Interception" | Event == "Fumble"'))
        enemyTurnovers = len(self.dData.query('Event == "Interception" | Event == "Fumble"'))
        totalTurnovers = teamTurnovers + enemyTurnovers
    
        teamTurnoverBar = self.getBar(teamTurnovers, totalTurnovers)
        enemyTurnoverBar = self.getBar(enemyTurnovers, totalTurnovers)
        
        turnoverDict = {"stat": "Forced Turnovers", "teamVal": teamTurnovers, "enemyVal": enemyTurnovers, "teamBar": teamTurnoverBar, "enemyBar": enemyTurnoverBar}
        return [turnoverDict]
    
    def get3rdConv(self) -> list:
        teamConv = get_nfl_efficiency(self.oData.query('Down == 3'))[0]
        enemyConv = get_nfl_efficiency(self.dData.query('Down == 3'))[0]
        totalConv = teamConv + enemyConv

        teamConvStr = str(teamConv) + "%"
        enemyConvStr = str(enemyConv) + "%"

        team3rdConvBar = self.getBar(teamConv, totalConv)
        enemy3rdConvBar = self.getBar(enemyConv, totalConv)
        turnoverDict = {"stat": "3rd Down Conv", "teamVal": teamConvStr, "enemyVal": enemyConvStr, "teamBar": team3rdConvBar, "enemyBar": enemy3rdConvBar}
        return [turnoverDict]
    
    def getStartingFieldPos(self) -> list:
        try:
            teamDriveList = []
            teamTotalStartPos = 0
            teamNumDrives = 0
            for i in self.oData['Drive']:
                if i not in teamDriveList:
                    teamDriveList.append(i)
            for driveNum in teamDriveList:
                driveData = self.oData.query('Drive == @driveNum')
                playNum = min(driveData['Play_Number'])
                val = self.oData.query(f'Drive == {driveNum} & Play_Number == {playNum}')['Yard'].iloc[0]
                teamTotalStartPos += val
                teamNumDrives += 1
            teamStartPos = round(teamTotalStartPos / teamNumDrives)
        except:
            enemyStartPos = "invalid"

        try:
            enemyDriveList = []
            enemyTotalStartPos = 0
            enemyNumDrives = 0
            for i in self.dData['Drive']:
                if i not in enemyDriveList:
                    enemyDriveList.append(i)
            for driveNum in enemyDriveList:
                driveData = self.dData.query(f'Drive == {driveNum}')
                playNum = min(driveData['Play_Number'])
                val = self.dData.query(f'Drive == {driveNum} & Play_Number == {playNum}')['Yard'].iloc[0]
                enemyTotalStartPos += val
                enemyNumDrives += 1
            enemyStartPos = round(enemyTotalStartPos / enemyNumDrives)
        except:
            enemyStartPos = "invalid"

        totalStartPos = teamStartPos + enemyStartPos
        teamStartPosBar = self.getBar(teamStartPos, totalStartPos)
        enemyStartPosBar = self.getBar(enemyStartPos, totalStartPos)

        startPosDict = {"stat": "Avg Starting Field Pos", "teamVal": teamStartPos, "enemyVal": enemyStartPos, "teamBar": teamStartPosBar, "enemyBar": enemyStartPosBar}
        return [startPosDict]
    

    def getPlaysToStrength(self) -> list:
        teamStrengthPlays = len(self.oData.query('To_Strength == True'))
        enemyStrengthPlays = len(self.dData.query('To_Strength == True'))
        totalPlays = teamStrengthPlays + enemyStrengthPlays

        teamStrengthBar = self.getBar(teamStrengthPlays, totalPlays)
        enemyStrengthBar = self.getBar(enemyStrengthPlays, totalPlays)

        strengthDict = {"stat": "Plays into Strength", "teamVal": teamStrengthPlays, "enemyVal": enemyStrengthPlays, "teamBar": teamStrengthBar, "enemyBar": enemyStrengthBar}

        return [strengthDict]
    

    def getPlaysToBoundary(self) -> list:
        # boundaryData = self.oData['Play_Type_Dir'] == self.oData['Hash']
        teamBoundaryPlays = len(self.oData.query('Play_Type_Dir == Hash'))
        enemyBoundaryPlays = len(self.dData.query('Play_Type_Dir == Hash'))
        totalPlays = teamBoundaryPlays + enemyBoundaryPlays

        teamBoundaryBar = self.getBar(teamBoundaryPlays, totalPlays)
        enemyBoundaryBar = self.getBar(enemyBoundaryPlays, totalPlays)

        boundaryDict = {"stat": "Plays into Boundary", "teamVal": teamBoundaryPlays, "enemyVal": enemyBoundaryPlays, "teamBar": teamBoundaryBar, "enemyBar": enemyBoundaryBar}

        return [boundaryDict]
    

    def getPenalties(self) -> list:
        teamOPenalties = len(self.penalties.query(f'Penalty_Offending_Team == "{self.team_of_interest}" & Penalty_Offending_Side == "Offense"'))
        teamDPenalties = len(self.penalties.query(f'Penalty_Offending_Team == "{self.team_of_interest}" & Penalty_Offending_Side == "Defense"'))

        enemyOPenalties = len(self.penalties.query(f'Penalty_Offending_Team != "{self.team_of_interest}" & Penalty_Offending_Side == "Offense"'))
        enemyDPenalties = len(self.penalties.query(f'Penalty_Offending_Team != "{self.team_of_interest}" & Penalty_Offending_Side == "Defense"'))

        totalOPenalties = teamOPenalties + enemyOPenalties
        totalDPenalties = teamDPenalties + enemyDPenalties

        teamOBar = self.getBar(teamOPenalties, totalOPenalties)
        enemyOBar = self.getBar(enemyOPenalties, totalOPenalties)
        teamDBar = self.getBar(teamDPenalties, totalDPenalties)
        enemyDBar = self.getBar(enemyDPenalties, totalDPenalties)

        oPenaltiesDict = {"stat": "O Penalties", "teamVal": teamOPenalties, "enemyVal": enemyOPenalties, "teamBar": teamOBar, "enemyBar": enemyOBar}
        dPenaltiesDict = {"stat": "D Penalties", "teamVal": teamDPenalties, "enemyVal": enemyDPenalties, "teamBar": teamDBar, "enemyBar": enemyDBar}
        return [oPenaltiesDict, dPenaltiesDict]

    
    def title_page(self) -> None:
        """_summary_

        Args:
            hi (_type_): _description_

        Returns:
            _type_: _description_
        """
        title_template = env.get_template('ingame_report/report_pages/title.html')

        totalPlays = self.getTotalPlays()
        yardList = self.getYardage()
        effList = self.getEfficiency()
        sackRateList = self.getSackRate()
        blitzRateList = self.getBlitzRate()
        turnoverList = self.getForcedTurnovers()
        conv3rdList = self.get3rdConv()
        startPosList = self.getStartingFieldPos()
        playsToStrength = self.getPlaysToStrength()
        playsToBoundary = self.getPlaysToBoundary()
        penaltiesList = self.getPenalties()
        data_list = totalPlays + yardList + effList + sackRateList + blitzRateList + turnoverList + \
                    conv3rdList + startPosList + playsToStrength + playsToBoundary + penaltiesList

        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        html = title_template.render(title="Ingame Report", data_list=data_list, image_path = image_path)
        # Render this sucker!
        self.template_to_pdf(html, True)

    def run_report(self):
        self.title_page()

        
if __name__ == "__main__":
    test = IngameReport("team", "game", "team_code")
