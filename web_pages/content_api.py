from flask import Flask, Blueprint, Response, render_template
from flask_login import login_required
content_api = Blueprint("content_api", __name__, template_folder="pages", static_folder="pages")

@content_api.route("/", methods = ["GET"])
def home():
    return render_template("/public/home/home.html")

@content_api.route("/contact", methods = ["GET"])
def contactUs():
    return render_template("/public/contact/contact.html")

@content_api.route("/pricing", methods = ["GET"])
def pricing():
    return render_template("/public/pricing/pricing.html")

@content_api.route("/product", methods = ["GET"])
def product():
    return render_template("/public/product/product.html")

@content_api.route("/login", methods = ["GET"])
def login():
    return render_template("/public/login/login.html")

@content_api.route("/about", methods = ["GET"])
def aboutUs():
    return render_template("/public/about/about.html")

@content_api.route("/account/create", methods = ["GET"])
def frontOffice():
    return render_template("/public/front-office/front-office.html")

@content_api.route("/account/terms", methods = ["GET"])
def accountTermsServices():
    return render_template("/public/terms-conditions/terms-conditions.html")

@content_api.route("/account/user", methods = ["GET"])
def accountUser():
    return render_template("/public/user-create/user-create.html")

@content_api.route("/account/team", methods = ["GET"])
def accountTeam():
    return render_template("/public/team-create/team-create.html")

@content_api.route("/endzone/hub", methods = ["GET"])
@login_required
def hub():
    return render_template("/endzone/hub/hub.html")

@content_api.route("/endzone/coaches-corner/hub", methods = ["GET"])
@login_required
def coachHub():
    return render_template("/coaches-corner/hub/coach_hub.html")

@content_api.route("/endzone/coaches-corner/formation", methods = ["GET"])
@login_required
def formation():
    return render_template("/coaches-corner/formation/formation.html")

@content_api.route("/endzone/data/hub")
@login_required
def dataHub():
    return render_template("/data/hub/data_hub.html")

@login_required
@content_api.route("/endzone/data/game")
def GamePage():
    return render_template("/data/create-game/create-game.html")

@login_required
@content_api.route("/endzone/data/game")
def CreateGame():
    return render_template("/data/create-game/create-game.html")