from waitress import serve
from extensions import app

from views import views
app.register_blueprint(views, url_prefix="/")

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Internal server error", 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000, threads=6)
