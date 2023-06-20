from flask import Blueprint, Response, request, jsonify
from flask_login import login_required
from database.models import *
import json
from .utils import *
from .CASE_model_manager import *
from server_utils import check_required_params

tars_api = Blueprint("tars_api", __name__)

@tars_api.route("/endzone/models/create", methods = ["POST"])
@login_required
def modelCreate():
    # To-Do Check Input Lengths and Values.
    try:
        data = json.loads(request.get_data())
        param_check = check_required_params(["GameIDs", "PredictionParams", "TeamOfInterest", "ModelName", "ModelType", "ModelClass", "ModelPredictor"], data.keys())
        if param_check: return param_check
        game_ids = data["GameIDs"]
        model_name = data["ModelName"]
        model_type = data["ModelType"]
        model_class = data["ModelClass"]
        model_predictor = data["ModelPredictor"]
        prediction_params = data["PredictionParams"]
        teamOfInterest = data["TeamOfInterest"]
        isGeneralizeFeatures = data["generalizeFeatures"]
        
        case_manager = CASE_Manager(model_name, model_type, model_class, model_predictor, game_ids, prediction_params, teamOfInterest, current_user.Current_Team, isGeneralizeFeatures)
        if model_class == "KNN":
            case_manager.train_knn_model()
        elif model_class == "RF":
            case_manager.train_rf_model()

        model_id = case_manager.save__model()
        model_accuracy = case_manager.accuracy
        return jsonify({"modelId": model_id, "modelAccuracy": model_accuracy})
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@tars_api.route("/endzone/models/predict", methods = ["POST"])
def modelPredict():
    try:
        payload_data = json.loads(request.data)
        model_id = payload_data["modelID"] 
        prediction_params = payload_data["predictionParams"] 
        case_predictor = CASE_Predictor(model_id)
        prediction = case_predictor.predict_play(prediction_params)
        return prediction
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
        
@tars_api.route("/endzone/models/get", methods = ["GET"])
def modelGet():
    try:
        if request.args.get('modelID'):
            model_id = request.args.get('modelID')
            model = db.session.query(Models).filter(Models.Team_Code == current_user.Current_Team).filter(Models.Model_ID == model_id).first()
            if model:
                return jsonify(load_one_model_json(model))
        else:
            models = db.session.query(Models).filter(Models.Team_Code == current_user.Current_Team).all()
            if models:
                return jsonify(load_models_json(models))
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    else:
        return Response("No Models Found", status = 400)
