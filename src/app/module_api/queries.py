from sqlalchemy.sql import text

# Matches GeoJSON https://geojson.org/
# always validate against
# http://geojsonlint.com/

TEMPLATE_FEATURE_COLLECTION = '''
	SELECT row_to_json(collection)
	FROM (
		SELECT 'FeatureCollection' AS type, array_to_json(array_agg(
			jsonb_build_object(
				'type',			'Feature',
				'gid',			gid,
				'geometry',		ST_AsGeoJSON(ST_Transform(way, 4326))::json, -- SRID 4326 for WGS84
				'properties',	to_jsonb(row) - 'gid' - 'way'
			)
		)) AS features
		FROM (
			{}
		) AS row
	) AS collection
;'''

SELECT_ALL = text(TEMPLATE_FEATURE_COLLECTION.format('''
			SELECT osm_id AS gid, name, amenity, way
			FROM planet_osm_point
			WHERE amenity IN ('dentist', 'doctors', 'hospital')
'''))

SELECT_PARKING_NEARBY = text(TEMPLATE_FEATURE_COLLECTION.format('''
			WITH point AS (
				SELECT way FROM planet_osm_point WHERE osm_id = :point_id
			)
			SELECT osm_id AS gid, polygon.way, way_area, name, access,
				ST_DistanceSphere(ST_Transform(point.way, 4326), ST_Transform(polygon.way, 4326)) AS meters
			FROM planet_osm_polygon AS polygon, point
			WHERE amenity IN ('parking', 'parking_space')
			ORDER BY meters
			LIMIT 10
'''))

SELECT_DIJKSTRA = text(TEMPLATE_FEATURE_COLLECTION.format('''
			SELECT seq, geom_way AS way, osm_id AS gid, osm_name, km, kmh
			FROM pgr_dijkstra(
				'SELECT id, source, target, st_length(geom_way, true) as cost FROM osm_2po_4pgr',
				(SELECT source FROM osm_2po_4pgr
				ORDER BY ST_Distance(
					ST_StartPoint(geom_way),
					ST_SetSRID(ST_MakePoint(:source_lon, :source_lat), 4326),
					true
				) ASC
				LIMIT 1),
				(SELECT source FROM osm_2po_4pgr
				ORDER BY ST_Distance(
					ST_StartPoint(geom_way),
					ST_SetSRID(ST_MakePoint(:target_lon, :target_lat), 4326),
					true
				) ASC
				LIMIT 1),
				false -- ignore direction
			) as shortest_path
			JOIN osm_2po_4pgr ON shortest_path.edge = osm_2po_4pgr.id
			ORDER BY seq
'''))
