from flask import Flask, render_template
from flask_cors import CORS

import config
from app.blueprints.analytics import analytics_bp
from app.blueprints.feeds import feeds_bp
from app.filters.custom_filters import initialize_filters
from libs.database import initialize_database

# Create Flask API
app = Flask(
    __name__, static_folder=config.STATIC_DIR, template_folder=config.TEMPLATES_DIR
)
app.config.from_object("config")
app.secret_key = "eccpecckimehetsz"

cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Configure SQLAlchemy for PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = config.pow_db_config_str
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database within the application context
initialize_database(app)
initialize_filters()

# Flask Blueprints
app.register_blueprint(feeds_bp)
app.register_blueprint(analytics_bp)


# Flask Base Routing
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html"), 404


@app.route("/")
def home_page():
    page_title = "Home"
    return render_template("pages/home.html", page_title=page_title)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG, threaded=True)
