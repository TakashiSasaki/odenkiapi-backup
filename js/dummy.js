//https://spreadsheets.google.com/feeds/cells/0AuFt9cSl5maddEtiOG9rNUstdW80dmlyakRFYnlPeXc/od6/public/values?alt=json&callback=od6

function JsonToArray(json) {
	var height = json.feed.gs$rowCount["$t"];
	var width = json.feed.gs$colCount["$t"];
	var array = new Array(height);
	for ( var r = 0; r < height; ++r) {
		array[r] = new Array(width);
	}
	var entries = json.feed.entry;
	for ( var i = 0; i < entries.length; ++i) {
		var entry = entries[i]["gs$cell"];
		var row = entry.row;
		var col = entry.col;
		var value = entry["$t"];
		array[row - 1][col - 1] = value;
	}// for
	return array;
}// JsonToArray

function Sheet(sheet_id) {
	// 2x2 array is given to callback
	this.url = "https://spreadsheets.google.com/feeds/cells/0AuFt9cSl5maddEtiOG9rNUstdW80dmlyakRFYnlPeXc/"
			+ sheet_id + "/public/values?callback=?";

	this.array = null;

	this.fetch = function() {
		// this.callback.bind(this)();
		// this.callback.bind(this)();
		var self = this;
		$.getJSON(this.url, {
			alt : "json"
		}, function(json) {
			self.array = JsonToArray(json);
		});
	}// fetch

	this.getArray = function(callback) {
		// this is a blocking function, polling interval is 100ms
		var self = this;
		if (self.array != null) {
			// alert("in setTimeout, self.array = " + self.array);
			// alert("in setTimeout, self.getArray = " + self.getArray);
			// alert("in setTimeout, callback = " + callback)
			callback(self.array);
		} else {
			setTimeout(function() {
				// alert("in setTimeout, self.array = " + self.array);
				// alert("in setTimeout, self.getArray = " + self.getArray);
				// alert("in setTimeout, callback = " + callback)
				// alert(self.getArray.call);
				self.getArray(callback);
			}, 100);
		}// if
	}// getArray

	this.fetch();

}// Sheet

function drawTotalElectricityChart(div) {
	var od6 = new Sheet("od6");
	od6.getArray(function(array) {
		var totalElectricityGenerated = new google.visualization.DataTable();
		totalElectricityGenerated.addColumn("datetime", "発電日");
		totalElectricityGenerated.addColumn("number", "発電量(kWh)");
		for ( var i = 0; i < array.length; ++i) {
			var row = array[i];
			totalElectricityGenerated.addRow([
					new Date(row[0], row[1], row[2]), Number(row[3]) ]);
			// totalElectricityGenerated.addRow([new Date(1990,10,10), 100] );
		}// for
		var lineChart = new google.visualization.LineChart(div);
		lineChart.draw(totalElectricityGenerated, {
			title : 'みんなの発電量',
			height : 300,
			width : $(window).width() * 0.95
		});
	});
}// drawTotalElectricityChart

function drawmap(div) {
	var od7 = new Sheet("od7");
	od7
			.getArray(function(array) {
				var map = new google.maps.Map(div, {
					center : new google.maps.LatLng(33, 132),
					zoom : 10,
					mapTypeId : 'terrain',
					height : 500,
					width : $(window).width() * 0.95
				});
				var marker_clusterer = new MarkerClusterer(map, null, {
					maxZoom : 19
				});
				marker_clusterer.addMarker(new google.maps.Marker({
					position : new google.maps.LatLng(33, 132),
					title : "松山"
				}));
				for ( var i = 1; i < array.length; ++i) {
					var row = array[i];
					var latlng = new google.maps.LatLng(Number(row[2]),
							Number(row[3]));
					var title = row[0];
					var marker = new google.maps.Marker({
						position : latlng,
						title : title
					});
					marker_clusterer.addMarker(marker);
				}
				marker_clusterer.redraw();

			});
}// drawmap

function drawRanking(div) {
	var sheet = new Sheet("3");
	sheet.getArray(function(array) {
		var data_table = new google.visualization.DataTable();
		data_table.addColumn("number", "順位");
		data_table.addColumn("string", "グループ");
		data_table.addColumn("number", "発電量");
		data_table.addColumn("string", "コメント");
		data_table.addColumn("number", "規模");
		for ( var i = 1; i < array.length; ++i) {
			var row = array[i];
			data_table.addRow([ Number(row[0]), row[1], Number(row[4]), row[5],
					Number(row[3]) ]);
			data_table.setFormattedValue(i-1, 1, '<img src="' + row[6]
					+ '" width="40px" height="40px"></img>' + row[1]);
		}// for
		var table = new google.visualization.Table(div);
		table.draw(data_table, {
			allowHtml : true
		});
	});
}// drawRanking
