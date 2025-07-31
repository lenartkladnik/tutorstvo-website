from flask import render_template
from waitress import serve
from extensions import app
from resources import log, DEBUG

if DEBUG:
    log(f"Running in debug mode, with level {DEBUG}!", "app", "warning")

log("Sarting server", "app")

from views import views
app.register_blueprint(views, url_prefix="/")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    if DEBUG:
        return e, 500

    return "Internal server error", 500

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    threads = 6
    log(f"The app is served on {host}:{port} with {threads} threads.", "app");
    serve(app, host=host, port=port, threads=threads)
