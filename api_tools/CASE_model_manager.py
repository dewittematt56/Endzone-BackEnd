import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import copy
import pickle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import db_uri
from database.models import *

db_engine = create_engine(db_uri)
Session = sessionmaker(db_engine)
session = Session()

def transform_pressure(df: pd.DataFrame) -> pd.DataFrame:
    # New Column for Boolean Pressure
    pressure_columns = []
    for column in df.columns:
        if "Pressure" in column:
            pressure_columns.append(column)

    df["Pressure"] = 0
    pressure_condition = (df[pressure_columns] >= 1).any(axis=1)
    df.loc[pressure_condition, "Pressure"] = 1
    df.drop(columns=pressure_columns, inplace=True)
    return df

def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df["Coverage"] != "Not Selected") & (df["D_Formation"] != "Not Selected") & (df["Distance"] != "Not Selected") & (df["Down"] != "Not Selected") & (df["Formation"] != "Not Selected") & (df["Formation_Strength"] != "Not Selected") & (df["Hash"] != "Not Selected") & (df["Pressure"] != "Not Selected") & (df["Quarter"] != "Not Selected") & (df["Yard"] != "Not Selected") & (df["Play_Type"] != "Unknown")]
    return df

class CASE_Manager(object):
    def __init__(self, model_name: str, model_type: str, model_class: str, model_predictor: str, game_ids: 'list[str]', prediction_params: 'list[str]', team_of_interest: str, team_code: str, isGeneralizeFeatures: bool = False) -> None:
        self.model_name = model_name
        self.model_type = model_type
        self.model_class = model_class
        self.model_predictor = model_predictor
        self.game_ids = game_ids
        self.predictor_params = prediction_params
        self.team_of_interest = team_of_interest
        self.team_code = team_code
        self.isGeneralizeFeatures = isGeneralizeFeatures
        self.training_length = 0
        self.categorical_params = []
        self.numeric_params = []
        self.accuracy = None
        self.model = None
        self.__getData__()
        self.__prep_training_data__()

    def __getData__(self) -> None:
        self.params = copy.deepcopy(self.predictor_params)
        if self.model_predictor == "Pressure": 
            self.params.extend(["Pressure_Left", "Pressure_Middle", "Pressure_Right"])
        else:
            self.params.append(self.model_predictor)
        self.params.extend(["Possession"])
        self.data = pd.read_sql(session.query(*[getattr(Play, col) for col in self.params]).filter(Play.Game_ID.in_(self.game_ids)).statement, db_engine)

        if self.model_type == "Defense":
            self.data = self.data[self.data["Possession"] != self.team_of_interest]
        elif self.model_type == "Offense":
            self.data = self.data[self.data["Possession"] == self.team_of_interest]
        
        
        if "Pressure_Left" in self.params or "Pressure_Middle" in self.params or "Pressure_Right" in self.params: 
            self.data = transform_pressure(self.data)
            self.model_predictor = "Pressure"
        
        self.data = self.data[(self.data[self.model_predictor] != 'Not Selected') & (self.data[self.model_predictor] != 'Unknown')]
        self.data.dropna(inplace=True)
        self.data = self.__prepData__(self.data)
        self.training_length = len(self.data)

    def generalizeCoverage(self):
        self.data['GeneralCoverage'] = self.data['Coverage'].apply(lambda x: 'Zone' if 'Zone' in x else 'Man')
        self.model_predictor = "GeneralCoverage"
    
    def generalizePlayType(self):
        self.data['GeneralPlayType'] = self.data['Play_Type'].apply(lambda x: 'Run' if 'Run' in x or "Option" in x else 'Pass')
        self.model_predictor = "GeneralPlayType"

    def __prepData__(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.isGeneralizeFeatures:
            if self.model_predictor == "Coverage": self.generalizeCoverage()
            elif self.model_predictor == "Play_Type": self.generalizePlayType()

        categorical_endzone_columns = ["Pressure", "Coverage", "D_Formation", "O_Formation", "Formation_Strength", "Hash", "Possession", "Quarter", "Motion", "Play_Type", "Play", "Play_Type_Dir", "Pass_Zone", "Ball_Carrier"]
        for param in self.params:
            if param in categorical_endzone_columns: 
                df[param] = df[param].astype("category")
                if param in self.predictor_params: self.categorical_params.append(param)
            elif param in self.predictor_params: self.numeric_params.append(param)
        return df
    
    def __prep_training_data__(self):
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.data[self.predictor_params], self.data[self.model_predictor], test_size=0.2, random_state=123)
        self.preprocess_params = ColumnTransformer([
            ("numeric", preprocessing.StandardScaler(), self.numeric_params),
            ("categorical", OneHotEncoder(), self.categorical_params)
        ])
        self.X_train = self.preprocess_params.fit_transform(self.X_train)
        
        self.X_test = self.preprocess_params.transform(self.X_test)

    def train_knn_model(self):
        from sklearn.neighbors import KNeighborsClassifier
        knnModel = KNeighborsClassifier(n_neighbors=10)
        knnModel.fit(self.X_train, self.Y_train)
        self.__test_model__(knnModel)
        self.model = knnModel

    def train_rf_model(self):
        from sklearn.ensemble import RandomForestClassifier
        RF_Model = RandomForestClassifier(n_estimators=500, max_features=3, random_state=123)
        RF_Model.fit(self.X_train, self.Y_train)
        self.__test_model__(RF_Model)
        self.model = RF_Model

    def __test_model__(self, model): 
        predictions = model.predict(self.X_test)
        self.accuracy = accuracy_score(self.Y_test, predictions)

    def save__model(self):
        model = Models(self.model_name, self.model_class, self.model_type, self.model_predictor, pickle.dumps(self.preprocess_params), pickle.dumps(self.model), self.accuracy, self.training_length)
        session.add(model)
        session.commit()
        return model.Model_ID

class CASE_Predictor(object):
    def __init__(self, model_id) -> None:
        self.model_id = model_id
        self.__load_model__()

    def __load_model__(self):
        model = session.query(Models).filter(Models.Model_ID == self.model_id).first()
        self.model = pickle.loads(model.Model)
        self.preProcessingParams = pickle.loads(model.Model_Preprocessor)
        
    def predict_play(self, prediction_param_dict: dict) -> str:
        input_data = pd.DataFrame([prediction_param_dict], index=[0])
        input_data = self.preProcessingParams.transform(input_data)
        prediction = self.model.predict(input_data)
        return prediction[0]
    
