from flask import Flask, jsonify, send_from_directory

STATIC_ROOT = "static"


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def root():
        return static_content("index.html")

    @app.route('/<path:path>')
    def static_content(path):
        """Serve static content relative from STATIC_ROOT directory."""
        return send_from_directory(STATIC_ROOT, path)

    @app.route("/actions/activate")
    def activate():
        return jsonify({"test": "activated"})

    @app.route("/actions/deactivate")
    def deactivate():
        return jsonify({"test": "deactivated"})

    @app.route("/status")
    def status():
        return jsonify({"status": "Some status"})

    return app


def main():
    app = create_app()
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
