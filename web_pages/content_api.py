from flask import Flask, Blueprint, Response, render_template
from flask_login import login_required
content_api = Blueprint("content_api", __name__, template_folder="pages", static_folder="pages")

@content_api.route("/", methods = ["GET"])
def home():
    return render_template("/home/home.html")

@content_api.route("/login", methods = ["GET"])
def login():
    return render_template("/login/login.html")

@content_api.route("/endzone/hub", methods = ["GET"])
@login_required
def hub():
    return "test"