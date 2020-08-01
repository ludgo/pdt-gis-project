import json
from sqlalchemy import create_engine

from app.module_api.queries import *
from app.module_api.properties import *

# contains connection pool engine thereby provides controllers with query execution
class PostgreSqlProvider:

	def __init__(self):
		# initialize connection pool engine
		DB_URL = 'postgresql://{}:{}@{}:{}/{}'.format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
		self.engine = create_engine(DB_URL, pool_size=10, max_overflow=0, echo=True)
		self.engine.connect()

class ApiProvider(PostgreSqlProvider):

	def rowToJson(self, rowproxy):
		result = rowproxy.items()[0][1] # https://stackoverflow.com/a/50141868/5148218
		return json.dumps(result)

	def listAll(self):
		rowproxy = self.engine.execute(SELECT_ALL).fetchone()
		return self.rowToJson(rowproxy)

	def findParking(self, point_id):
		rowproxy = self.engine.execute(SELECT_PARKING_NEARBY, point_id=point_id).fetchone()
		return self.rowToJson(rowproxy)

	def shortestPath(self, source_lon, source_lat, target_lon, target_lat):
		rowproxy = self.engine.execute(SELECT_DIJKSTRA, source_lon=source_lon, source_lat=source_lat, \
			target_lon=target_lon, target_lat=target_lat).fetchone()
		return self.rowToJson(rowproxy)

