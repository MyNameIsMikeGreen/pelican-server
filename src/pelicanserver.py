import logging
from subprocess import CalledProcessError

from flask import Flask, jsonify, send_from_directory, request

from automaticdeactivator import AutomaticDeactivator
from commands import CommandExecutor
from statusMonitor import StatusMonitor, Status

__author__ = "Mike Green"

STATIC_ROOT = "static"


class PelicanServer:

    def __init__(self, status_monitor, command_executor, automatic_deactivator=None):
        self.status_monitor = status_monitor
        self.command_executor = command_executor
        try:
            self.command_executor.deactivate()
        except CalledProcessError:
            logging.fatal("Failed to deactivate upon startup of Pelican Server. "
                          "MiniDLNA may not be installed. Aborting...")
            exit(1)
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
            timeout_seconds = request.args.get('timeout_seconds', default=None, type=int)
            if self.status_monitor.status == Status.ACTIVATED:
                return jsonify({"result": "already activated; no change"})
            self.command_executor.activate()
            self.status_monitor.set_status(Status.ACTIVATED)
            self.automatic_deactivator.reset_timer(timeout_seconds)
            return jsonify({"result": "activated"})

        @app.route("/actions/deactivate")
        def deactivate():
            if self.status_monitor.status == Status.DEACTIVATED:
                return jsonify({"result": "already deactivated; no change"})
            self.command_executor.deactivate()
            self.status_monitor.set_status(Status.DEACTIVATED)
            return jsonify({"result": "deactivated"})

        return app


def main():
    logging.basicConfig(filename='pelicanServerLog.log', level=logging.INFO)
    status_monitor = StatusMonitor()
    command_executor = CommandExecutor()
    pelican_server = PelicanServer(status_monitor, command_executor)
    pelican_server.app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
