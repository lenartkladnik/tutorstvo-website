from views import views
from waitress import serve
from extensions import db, login_manager, app
from resources import secrets

app.config["SECRET_KEY"] = secrets['db']

login_manager.login_view = "views.login"  

with app.app_context():
    db.create_all()

app.register_blueprint(views, url_prefix="/")

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Internal server error", 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000, threads=6)