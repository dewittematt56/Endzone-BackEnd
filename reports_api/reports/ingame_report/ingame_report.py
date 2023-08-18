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
    def __init__(self, team_of_interest: str, game: str, team_code: str, prior_games: list) -> None:
        self.team_of_interest = team_of_interest ## either self team or opponent
        self.game_id = game
        self.prior_game_ids = prior_games
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
        self.prior_game_ids = ["643ad3ef-8b71-422d-ba03-f150637f148e", "a8ebe210-8ae1-4554-baef-9e73b35052ae", "35903bf5-dc8d-4512-b7ba-ed6d18ecca76"]


        self.get_data()
        self.split_data()
        self.get_prior_game_data()
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

    
    def get_prior_game_data(self) -> None:
        db_engine = create_engine(db_uri)
        Session = sessionmaker(db_engine)
        session = Session()
        team_game_data = pd.read_sql(session.query(Game).filter(Game.Game_ID.in_(self.prior_game_ids)).statement, db_engine)
        team_game_data['Game_Date'] = pd.to_datetime(team_game_data['Game_Date'])
        team_game_data['Game_Date'] = team_game_data['Game_Date'].dt.strftime('%A, %d %B %Y')
        temp_plays = pd.read_sql(session.query(Play).filter(Play.Game_ID.in_(self.prior_game_ids)).statement, db_engine)
        df_forms = pd.read_sql(session.query(Formations).filter(Formations.Team_Code == self.team_code).statement, db_engine)
        df_plays = pd.merge(temp_plays, df_forms, left_on='O_Formation', right_on="Formation", how='inner')
        team_play_data = pd.merge(df_plays, team_game_data, on='Game_ID', how='inner')
        self.prior_penalties = pd.read_sql(session.query(Penalty).filter(Penalty.Game_ID.in_(self.prior_game_ids)).statement, db_engine)
        dPlays = team_play_data[(team_play_data["Possession"] != self.team_of_interest)]
        oPlays = team_play_data[(team_play_data["Possession"] == self.team_of_interest)]
        self.oPriorData = enrich_data(oPlays, self.team_of_interest)
        self.dPriorData = enrich_data(dPlays, self.team_of_interest)


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

    # Will take calculate the percentage the val is of the total
    # Used to dictate how big the bar for a specific stat should be
    # Pass it as a percentage to the frontend
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


    def o_overview_page(self) -> None:
        o_overview_template = env.get_template('ingame_report/report_pages/offense_overview.html')
        formation_play = groupedBarGraph(self.oData, "Formation", "Play_Type", "Play Type", "Result", "Average Yards Gained")
        down_coverage = groupedBarGraph(self.oData, "Down", "Coverage", "Coverage")
        distance_coverage = groupedBarGraph(self.oData, "Distance", "Coverage", "Coverage")
        o_formation_coverage = groupedBarGraph(self.oData, "O_Formation", "Coverage", "Coverage")
        field_pos_coverage = groupedBarGraph(self.oData, "Field_Group", "Coverage", "Coverage")
        barGraphList = [{"title": "Avg Yards Gained for Formation by Play Type", "graph": formation_play}, \
                     {"title": "Down by Coverage", "graph": down_coverage}, \
                     {"title": "Distance by Coverage", "graph": distance_coverage}, \
                     {"title": "O Formation by Coverage", "graph": o_formation_coverage}, \
                     {"title": "Field Position by Coverage", "graph": field_pos_coverage}
        ]

        down1_coverage = categorical_pieChart_wrapper(self.oData.query('Down == 1'), "Coverage", "1st Down Coverage Frequency")
        down2_coverage = categorical_pieChart_wrapper(self.oData.query('Down == 2'), "Coverage", "2nd Down Coverage Frequency")
        down3_coverage = categorical_pieChart_wrapper(self.oData.query('Down == 3'), "Coverage", "3rd Down Coverage Frequency")
        downCoverageList = [{"title": "1st Down Coverage Frequency", "graph": down1_coverage}, \
                        {"title": "2nd Down Coverage Frequency", "graph": down2_coverage}, \
                        {"title": "3rd Down Coverage Frequency", "graph": down3_coverage}
        ]

        short_coverage = categorical_pieChart_wrapper(self.oData.query('Down_Group == "Short"'), "Coverage", "Coverage Frequency")
        medium_coverage = categorical_pieChart_wrapper(self.oData.query('Down_Group == "Medium"'), "Coverage", "Coverage Frequency")
        long_coverage = categorical_pieChart_wrapper(self.oData.query('Down_Group == "Long"'), "Coverage", "Coverage Frequency")
        downGroupCoverageList = [{"title": "Short Coverage Frequency", "graph": short_coverage}, \
                                {"title": "Medium Coverage Frequency", "graph": medium_coverage}, \
                                {"title": "Long Coverage Frequency", "graph": long_coverage}
        ]

        prior_coverage_play = groupedBarGraph(self.oData, "Coverage", "Play_Type", "Play Type")
        during_coverage_play = groupedBarGraph(self.oData, "Coverage", "Play_Type", "Play Type")
        prior_formation_pressure = stackedBarGraph(self.oData, "Formation", ["Pressure_Left", "Pressure_Middle", "Pressure_Right"], "Formation by Pressure")
        during_formation_pressure = stackedBarGraph(self.oData, "Formation", ["Pressure_Left", "Pressure_Middle", "Pressure_Right"], "Formation by Pressure")
        priorDuringList = [{"title": "Prior: Coverage by Play Type", "graph": prior_coverage_play}, \
                                {"title": "During: Coverage by Play Type", "graph": during_coverage_play}, \
                                {"title": "Prior: Formation by Pressure", "graph": prior_formation_pressure}, \
                                {"title": "Formation by Pressure", "graph": during_formation_pressure}
        ]

        data = barGraphList + downCoverageList + downGroupCoverageList + priorDuringList

        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        html = o_overview_template.render(image_path = image_path, data = data)
        # Render this sucker!
        self.template_to_pdf(html, True)


    def d_overview_page(self) -> None:
        o_overview_template = env.get_template('ingame_report/report_pages/defense_overview.html')

        down_play = groupedBarGraph(self.dData, "Down", "Coverage", "Coverage")
        personnel_formation = groupedBarGraph(self.dData, "Personnel", "Formation", "Formation")
        throw_attempts = categorical_pieChart_wrapper(self.dData.query('Pass_Zone != "Non-Passing-Play"'), "Pass_Zone", "Pass Zone Frequency")
        formation_field_pos = groupedBarGraph(self.dData, "Formation", "Field_Group", "Field Position")
        frontPage = [{"title": "Down by Play Type", "graph": down_play}, \
                     {"title": "Personnel by Formation", "graph": personnel_formation}, \
                     {"title": "Pass Zone Frequency", "graph": throw_attempts}, \
                     {"title": "Formation by Field Position", "graph": formation_field_pos}
        ]

        down1_play = categorical_pieChart_wrapper(self.dData.query('Down == 1'), "Play_Type", "1st Down Play Type Frequency")
        down2_play = categorical_pieChart_wrapper(self.dData.query('Down == 2'), "Play_Type", "2nd Down Play Type Frequency")
        down3_play = categorical_pieChart_wrapper(self.dData.query('Down == 3'), "Play_Type", "3rd Down Play Type Frequency")
        downPlayList = [{"title": "1st Down Play Type Frequency", "graph": down1_play}, \
                        {"title": "2nd Down Play Type Frequency", "graph": down2_play}, \
                        {"title": "3rd Down Play Type Frequency", "graph": down3_play}
        ]

        short_play = categorical_pieChart_wrapper(self.dData.query('Down_Group == "Short"'), "Play_Type", "Short Play Type Frequency")
        medium_play = categorical_pieChart_wrapper(self.dData.query('Down_Group == "Medium"'), "Play_Type", "Medium Play Type Frequency")
        long_play = categorical_pieChart_wrapper(self.dData.query('Down_Group == "Long"'), "Play_Type", "Long Play Type Frequency")
        downGroupPlayList = [{"title": "Short Play Type Frequency", "graph": short_play}, \
                                {"title": "Medium Play Type Frequency", "graph": medium_play}, \
                                {"title": "Long Play Type Frequency", "graph": long_play}
        ]

        prior_formation_play = groupedBarGraph(self.dPriorData, "Formation", "Play_Type", "Play Type")
        during_formation_play = groupedBarGraph(self.dData, "Formation", "Play_Type", "Play Type")
        strength_prior = categorical_pieChart_wrapper(self.dPriorData, "To_Strength", "Prior: Plays into Strength")
        strength_during = categorical_pieChart_wrapper(self.dData, "To_Strength", "During: Plays into Strength")

        tempDataDuring = self.dData
        tempDataDuring['To_Boundary'] = tempDataDuring["Play_Type_Dir"] == tempDataDuring['Hash']
        boundary_during = categorical_pieChart_wrapper(tempDataDuring, "To_Boundary", "During: Plays into Boundary")

        tempDataPrior = self.dPriorData
        tempDataPrior['To_Boundary'] = tempDataPrior["Play_Type_Dir"] == tempDataPrior['Hash']
        boundary_prior = categorical_pieChart_wrapper(tempDataPrior, "To_Boundary", "Prior: Plays into Boundary")

        priorDuringList = [{"title": "Prior: Formation by Play Type", "graph": prior_formation_play}, \
                                {"title": "During: Formation by Play Type", "graph": during_formation_play}, \
                                {"title": "Prior: Plays into Strength", "graph": strength_prior}, \
                                {"title": "During: Plays into Strength", "graph": strength_during}, \
                                {"title": "Prior: Plays into Boundary", "graph": boundary_prior}, \
                                {"title": "During: Plays into Boundary", "graph": boundary_during}
        ]


        data = frontPage + downPlayList + downGroupPlayList + priorDuringList

        image_path = os.path.dirname(__file__) + '\static\endzone_shield.png'
        html = o_overview_template.render(image_path = image_path, frontPage=frontPage, downPlayList=downPlayList, downGroupPlayList=downGroupPlayList, priorDuringList=priorDuringList)
        # Render this sucker!
        self.template_to_pdf(html, True)

    def run_report(self):
        # self.title_page()
        self.d_overview_page()

        
if __name__ == "__main__":
    test = IngameReport("team", "game", "team_code")
