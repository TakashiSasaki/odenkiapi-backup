odenki = {
	"getVersion" : function getVersion() {
		$.ajax({
			datatype : "json",
			url : "/api/Version",
			type : "GET",
			data : null,
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
	,
	"getFooter" : function getFooter() {
		$.ajax({
			datatype : "html",
			url : "/html/footer.html",
			type : "GET",
			data : null,
			success : function(footer_html) {
				$("footer").html(footer_html);
			}
		})
	}// getFooter
	,
	"getHeader" : function getHeaderer(){
		$.ajax({
			datatype: "html",
			url: "/html/header.html",
			type : "GET",
			data: null,
			success : function(header_html){
				$("header").html(header_html);
			}
		})
	}
}// odenki
