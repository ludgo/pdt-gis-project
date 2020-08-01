import os
from flask import Flask, render_template, url_for


app = Flask(__name__)

# configure application from file
app.config.from_object('config')

''' START
following 2 methods ensure static css in not cached, thus updated by browser every time it has changed
'''
@app.context_processor
def override_url_for():
	return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
	if endpoint == 'static':
		filename = values.get('filename', None)
		if filename:
			file_path = os.path.join(app.root_path,	endpoint, filename)
			values['q'] = int(os.stat(file_path).st_mtime)
	return url_for(endpoint, **values)
# END

# whole app's 404
@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

# integrate separate blueprints
from app.module_api.controllers import blueprint_api
app.register_blueprint(blueprint_api)
from app.module_app.controllers import blueprint_app
app.register_blueprint(blueprint_app)

