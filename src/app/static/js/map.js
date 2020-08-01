mapboxgl.accessToken = 'pk.eyJ1IjoibHVka28iLCJhIjoiY2syMXM4Ymp5MWNlaTNtbXZhYmlwdm5xdyJ9.3OKC-gAnIHVnu9R8ob55yQ';
var map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/mapbox/streets-v9',
	center: [4.35, 50.84],
	zoom: 11
});

var LAYER_PARKING_ID = 'parking_id';
var LAYER_PATH_ID = 'path_id';

var source_coor = null;
var target_coor = null;

function add_healthpoint(point) {
	var el = document.createElement('div');
	el.className = 'healthpoint';
	var amenity = point.properties.amenity;
	if (amenity == 'dentist') {
		el.className += ' dentist';
		el.textContent = 'D';
	} else if (amenity == 'hospital') {
		el.className += ' hospital';
		el.textContent = 'H';
	} else {
		el.className += ' doctors';
		el.textContent = '+';
	}

	el.addEventListener('click', function() {
		var name = point.properties.name;
		if (name == null) name = '--Unknown provider--';
		$('#healthpoint_name').text(name);

		target_coor = point.geometry.coordinates;
		console.log(target_coor);

		find_parking(point.gid);
	});

	new mapboxgl.Marker(el)
	.setLngLat(point.geometry.coordinates)
	.addTo(map);
};

function add_parking(polygon) {
	var el = document.createElement('div');
	el.className = 'parking';
	el.textContent = 'P';

	el.addEventListener('click', function() {
		source_coor = polygon.geometry.coordinates[0][0];
		console.log(source_coor);

		var area = polygon.properties.way_area;
		$('#parking_area').text('area ' + area + ' m2');
		var distance = parseFloat(polygon.properties.meters).toFixed(1);
		$('#parking_airdistance').text('air distance ' + distance + ' m away');

		shortest_path();
	});

	new mapboxgl.Marker(el)
	.setLngLat(polygon.geometry.coordinates[0][0])
	.addTo(map);
};

function draw_parking(polygon_collection) {
	map.addLayer({
		"id": LAYER_PARKING_ID,
		"type": "fill",
		"source": {
			"type": "geojson",
			"data": polygon_collection
		},
		'layout': {},
		'paint': {
			'fill-color': 'magenta',
			'fill-opacity': .3
		}
	});
};

function draw_path(linestring_collection) {
	if (linestring_collection.features == null) {
		console.log('not found');
		return;
	}

	map.addLayer({
		"id": LAYER_PATH_ID,
		"type": "line",
		"source": {
			"type": "geojson",
			"data": linestring_collection
		},
		"layout": {
			"line-join": "round",
			"line-cap": "round"
		},
		"paint": {
			"line-color": "red",
			'line-opacity': .3,
			"line-width": 3
		}
	});
};

function remove_layer(id) {
	if (id == LAYER_PARKING_ID) {
		$('.parking').remove();
	}
	if (typeof map.getLayer(id) !== 'undefined') {
		// remove both layer & source necessary
      map.removeLayer(id).removeSource(id);
	}
};

function calc_distance(linestring_array) {
	var dist = 0.
	linestring_array.forEach(function(linestring) {
		dist += linestring.properties.km;
	});
	dist *= 1000; // km to m conversion
	$('#parking_distance').text('driving distance ' + dist.toFixed(1) + ' m');
};

// API calls

function list_all() {
	$.getJSON($SCRIPT_ROOT + '/api/_list_all', function(data) {
		console.log(data);
		data.features.forEach(function(point) {
			add_healthpoint(point);
		});
	});
};

function find_parking(gid) {
	new Promise(function(resolve, reject) {
		remove_layer(LAYER_PARKING_ID);
		remove_layer(LAYER_PATH_ID);
		resolve();
	}).then(function() {
		$.getJSON($SCRIPT_ROOT + '/api/_find_parking/' + gid, function(data) {
			console.log(data);
			data.features.forEach(function(polygon) {
				add_parking(polygon);
			});
			draw_parking(data);
		});
	});
};

function shortest_path() {
	new Promise(function(resolve, reject) {
		remove_layer(LAYER_PATH_ID);
		resolve();
	}).then(function() {
		args = {
			'source_lon': parseFloat(source_coor[0]),
			'source_lat': parseFloat(source_coor[1]),
			'target_lon': parseFloat(target_coor[0]),
			'target_lat': parseFloat(target_coor[1])
		};
		$.getJSON($SCRIPT_ROOT + '/api/_shortest_path', args, function(data) {
			console.log(data);
			draw_path(data);
			calc_distance(data.features);
		});
	});
};

$(function() { // $(document).ready(function() {
	list_all();
});
