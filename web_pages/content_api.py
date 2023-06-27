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

@content_api.route("/products", methods = ["GET"])
def product():
    return render_template("/public/products/products.html")

@content_api.route("/login", methods = ["GET"])
def login():
    return render_template("/public/login/login.html")

@content_api.route("/about", methods = ["GET"])
def aboutUs():
    return render_template("/public/about/about.html")

@content_api.route("/account/create", methods = ["GET"])
def frontOffice():
    return render_template("/public/account-start/account-start.html")

@content_api.route("/account/terms", methods = ["GET"])
def accountTermsServices():
    return render_template("/public/terms-conditions/terms-conditions.html")

@content_api.route("/account/user", methods = ["GET"])
def accountUser():
    return render_template("/public/user-create/user-create.html")

# Login in Required -- since user's must be logged in to create an organization.
@content_api.route("/account/org", methods = ["GET"])
@login_required
def accountOrg():
    return render_template("/public/org-create/org-create.html")

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

@login_required
@content_api.route("/endzone/data/game/manual")
def ManualGame():
    return render_template("/data/manual-game/manual-game.html")

@login_required
@content_api.route("/endzone/data/manage")
def ManageData():
    return render_template("/data/manage-data/manage-data.html")

@content_api.route("/endzone/account/profile", methods = ["GET"])
@login_required
def profile():
    return render_template("/user/profile/profile.html")

@content_api.route("/endzone/org/home", methods = ["GET"])
@login_required
def OMHome():
    return render_template("/org/om_home/om_home.html")

@content_api.route("/endzone/org/profile", methods = ["GET"])
@login_required
def OMProfile():
    return render_template("/org/om_profile/om_profile.html")

@content_api.route("/endzone/org/members", methods = ["GET"])
@login_required
def OMMembers():
    return render_template("/org/om_members/om_members.html")

@content_api.route("/endzone/data/viewer", methods = ["GET"])
@login_required
def DataViewer():
    return render_template("/data/data-viewer/data-viewer.html")

@content_api.route("/endzone/pregame/report", methods = ["GET"])
@login_required
def PregameReportPage():
    return render_template("/pregame/report/pregame_report.html")

@content_api.route("/endzone/team/home", methods = ["GET"])
@login_required
def TMHome():
    return render_template("/team/tm_home/tm_home.html")

@content_api.route("/endzone/team/profile", methods = ["GET"])
@login_required
def TMProfile():
    return render_template("/team/tm_profile/tm_profile.html")

@content_api.route("/endzone/team/members", methods = ["GET"])
@login_required
def TMMembers():
    return render_template("/team/tm_members/tm_members.html")
=======
@content_api.route("/endzone/pregame/hub", methods = ["GET"])
@login_required
def PregameHub():
    return render_template("/pregame/hub/pregame_hub.html")

@content_api.route("/endzone/pregame/dashboard", methods = ["GET"])
@login_required
def PregameDashboard():
    return render_template("/pregame/dashboard/pregame_dashboard.html")
