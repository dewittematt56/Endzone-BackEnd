from database.models import *
from sqlalchemy import *

def load_models_json(models: "list[Models]") -> "list[dict]":
    json = []
    for model in models:
        json.append({
            "id": model.Model_ID,
            "ModelName": model.Model_Name,
            "ModelClass": model.Model_Class,
            "ModelType": model.Model_Type,
            "ModelPredictor": model.Model_Predictor,
            "ModelAccuracy": model.Model_Accuracy,
            "ModelTrainingSize": model.Model_Training_Size,
            "TeamCode": model.Team_Code,
            "Creator": model.Creator,
            "Creation_Date": model.Creation_Date
        })
    return json

def load_one_model_json(model: Models) -> "dict":
    return {
        "id": model.Model_ID,
        "ModelName": model.Model_Name,
        "ModelClass": model.Model_Class,
        "ModelType": model.Model_Type,
        "ModelPredictor": model.Model_Predictor,
        "ModelAccuracy": model.Model_Accuracy,
        "ModelTrainingSize": model.Model_Training_Size,
        "TeamCode": model.Team_Code,
        "Creator": model.Creator,
        "Creation_Date": model.Creation_Date
    }
    
    
