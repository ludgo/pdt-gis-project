# Overview

We provide patients with a hint to find a convenient parking near their healthpoint.

# Scenarios

This is it in action:

- show medical points in Brussels city

![](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/scenario1.png)

- find n closest car parks

![](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/scenario2.png)

- display closest path from parking to healthpoint

![](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/scenario3.png)

# Application

[Backend](#backend) is written in [flask](http://flask.palletsprojects.com/en/1.1.x/) and it has 2 separate modules - GeoJSON API and web application. [Frontend](#frontend) is standard web stack, just for web application module. The frontend application communicates with backend using a [REST API](##api).

[readme.txt](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/readme.txt) documents flask application structure in detail.

[queries.py](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/app/module_api/queries.py) contains used SQL for scenarios (API calls).

# Frontend

Functionally, frontend buils on [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/api/). [map.html](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/app/templates/module_app/map.html) contains web content. Styles are at [style.css](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/app/static/css/style.css) and functionality, i.e. API calls, MapBox loading at [map.js](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/app/static/js/map.js). JavaScript Promises have been used for map clearing and populating consequently.

Reach webpage at

`GET /app`

# Backend

2 separate python modules are under standard flask application structure. The API module is backed by PostGIS database. Database properties are specified at [properties.py](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/src/app/module_api/properties.py).

Run application as
```
python run.py
```

## Data

Coming directly from [Open Street Maps](https://www.openstreetmap.org/). Database setup is specified at [dbsetup.txt](https://github.com/fiit-pdt-2019/gis-project-ludko/blob/master/dbsetup.txt).

## Api

Fulfils [GeoJSON](https://geojson.org/) specification - validated against [GeoJSONLint](http://geojsonlint.com/).

**List all healthpoints**

`GET /api/_list_all`

```
{
   "type":"FeatureCollection",
   "features":[
      {
         "gid":1306718888,
         "type":"Feature",
         "geometry":{
            "type":"Point",
            "coordinates":[
               4.195847,
               50.9095900992654
            ]
         },
         "properties":{
            "name":"OLV Ziekenhuis - Campus Asse",
            "amenity":"hospital"
         }
      },
      {
         "gid":1474127861,
         "type":"Feature",
         "geometry":{
            "type":"Point",
            "coordinates":[
               4.205983,
               50.9388144992602
            ]
         },
         "properties":{
            "name":null,
            "amenity":"dentist"
         }
      },
      ...
   ]
}
```
Database query behind

```
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
			SELECT osm_id AS gid, name, amenity, way
			FROM planet_osm_point
			WHERE amenity IN ('dentist', 'doctors', 'hospital')
		) AS row
	) AS collection
;
```


**Find 10 closest parking spots near healthpoint**

`GET /api/_find_parking/<point_id>`

<point_id> heathpoint gid

`GET /api/_find_parking/4772763723`

```
{
   "type":"FeatureCollection",
   "features":[
      {
         "gid":477342615,
         "type":"Feature",
         "geometry":{
            "type":"Polygon",
            "coordinates":[
               [
                  [
                     4.3660844,
                     50.8531617992756
                  ],
                  [
                     4.3660904,
                     50.8531452992756
                  ],
                  ...
               ]
            ]
         },
         "properties":{
            "name":null,
            "access":null,
            "meters":231.78119298,
            "way_area":187.535
         }
      },
      {
         "gid":477350235,
         "type":"Feature",
         "geometry":{
            "type":"Polygon",
            "coordinates":[
               [
                  [
                     4.366682,
                     50.8529936992756
                  ],
                  [
                     4.3666923,
                     50.8529737992756
                  ],
                  ...
               ]
            ]
         },
         "properties":{
            "name":null,
            "access":null,
            "meters":263.65216155,
            "way_area":233.186
         }
      },
      ...
      }
   ]
}
```

Database query behind

```
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
			WITH point AS (
				SELECT way FROM planet_osm_point WHERE osm_id = 4772763723
			)
			SELECT osm_id AS gid, polygon.way, way_area, name, access,
				ST_DistanceSphere(ST_Transform(point.way, 4326), ST_Transform(polygon.way, 4326)) AS meters
			FROM planet_osm_polygon AS polygon, point
			WHERE amenity IN ('parking', 'parking_space')
			ORDER BY meters
			LIMIT 10
		) AS row
	) AS collection
;
```

**Find closest path between points**  
Closest path by dijkstra. We use undirected version since with assume app users walking from car park to healthpoint.

`GET /api/_shortest_path?source_lon=<source_lon>&source_lat=<source_lat>&target_lon=<target_lon>&target_lat=<target_lat>`

<source_lon> source longitude  
<source_lat> source latitude  
<target_lon> target longitude  
<target_lat> target latitude

`GET /api/_shortest_path?source_lon=4.3536106&source_lat=50.8606758992742&target_lon=4.3652371&target_lat=50.8551822992752`

```
{
   "type":"FeatureCollection",
   "features":[
      {
         "gid":11479928,
         "type":"Feature",
         "geometry":{
            "type":"LineString",
            "coordinates":[
               [
                  4.3533633,
                  50.8603631
               ],
               [
                  4.3549992,
                  50.8599097
               ],
               ...
            ]
         },
         "properties":{
            "km":0.1398901,
            "kmh":30,
            "seq":1,
            "osm_name":"Rue Simons - Simonsstraat"
         }
      },
      {
         "gid":14590428,
         "type":"Feature",
         "geometry":{
            "type":"LineString",
            "coordinates":[
               [
                  4.3566786,
                  50.8595092
               ],
               [
                  4.3565401,
                  50.8595328
               ],
               ...
            ]
         },
         "properties":{
            "km":0.1121844,
            "kmh":40,
            "seq":2,
            "osm_name":"Rue du Peuple - Volksstraat"
         }
      },
      ...
      }
   ]
}
```

Database query behind

```
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
			SELECT seq, geom_way AS way, osm_id AS gid, osm_name, km, kmh
			FROM pgr_dijkstra(
				'SELECT id, source, target, st_length(geom_way, true) as cost FROM osm_2po_4pgr',
				(SELECT source FROM osm_2po_4pgr
				ORDER BY ST_Distance(
					ST_StartPoint(geom_way),
					ST_SetSRID(ST_MakePoint(4.3536106, 50.8606758992742), 4326),
					true
				) ASC
				LIMIT 1),
				(SELECT source FROM osm_2po_4pgr
				ORDER BY ST_Distance(
					ST_StartPoint(geom_way),
					ST_SetSRID(ST_MakePoint(4.3652371, 50.8551822992752), 4326),
					true
				) ASC
				LIMIT 1),
				false -- ignore direction
			) as shortest_path
			JOIN osm_2po_4pgr ON shortest_path.edge = osm_2po_4pgr.id
			ORDER BY seq
		) AS row
	) AS collection
;
```

# Shortest path algorithm

For patient to reach a healthcare point from the parking, we used dijkstra algorithm. It is powered by pgRouting. We tunned [pgr_dijkstra](https://docs.pgrouting.org/2.0/en/src/dijkstra/doc/index.html) method with setting bool directed to false, making algorithm undirected, because we suppose patient walking to ambulance after parking the car. Imaged shortest walking, not driving, path could be achieved this way.

# Useful links

https://www.postgresonline.com/journal/archives/267-Creating-GeoJSON-Feature-Collections-with-JSON-and-PostGIS-functions.html

https://gis.stackexchange.com/questions/223675/how-to-display-proper-route-for-osm-data-using-pgrouting

https://blog.daftcode.pl/find-your-way-with-the-power-of-postgis-pgrouting-66d620ef201b

http://osm2po.de/

https://anitagraser.com/2011/12/15/an-osm2po-quickstart/
