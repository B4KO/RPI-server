# app/errors.py
from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not Found'}), 404

@errors.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500
