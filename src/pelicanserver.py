from flask import Flask, jsonify, send_from_directory

from automaticdeactivator import AutomaticDeactivator
from commands import CommandExecutor
from statusMonitor import StatusMonitor, Status

__author__ = "Mike Green"

STATIC_ROOT = "static"

status_monitor = StatusMonitor()
command_executor = CommandExecutor()
automatic_deactivator = AutomaticDeactivator(status_monitor, command_executor)


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
        return jsonify({
            "status": status_monitor.status.name,
            "lastChange": str(status_monitor.last_change)
        })

    @app.route("/actions/activate")
    def activate():
        if status_monitor.status == Status.ACTIVATED:
            return jsonify({"result": "already activated; no change"})
        command_executor.activate()
        status_monitor.set_active(True)
        automatic_deactivator.reset_timer()
        return jsonify({"result": "activated"})

    @app.route("/actions/deactivate")
    def deactivate():
        if status_monitor.status == Status.DEACTIVATED:
            return jsonify({"result": "already deactivated; no change"})
        command_executor.deactivate()
        status_monitor.set_active(False)
        return jsonify({"result": "deactivated"})

    return app


def main():
    command_executor.deactivate()
    app = create_app()
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
