odenki = {
	"getVersion" : function getVersion() {
		var data = '{"id": 0, "method":"get"}';
		$.ajax({
			datatype : "json",
			url : "/Version",
			type : "POST",
			data : data,
			success : function(result_json) {
				$("#versionString").text(result_json.versionString);
				$("#timeStampString").text(result_json.timeStampString);
			},
			error : function(result_json, text_status, error_thrown) {
				$("#versionString").text("?");
				$("#timeStampString").text("?");
			}
		});
	}// getVersion
}// odenki
