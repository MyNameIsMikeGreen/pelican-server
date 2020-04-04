from flask import jsonify


def activate():
    return jsonify({"result": "activated"})


def deactivate():
    return jsonify({"result": "deactivated"})
