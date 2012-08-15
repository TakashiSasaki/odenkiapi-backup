//https://spreadsheets.google.com/feeds/cells/0AuFt9cSl5maddEtiOG9rNUstdW80dmlyakRFYnlPeXc/od6/public/values?alt=json&callback=od6

function JsonToArray(json) {
    var height = json.feed.gs$rowCount["$t"];
    var width = json.feed.gs$colCount["$t"];
    var array = new Array(height);
    for (var r = 0; r < height; ++r) {
        array[r] = new Array(width);
    }
    var entries = json.feed.entry;
    for (var i = 0; i < entries.length; ++i) {
        var entry = entries[i]["gs$cell"];
        var row = entry.row;
        var col = entry.col;
        var value = entry["$t"];
        array[row - 1][col - 1] = value;
    }// for
    return array;
}// JsonToArray

function Sheet(sheet_id) {
    this.url = "https://spreadsheets.google.com/feeds/cells/0AuFt9cSl5maddEtiOG9rNUstdW80dmlyakRFYnlPeXc/" + sheet_id + "/public/values?callback=?";

    this.callback = function(json) {
        //alert(json);
        //alert(json);
        //if(json == undefined) return;
        this.array = JsonToArray(json);
    }

    this.fetch = function(callback) {
        this.array = [2];
        //this.callback.bind(this)();
        //this.callback.bind(this)();
        //alert("bind ok");
        $.getJSON(this.url, {
            alt : "json"
        }, callback);
    }// fetch

    this.fetch();

}// Sheet

var ob6 = new Sheet("od6");
ob6.fetch(function(json) {
    var array = JsonToArray(json);
    var totalElectricityGenerated = new google.visualization.DataTable();
    totalElectricityGenerated.addColumn("datetime", "発電日");
    totalElectricityGenerated.addColumn("number", "発電量(kWh)");
    for (var i = 0; i < array.length; ++i) {
        var row = array[i];
        //alert(row[3]);
        totalElectricityGenerated.addRow([new Date(row[0], row[1], row[2]), Number(row[3])]);
        //totalElectricityGenerated.addRow([new Date(1990,10,10), 100] );
    }//for
    var lineChart = new google.visualization.LineChart(document.getElementById('totalElectricityGenerated'));
    lineChart.draw(totalElectricityGenerated, {
        title : 'みんなの発電量',
        height : 300,
        width : $(window).width() * 0.95
    });
});

