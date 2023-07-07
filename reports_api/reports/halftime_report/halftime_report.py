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
import sys
import datetime

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./reports_api/reports'))
env.globals.update(static='./reports_api/reports/static')

class HalftimeReport():
    def __init__(self, options: 'list[str]', goodTeam: str, goodTeamCode: str, enemyTeam: str, enemyTeamCode: str) -> None:
        goodPlays = []
        goodOPlays = []
        goodDPlays = []

        games = db.session.query(Game).filter(Game.Home_Team_Code == goodTeamCode or Game.Away_Team_Code == goodTeamCode).all()

        for game in games:
            goodPlays.append(db.session.query(Play).filter(Play.Game_ID == game.Game_ID).all())

        goodOPlays = db.session.query(Play).filter(Play.Posession_Code == goodTeamCode).all()

        for play in goodPlays:
            if play.Possession != goodTeam:
                goodDPlays.append(play)

        enemyPlays = []
        enemyOPlays = []
        enemyDPlays = []

        games = db.session.query(Game).filter(Game.Home_Team_Code == enemyTeamCode or Game.Away_Team_Code == enemyTeamCode).all()

        for game in games:
            enemyPlays.append(db.session.query(Play).filter(Play.Game_ID == game.Game_ID).all())

        enemyOPlays = db.session.query(Play).filter(Play.Posession_Code == enemyTeamCode).all()

        for play in enemyPlays:
            if play.Possession != enemyTeam:
                enemyDPlays.append(play)
        




if __name__ == "__main__":
    test = HalftimeReport()