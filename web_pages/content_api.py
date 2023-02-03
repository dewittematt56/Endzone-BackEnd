from flask import Flask, Blueprint, Response, render_template
from flask_login import login_required
content_api = Blueprint("content_api", __name__, template_folder="pages", static_folder="pages")

@content_api.route("/", methods = ["GET"])
def home():
    return render_template("/home/home.html")

@content_api.route("/contact", methods = ["GET"])
def contactUs():
    return render_template("/contact-us/contact-us.html")

@content_api.route("/pricing", methods = ["GET"])
def pricing():
    return render_template("/pricing/pricing.html")

@content_api.route("/products", methods = ["GET"])
def product():
    return render_template("/products/products.html")

@content_api.route("/login", methods = ["GET"])
def login():
    return render_template("/login/login.html")

@content_api.route("/account/create", methods = ["GET"])
def frontOffice():
    return render_template("/front-office/front-office.html")

@content_api.route("/account/terms", methods = ["GET"])
def accountTermsServices():
    return render_template("/terms-conditions/terms-conditions.html")

@content_api.route("/account/user", methods = ["GET"])
def accountUser():
    return render_template("/user-create/user-create.html")

@content_api.route("/account/team", methods = ["GET"])
def accountTeam():
    return render_template("/team-create/team-create.html")

@content_api.route("/endzone/hub", methods = ["GET"])
@login_required
def hub():
    return render_template("/hub/hub.html")