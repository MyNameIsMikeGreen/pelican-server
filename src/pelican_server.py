from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def root():
        return """
        <h1>Welcome to the Pelican Server</h1>
        <p>
            Activation endpoint available at: <b>/actions/activate</b><br />
            Deactivate endpoint available at: <b>/actions/deactivate</b><br />
            Status endpoint available at: <b>/status</b><br />
        </p>
        """

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
