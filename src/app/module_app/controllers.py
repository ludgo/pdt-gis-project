from flask import Blueprint, request, render_template, redirect, url_for, abort, flash, jsonify

# static web page
blueprint_app = Blueprint('app', __name__, url_prefix='/app')

# GET /app
@blueprint_app.route('/')
def main_page():
	return render_template('module_app/map.html')
