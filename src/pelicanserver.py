from flask import Flask, jsonify, send_from_directory

import commands
from statusMonitor import StatusMonitor

__author__ = "Mike Green"

STATIC_ROOT = "static"

status_monitor = StatusMonitor()
command_executor = commands.CommandExecutor()


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def root():
        return static_content("index.html")

    @app.route('/<path:path>')
    def static_content(path):
        """Serve static content relative from STATIC_ROOT directory."""
        return send_from_directory(STATIC_ROOT, path)

    @app.route("/status")
    def status():
        return jsonify({"status": status_monitor.status.name})

    @app.route("/actions/activate")
    def activate():
        status_monitor.set_active(True)
        command_executor.activate()
        return jsonify({"result": "activated"})

    @app.route("/actions/deactivate")
    def deactivate():
        status_monitor.set_active(False)
        command_executor.deactivate()
        return jsonify({"result": "deactivated"})

    return app


def main():
    app = create_app()
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
