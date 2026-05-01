from flask import Flask

from routes import main_bp


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder=".",
        static_url_path="",
    )
    app.config["JSON_SORT_KEYS"] = False
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
