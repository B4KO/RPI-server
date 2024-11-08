from flask import Blueprint, render_template

home_routes = Blueprint('home_routes', __name__)

@home_routes.route('/', methods=['GET'])
def home():
    return render_template('index.html')
