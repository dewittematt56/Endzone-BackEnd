from flask import Blueprint, Response, render_template

pages_api = Blueprint("Pages", __name__, template_folder = "pages", static_folder = "pages")

@pages_api.route('/', methods = ["GET"])
def Home():
    return render_template("/home/home.html")

@pages_api.route('/login', methods = ["GET"])
def Login():
    return render_template("/login/login.html")

@pages_api.route('/endzone/hub', methods = ["GET"])
def Hub():
    return "Hub"