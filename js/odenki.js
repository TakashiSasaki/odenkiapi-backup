odenki = {}

odenki.setVersion = function() {
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

odenki.setFooter = function() {
	$.ajax({
		datatype : "html",
		url : "/html/footer.html",
		type : "GET",
		cache : true,
		data : null,
		success : function(footer_html) {
			$("footer").html(footer_html);
		}
	})
}// getFooter

odenki.setHeader = function() {
	$.ajax({
		datatype : "html",
		url : "/html/header.html",
		type : "GET",
		cache : true,
		data : null,
		success : function(header_html) {
			$("header").html(header_html);
		}
	})
}// getHeader

odenki.echo = function(method, param_string, body_string, tr_id) {
	var url;
	if (param_string) {
		url = "/api/Echo?" + param_string;
	} else {
		url = "/api/Echo";
	}
	$.ajax({
		datatype : "json",
		cache : true,
		url : url,
		type : method,
		data : body_string,
		success : function(data, dataType) {
			$("#" + tr_id + " td.param_string").text(param_string);
			$("#" + tr_id + " td.body_string").text(body_string);
			$("#" + tr_id + " td.response").text($.toJSON(data));
		},// success
		error : function(XMLHttpRequest, textStatus, errorThrow) {
			$("#" + tr_id + " td.param_string").text(param_string);
			$("#" + tr_id + " td.body_string").text(body_string);
			$("#" + tr_id + " td.response").text($.toJSON(textStatus));
		}// error
	});// ajax
}// echo

odenki.replaceEventSoruceElement = function(arguments, text) {
	script_tag = arguments[0].target;
	$(script_tag).replaceWith(text);
}// replaceEventSourceElement

odenki.replaceEventSourceParentElement = function(argument, html) {
	script_tag = arguments[0].target;
	parent_tag = $(script_tag).parent();
	parent_tag.replaceWith(html);
}// replaceEventSourceParemtElement
