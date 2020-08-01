from flask import Blueprint, request, render_template, redirect, url_for, abort, flash, jsonify

from app.module_api.providers import ApiProvider
provider = ApiProvider()

# JSON API
blueprint_api = Blueprint('api', __name__, url_prefix='/api')

# GET /api/_list_all
@blueprint_api.route('/_list_all')
def _list_all():
	return provider.listAll()

# GET /api/_find_parking/<point_id>
@blueprint_api.route('/_find_parking/<point_id>')
def _find_parking(point_id):
	return provider.findParking(point_id)

# GET /api/_shortest_path?source_lon=<source_lon>&source_lat=<source_lat>&target_lon=<target_lon>&target_lat=<target_lat>
@blueprint_api.route('/_shortest_path')
def _shortest_path():
	source_lon = request.args.get('source_lon', '', type=str)
	source_lat = request.args.get('source_lat', '', type=str)
	target_lon = request.args.get('target_lon', '', type=str)
	target_lat = request.args.get('target_lat', '', type=str)
	return provider.shortestPath(source_lon, source_lat, target_lon, target_lat)
