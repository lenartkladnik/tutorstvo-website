from flask import render_template, render_template_string, g
from waitress import serve
from extensions import app, scheduler
from resources import log, DEBUG, FORM_VALIDATION_OFF, secrets
from views import current_user, login_required
import traceback
import sys

try:
    if __name__ == "__main__":
        if DEBUG:
            log(f"Running in debug mode, with level {DEBUG}, DO NOT RUN IN A PRODUCTION ENVIRONMENT!", "app", "warning")

        if FORM_VALIDATION_OFF:
            log(f"Running with form validation disabled, DO NOT RUN IN A PRODUCTION ENVIRONMENT!", "app", "warning")

        log("Sarting server", "app")

        from views import views
        app.register_blueprint(views, url_prefix="/")

        @app.errorhandler(404)
        def page_not_found(e):
            return render_template("404.html"), 404

        @app.errorhandler(Exception)
        def handle_exception(e):
            login_required(lambda *, context: context)() # Hacky way to get context into g.context

            if g.context and current_user(g.context).is_admin():
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

                return render_template_string("""<h1>Exception Occurred</h1>\n<pre>{{ tb }}</pre>""", tb=tb), 500

            return render_template("500.html"), 500

        host = "0.0.0.0"

        try:
            port = int(secrets["port"])
            threads = int(secrets["threads"])
        except ValueError:
            raise RuntimeError("'port' and 'threads' values must be integers!")

        log(f"The app is served on {host}:{port} with {threads} threads.", "app");
        serve(app, host=host, port=port, threads=threads)

finally:
    log("Exiting...", "app")
    if scheduler.running:
        scheduler.shutdown()
