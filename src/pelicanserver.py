from flask import Flask, jsonify, send_from_directory

from automaticdeactivator import AutomaticDeactivator
from commands import CommandExecutor
from statusMonitor import StatusMonitor, Status

__author__ = "Mike Green"

STATIC_ROOT = "static"


class PelicanServer:

    def __init__(self, status_monitor, command_executor, automatic_deactivator=None):
        self.status_monitor = status_monitor
        self.command_executor = command_executor
        self.command_executor.deactivate()
        if automatic_deactivator:
            self.automatic_deactivator = automatic_deactivator
        else:
            self.automatic_deactivator = AutomaticDeactivator(self.command_executor, self.status_monitor)
        self.app = self._create_app()

    def _create_app(self):
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
                "status": self.status_monitor.status.name,
                "lastChange": str(self.status_monitor.last_change),
                "lastChangeBy": self.status_monitor.last_change_by
            })

        @app.route("/actions/activate")
        def activate():
            if self.status_monitor.status == Status.ACTIVATED:
                return jsonify({"result": "already activated; no change"})
            self.command_executor.activate()
            self.status_monitor.set_active(True)
            self.automatic_deactivator.reset_timer()
            return jsonify({"result": "activated"})

        @app.route("/actions/deactivate")
        def deactivate():
            if self.status_monitor.status == Status.DEACTIVATED:
                return jsonify({"result": "already deactivated; no change"})
            self.command_executor.deactivate()
            self.status_monitor.set_active(False)
            return jsonify({"result": "deactivated"})

        return app


def main():
    status_monitor = StatusMonitor()
    command_executor = CommandExecutor()
    pelican_server = PelicanServer(status_monitor, command_executor)
    pelican_server.app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
