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
import os

pd.set_option("display.max_rows", None)
env = jinja2.Environment(loader = jinja2.FileSystemLoader("./reports_api/reports"))

def get_down_group(distance: int) -> str:
    if distance <= 3: return "Short"
    elif distance > 3 and distance <= 6: return "Med"
    elif distance > 6: return "Long"
# TODO - Make function to take the play type and make it either pass or run. (option = run), convert any of the given play types to the simply run or pass. Add it to a column on the dataframe and call it "generic_play_type"
# TODO - Convert man or zone variations to simple man or zone
# TODO - do a cross tab query on the data. 
# TODO - Write a function that does certain field sections

def get_qb_efficiency(completion_percentage: bool, yards: int, pass_attempts: int, touchdowns: int, interceptions: int) -> bool:
    factor1 = completion_percentage
    factor2 = (yards/pass_attempts) * 8.4
    factor3 = (touchdowns/pass_attempts) * 100 * 3.3
    factor4 = (interceptions/pass_attempts) * 100 * 2
    efficiency = factor1 + factor2 + factor3 - factor4
    return efficiency

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
        self.overview_page()
        # self.quarterback_page()
        rush_data = (self.o_data[~self.o_data['Run_Type'].isnull()])
        value_counts = rush_data["Ball_Carrier"].value_counts()
        values_to_keep = value_counts[value_counts > 6].index
        valid_running_data = rush_data[rush_data["Ball_Carrier"].isin(values_to_keep)]

        pass_data = (self.o_data[self.o_data["Run_Type"].isnull()])
        value_counts = pass_data["Ball_Carrier"].value_counts()
        values_to_keep = value_counts[value_counts > 6].index
        valid_passing_data = pass_data[pass_data["Ball_Carrier"].isin(values_to_keep)]
        # Create dataframe of ball carriers who have more than 6 carries
        # Same for wr 3 or more catches and pass zone has to be valid

        for ballCarrier in valid_running_data["Ball_Carrier"].unique():
            self.runningBack_page(ballCarrier)
        # for reciever in self.pass_data["Ball_Carrier"].unique():
        #     self.receiver_page(reciever)
         
    def getBar(self, val, total) -> str:
        try:
            val = str((val / total) * 100) + "%"
        except:
            val = "0%"
        return val

    def getEfficiency(self) -> list:
        oTotalEff = get_nfl_efficiency(self.o_data)[0]
        dTotalEff = get_nfl_efficiency(self.d_data)[0]
        oTotalEffStr = str(oTotalEff) + "%"
        dTotalEffStr = str(dTotalEff) + "%"

        oRushPlays = self.o_data.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        dRushPlays = self.d_data.query('Play_Type == "Inside Run" | Play_Type == "Outside Run"')
        oPassPlays = self.o_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        dPassPlays = self.d_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

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
        teamSackPlays = self.d_data.query('Pass_Zone == "Not Thrown" & Result < 0')
        enemySackPlays = self.o_data.query('Pass_Zone == "Not Thrown" & Result < 0')
        teamPassPlays = self.o_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        enemyPassPlays = self.d_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')

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
    
        teamBar = self.getBar(teamSackRate, totalSackRate)
        enemyBar = self.getBar(enemySackRate, totalSackRate)

        sackDict = {"stat": "Sack Rate", "teamVal": teamSackRateStr, "enemyVal": enemySackRateStr, "teamBar": teamBar, "enemyBar": enemyBar}
        # Returning list in case we want to add stuff later on down the road to this function
        return [sackDict]
    
    def getBlitzRate(self) -> list:
        enemyPressurePlays = self.o_data.query('Pressure_Existence == True')
        teamPressurePlays = self.d_data.query('Pressure_Existence == True')

        try:
            teamBlitzRate = round((len(teamPressurePlays) / len(self.d_data)) * 100)
            teamBlitzRateStr = str(teamBlitzRate) + "%"
        except ZeroDivisionError:
            teamBlitzRateStr = "Invalid"

        try:
            enemyBlitzRate = round((len(enemyPressurePlays) / len(self.o_data)) * 100)
            enemyBlitzRateStr = str(enemyBlitzRate) + "%"
        except ZeroDivisionError:
            teamBlitzRateStr = "Invalid"

        totalBlitzRate = teamBlitzRate + enemyBlitzRate

        teamBar = self.getBar(teamBlitzRate, totalBlitzRate)
        enemyBar = self.getBar(enemyBlitzRate, totalBlitzRate)

        sackDict = {"stat": "Blitz Rate", "teamVal": teamBlitzRateStr, "enemyVal": enemyBlitzRateStr, "teamBar": teamBar, "enemyBar": enemyBar}
        # Returning list in case we want to add stuff later on down the road to this function
        return [sackDict]
    
    def getForcedTurnovers(self) -> list:
        teamTurnovers = len(self.o_data.query('Event == "Interception" | Event == "Fumble"'))
        enemyTurnovers = len(self.d_data.query('Event == "Interception" | Event == "Fumble"'))
        totalTurnovers = teamTurnovers + enemyTurnovers
    
        teamBar = self.getBar(teamTurnovers, totalTurnovers)
        enemyBar = self.getBar(enemyTurnovers, totalTurnovers)
        
        turnoverDict = {"stat": "Forced Turnovers", "teamVal": teamTurnovers, "enemyVal": enemyTurnovers, "teamBar": teamBar, "enemyBar": enemyBar}
        return [turnoverDict]
    
    def get3rdConv(self) -> list:
        teamConv = get_nfl_efficiency(self.o_data.query('Down == 3'))[0]
        enemyConv = get_nfl_efficiency(self.d_data.query('Down == 3'))[0]
        totalConv = teamConv + enemyConv

        teamConvStr = str(teamConv) + "%"
        enemyConvStr = str(enemyConv) + "%"

        teamBar = self.getBar(teamConv, totalConv)
        enemyBar = self.getBar(enemyConv, totalConv)
        turnoverDict = {"stat": "3rd Down Conv", "teamVal": teamConvStr, "enemyVal": enemyConvStr, "teamBar": teamBar, "enemyBar": enemyBar}
        return [turnoverDict]
    
    def getStartingFieldPos(self) -> list:
        try:
            teamDriveList = []
            teamTotalStartPos = 0
            teamNumDrives = 0
            for i in self.o_data['Drive']:
                if i not in teamDriveList:
                    teamDriveList.append(i)
            for driveNum in teamDriveList:
                driveData = self.o_data.query('Drive == @driveNum')
                playNum = min(driveData['Play_Number'])
                val = self.o_data.query(f'Drive == {driveNum} & Play_Number == {playNum}')['Yard'].iloc[0]
                teamTotalStartPos += val
                teamNumDrives += 1
            teamStartPos = round(teamTotalStartPos / teamNumDrives)
        except:
            enemyStartPos = "invalid"

        try:
            enemyDriveList = []
            enemyTotalStartPos = 0
            enemyNumDrives = 0
            for i in self.d_data['Drive']:
                if i not in enemyDriveList:
                    enemyDriveList.append(i)
            for driveNum in enemyDriveList:
                driveData = self.d_data.query('Drive == @driveNum')
                playNum = min(driveData['Play_Number'])
                val = self.d_data.query(f'Drive == {driveNum} & Play_Number == {playNum}')['Yard'].iloc[0]
                enemyTotalStartPos += val
                enemyNumDrives += 1
            enemyStartPos = round(enemyTotalStartPos / enemyNumDrives)
        except:
            enemyStartPos = "invalid"

        totalStartPos = teamStartPos + enemyStartPos
        teamBar = self.getBar(teamStartPos, totalStartPos)
        enemyBar = self.getBar(enemyStartPos, totalStartPos)

        startPosDict = {"stat": "Avg Starting Field Pos", "teamVal": teamStartPos, "enemyVal": enemyStartPos, "teamBar": teamBar, "enemyBar": enemyBar}
        return [startPosDict]

    def getYardage(self) -> list:
        oTotalPlays = len(self.o_data)
        dTotalPlays = len(self.d_data)

        oTotalYards = sum(self.o_data["Result"])
        dTotalYards = sum(self.d_data["Result"])

        oInsideRushPlays = self.o_data.query('Play_Type == "Inside Run"')
        oOutsideRushPlays = self.o_data.query('Play_Type == "Outside Run"')

        dInsideRushPlays = self.d_data.query('Play_Type == "Inside Run"')
        dOutsideRushPlays = self.d_data.query('Play_Type == "Outside Run"')

        oRushYards = sum(oInsideRushPlays["Result"]) + sum(oOutsideRushPlays["Result"])
        dRushYards = sum(dInsideRushPlays["Result"]) + sum(dOutsideRushPlays["Result"])

        try: oAvgRush = round(oRushYards / (len(oInsideRushPlays) + len(oOutsideRushPlays)), 1)
        except ZeroDivisionError:oAvgRush = 0

        try: oYardsPerAttempt = round(oTotalYards / oTotalPlays, 1)
        except ZeroDivisionError: oYardsPerAttempt = 0

        try: dYardsPerAttempt = round(dTotalYards / dTotalPlays, 1)
        except ZeroDivisionError: dYardsPerAttempt = 0

        try: dAvgRush = round(dRushYards / (len(dInsideRushPlays) + len(dOutsideRushPlays)), 1)
        except ZeroDivisionError: dAvgRush = 0

        totalAvgRush = oAvgRush + dAvgRush

        oPassPlays = self.o_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        dPassPlays = self.d_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
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

        totalPlays = {"stat": "Plays Ran", "teamVal": oTotalPlays, "enemyVal": dTotalPlays, "teamBar":  self.getBar(oTotalPlays, oTotalPlays + dTotalPlays), "enemyBar": self.getBar(dTotalPlays, oTotalPlays + dTotalPlays)}
        totalDict = {"stat": "Total Yards", "teamVal": oTotalYards, "enemyVal": dTotalYards, "teamBar": oBarTotal, "enemyBar": dBarTotal}
        avgYardDict = {"stat": "Yards Per Attempt", "teamVal": oYardsPerAttempt, "enemyVal": dYardsPerAttempt, "teamBar": self.getBar(oYardsPerAttempt, oYardsPerAttempt + dYardsPerAttempt), "enemyBar": self.getBar(dYardsPerAttempt, oYardsPerAttempt + dYardsPerAttempt)}
        rushDict = {"stat": "Rush Yards", "teamVal": oRushYards, "enemyVal": dRushYards, "teamBar": oBarRush, "enemyBar": dBarRush}
        
        insideRushDict = {"stat": "Inside Run Yards", "teamVal": sum(oInsideRushPlays["Result"]), "enemyVal": sum(dInsideRushPlays["Result"]), "teamBar": self.getBar(sum(oInsideRushPlays["Result"]), sum(oInsideRushPlays["Result"]) + sum(dInsideRushPlays["Result"])), "enemyBar": self.getBar(sum(dInsideRushPlays["Result"]), sum(oInsideRushPlays["Result"]) + sum(dInsideRushPlays["Result"]))}
        outsideRushDict = {"stat": "Outside Run Yards", "teamVal": sum(oOutsideRushPlays["Result"]), "enemyVal": sum(dOutsideRushPlays["Result"]), "teamBar": self.getBar(sum(oOutsideRushPlays["Result"]), sum(oOutsideRushPlays["Result"]) + sum(dOutsideRushPlays["Result"])), "enemyBar": self.getBar(sum(dOutsideRushPlays["Result"]), sum(oOutsideRushPlays["Result"]) + sum(dOutsideRushPlays["Result"]))}

        passDict = {"stat": "Pass Yards", "teamVal": oPassYards, "enemyVal": dPassYards, "teamBar": oBarPass, "enemyBar": dBarPass}
        avgRushDict = {"stat": "Yards Per Carry", "teamVal": oAvgRush, "enemyVal": dAvgRush, "teamBar": oBarAvgRush, "enemyBar": dBarAvgRush}

        return [totalPlays, totalDict, avgYardDict, rushDict, insideRushDict, outsideRushDict, avgRushDict, passDict]

    def getRedzonePercentage(self):
        o_redzone = self.o_data.query("Yard >= 80")
        o_number_of_redzone_scores = len(o_redzone[o_redzone['Event'].isin(['Touchdown', 'Field Goal'])])
        o_number_of_redzone_drives = len(o_redzone.groupby("Drive"))
        o_redzone_percentage = round((o_number_of_redzone_scores / o_number_of_redzone_drives) * 100, 1)

        d_redzone = self.d_data.query("Yard >= 80")
        d_number_of_redzone_scores = len(d_redzone[d_redzone['Event'].isin(['Touchdown', 'Field Goal'])])
        d_number_of_redzone_drives = len(d_redzone.groupby("Drive"))
        d_redzone_percentage = round((d_number_of_redzone_scores / d_number_of_redzone_drives) * 100, 1)

        total_redzone_percentage = o_redzone_percentage + d_redzone_percentage
        return [{"stat": "Redzone Percentage", "teamVal": o_redzone_percentage, "enemyVal": d_redzone_percentage, "teamBar": self.getBar(o_redzone_percentage, total_redzone_percentage), "enemyBar": self.getBar(d_redzone_percentage, total_redzone_percentage)}]
    
    def getBigAndNegativePlays(self):
        o_big_plays = len(self.o_data.query("(Play_Type in ['Inside Run', 'Outside Run', 'Option'] and Result >= 10) or (Play_Type in ['Pass', 'Boot Pass'] and Result >= 20)"))
        d_big_plays = len(self.d_data.query("(Play_Type in ['Inside Run', 'Outside Run', 'Option'] and Result >= 10) or (Play_Type in ['Pass', 'Boot Pass'] and Result >= 20)"))
        total_big_plays = o_big_plays + d_big_plays

        o_neg_plays = len(self.o_data.query("Result < 0"))
        d_neg_plays = len(self.d_data.query("Result < 0"))
        total_neg_plays = o_neg_plays + d_neg_plays

        bigPlayDict = {"stat": "Big Plays", "teamVal": o_big_plays, "enemyVal": d_big_plays, "teamBar": self.getBar(o_big_plays, total_big_plays), "enemyBar": self.getBar(d_big_plays, total_big_plays)}
        negPlayDict = {"stat": "Negative Plays", "teamVal": o_neg_plays, "enemyVal": d_neg_plays, "teamBar": self.getBar(o_neg_plays, total_neg_plays), "enemyBar": self.getBar(d_neg_plays, total_neg_plays)}
        return [bigPlayDict, negPlayDict]

    def getPlaysToStrength(self) -> list:
        teamStrengthPlays = len(self.o_data.query('To_Strength == True'))
        enemyStrengthPlays = len(self.d_data.query('To_Strength == True'))
        totalPlays = teamStrengthPlays + enemyStrengthPlays

        teamStrengthBar = self.getBar(teamStrengthPlays, totalPlays)
        enemyStrengthBar = self.getBar(enemyStrengthPlays, totalPlays)

        strengthDict = {"stat": "Plays into Strength", "teamVal": teamStrengthPlays, "enemyVal": enemyStrengthPlays, "teamBar": teamStrengthBar, "enemyBar": enemyStrengthBar}

        return [strengthDict]
    
    def getPlaysToBoundary(self) -> list:
        # boundaryData = self.oData['Play_Type_Dir'] == self.oData['Hash']
        teamBoundaryPlays = len(self.o_data.query('Play_Type_Dir == Hash'))
        enemyBoundaryPlays = len(self.d_data.query('Play_Type_Dir == Hash'))
        totalPlays = teamBoundaryPlays + enemyBoundaryPlays

        teamBoundaryBar = self.getBar(teamBoundaryPlays, totalPlays)
        enemyBoundaryBar = self.getBar(enemyBoundaryPlays, totalPlays)

        boundaryDict = {"stat": "Plays into Boundary", "teamVal": teamBoundaryPlays, "enemyVal": enemyBoundaryPlays, "teamBar": teamBoundaryBar, "enemyBar": enemyBoundaryBar}

        return [boundaryDict]
    
    def getPenalties(self) -> list:
        teamOPenalties = sum(self.penalties.query(f'Penalty_Offending_Team == "{self.team_of_interest}" & Penalty_Offending_Side == "Offense"')["Penalty_Yards"])
        teamDPenalties = sum(self.penalties.query(f'Penalty_Offending_Team == "{self.team_of_interest}" & Penalty_Offending_Side == "Defense"')["Penalty_Yards"])

        enemyOPenalties = sum(self.penalties.query(f'Penalty_Offending_Team != "{self.team_of_interest}" & Penalty_Offending_Side == "Offense"')["Penalty_Yards"])
        enemyDPenalties = sum(self.penalties.query(f'Penalty_Offending_Team != "{self.team_of_interest}" & Penalty_Offending_Side == "Defense"')["Penalty_Yards"])

        totalOPenalties = teamOPenalties + enemyOPenalties
        totalDPenalties = teamDPenalties + enemyDPenalties

        teamOBar = self.getBar(teamOPenalties, totalOPenalties)
        enemyOBar = self.getBar(enemyOPenalties, totalOPenalties)
        teamDBar = self.getBar(teamDPenalties, totalDPenalties)
        enemyDBar = self.getBar(enemyDPenalties, totalDPenalties)

        oPenaltiesDict = {"stat": "O Penalty Yards", "teamVal": teamOPenalties, "enemyVal": enemyOPenalties, "teamBar": teamOBar, "enemyBar": enemyOBar}
        dPenaltiesDict = {"stat": "D Penalty Yards", "teamVal": teamDPenalties, "enemyVal": enemyDPenalties, "teamBar": teamDBar, "enemyBar": enemyDBar}
        return [oPenaltiesDict, dPenaltiesDict]

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
        self.penalties = pd.read_sql(session.query(Penalty).filter(Penalty.Game_ID == self.gameId).statement, db_engine)

    def split_data(self) -> None:
        self.report_data = enrich_data(self.play_data, self.team_of_interest)
        self.o_data = self.report_data[(self.report_data["Possession"] == self.team_of_interest)]
        self.d_data = self.report_data[(self.report_data["Possession"] != self.team_of_interest)]
        self.run_data = self.report_data[(self.report_data["Play_Type"].isin(["Inside Run", "Outside Run", "Option"]))]
        self.pass_data = self.report_data[(self.report_data["Play_Type"].isin(["Pass", "Pocket Pass"]))]

    def overview_page(self) -> None:
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        title_template = env.get_template('postgame_report/report_pages/title.html')

        data_list = self.getYardage() + self.getStartingFieldPos() + self.getRedzonePercentage() + self.getEfficiency() + self.get3rdConv() + self.getBigAndNegativePlays() + self.getSackRate() + self.getBlitzRate() + self.getPlaysToStrength() + self.getPlaysToBoundary() + self.getPenalties() + self.getForcedTurnovers()
        
        html = title_template.render(image_path = image_path, data_list = data_list, home_team = self.o_data['Home_Team'].iloc[0], away_team = self.o_data['Away_Team'].iloc[0], away_score = self.play_data["Home_Score"].iloc[len(self.play_data) - 1], home_score = self.play_data["Away_Score"].iloc[len(self.play_data) - 1])
        # Render
        self.template_to_pdf(html, True) 
    
    def quarterback_page(self) -> None:
        # To-Do Calculate Stats
        pass_attempts = 0
        complete_passes = 0
        pass_yards = 0
        touchdowns = 0
        interceptions = 0
        fumbles = 0
        thrown_passes = self.o_data.query('Play_Type == "Pocket Pass" | Play_Type == "Boot Pass"')
        pass_attempts = len(thrown_passes)
        thrown_passes["Distance"] = pd.to_numeric(thrown_passes["Distance"], errors='coerce')
        thrown_passes['Pass_Zone'] = thrown_passes['Pass_Zone'].replace('Non-Passing-Play', 'Not Thrown')
        self.o_data['is_sack'] = (self.o_data['Pass_Zone'].isin(['Non-Passing-Play'])) & (self.o_data["Result"] <= 0) # true= sack, false = scramble take sum of this and divide length of dataframe
        thrown_passes['Complete_Pass'] = (~thrown_passes['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (thrown_passes["Result"] != 0)
        sacks = self.o_data["is_sack"].sum()
        scrambles = len(self.o_data["is_sack"]) - self.o_data["is_sack"].sum()
        average_gain = round(self.o_data["Distance"].mean(), 2)
        for completion in thrown_passes["Complete_Pass"]:
            if completion == True:
                complete_passes += 1
        for throw in thrown_passes["Distance"]: # Get total yardage
            pass_yards += throw
        for event in thrown_passes["Event"]: # Get total touchdowns
            if event == "Touchdown":
                touchdowns += 1
            elif event == "Interception": # Find interceptions
                interceptions += 1
            elif event == "Fumble":
                fumbles += 1
        turnovers = interceptions + fumbles
        turnover_rate = round((turnovers / (pass_attempts + scrambles + sacks))*100, 2)
        sack_rate = round((sacks / (pass_attempts + scrambles + sacks))*100, 2)
        scramble_rate = round((scrambles / (pass_attempts + scrambles + sacks))*100, 2)
        qbr = calculate_qbr(thrown_passes)
        completion_percentage = round((complete_passes/pass_attempts) * 100)
        efficiency = get_nfl_efficiency(thrown_passes)[0]
        
        quarterback_bar = groupedBarGraph(thrown_passes, "Pass_Zone", "Ball_Carrier", "Targets")
        
        # Create Dataframe for Pass Zones
        df_yards = thrown_passes.groupby('Pass_Zone')['Result'].apply(lambda x: x.sum()).reset_index()
        df_comp_percentage = thrown_passes.groupby('Pass_Zone')['Complete_Pass'].apply(lambda x: int((x.sum() / len(x)) * 100)).reset_index()
        df_yards.columns = ["Category", "Value"]
        df_comp_percentage.columns = ["Category", "Value"]
        quarterback_yards_per_zone_graph = PassZone(df_yards, 'Value', number_of_classes=3, legend_labels=['Low', 'Medium', 'High'], title="Yards Per Pass Zone").create_graph()
        quarterback_comp_percentage_chart = PassZone(df_comp_percentage, 'Value', number_of_classes=3, legend_labels=['Low Completion %', 'Medium Completion %', 'High Completion %'], title="Completion Percentage Per Pass Zone").create_graph(),
        
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/quarterback.html')
        html = title_template.render(image_path = image_path, 
                                     svg_path = svg_path, 
                                     quarterback_bar = quarterback_bar, 
                                     quarterback_yards_per_zone_graph = quarterback_yards_per_zone_graph, 
                                     quarterback_comp_percentage_chart = quarterback_comp_percentage_chart,
                                     pass_yards = pass_yards,
                                    touchdowns = touchdowns, interceptions = interceptions, pass_attempts=pass_attempts, completion_percentage=completion_percentage,
                                    complete_passes = complete_passes, qbr=qbr, efficiency=efficiency, sacks = sacks, scrambles = scrambles, turnover_rate=turnover_rate,
                                    sack_rate=sack_rate, scramble_rate=scramble_rate, average_gain=average_gain)
        
        self.template_to_pdf(html, False)

    ## THIS SHOULD BE DOWN FOR EACH RUNNING BACK! so you'll need to use a for loop on distinct ball_carriers
    def runningBack_page(self, ball_carrier: int) -> None: # long is max run
        total_runs = 0
        total_yards = 0
        touchdowns = 0
        fumbles = 0
        rush_data = self.o_data[~self.o_data['Run_Type'].isnull() & (self.o_data["Ball_Carrier"] == ball_carrier)]
        for run in rush_data["Distance"]:
            total_runs += 1
            total_yards += run
        average = total_yards / total_runs
        for event in rush_data["Event"]:
            if event == "Touchdown":
                touchdowns += 1
            elif event == "Fumble":
                fumbles += 1
        first_down_yards = rush_data.query("Down == 1")["Result"].sum()
        second_down_yards = rush_data.query("Down == 2")["Result"].sum()
        third_down_yards = rush_data.query("Down == 3")["Result"].sum()
        long = self.o_data["Distance"].max()
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/runningBack.html')
        html = title_template.render(image_path = image_path, 
                                     svg_path = svg_path, 
                                     ball_carrier = ball_carrier, 
                                     total_runs = total_runs,
                                     total_yards = total_yards, 
                                     touchdowns = touchdowns, 
                                     fumbles = fumbles, 
                                     average = average, 
                                     long=long,
                                     first_down_yards = first_down_yards,
                                     second_down_yards = second_down_yards,
                                     third_down_yards = third_down_yards
        )
        
        # Render
        self.template_to_pdf(html, False)

    ## THIS SHOULD BE DOWN FOR EACH RECEIVER! so you'll need to use a for loop on distinct ball_carriers
    def receiver_page(self, receiver: int) -> None:
        pass_data = (self.o_data[self.o_data["Run_Type"].isnull()])
        pass_data['Complete_Pass'] = (~pass_data['Pass_Zone'].isin(['Not Thrown', 'Unknown'])) & (pass_data["Result"] != 0)
        pass_attempts = len(pass_data["Complete_Pass"])
        completions = pass_data["Complete_Pass"].sum()
        total_yards = pass_data["Distance"].sum()
        average_yards = round(pass_data["Distance"].mean(), 2)
        touchdowns = pass_data["Event"].str.count("Touchdown").sum()
        long = pass_data["Distance"].max()
        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        svg_path = os.path.dirname(__file__) + '\static\american-football-helmet-svgrepo-com.svg'
        title_template = env.get_template('postgame_report/report_pages/receiver.html')
        html = title_template.render(image_path = image_path, svg_path = svg_path, receiver = receiver, completions=completions,
                                     total_yards=total_yards, average_yards=average_yards, touchdowns=touchdowns, pass_attempts=pass_attempts, long=long)
        # Render
        self.template_to_pdf(html, False)
    
    