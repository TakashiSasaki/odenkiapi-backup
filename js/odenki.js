odenki = {}

odenki.fillVersion = function(parent) {
	$.ajax({
		datatype : "json",
		url : "/api/Version",
		type : "GET",
		data : null,
		success : function(result_json) {
			odenki.fillText(parent, result_json);
		},
		error : function(xml_http_request, text_status, error_thrown) {
			odenki.hideElement(parent);
		}
	});
}// fillVersion

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

odenki.getEventSourceElement = function(arguments) {
	return arguments[0].target;
}

odenki.replaceEventSoruceElement = function(arguments, text) {
	script_tag = odenki.getEventSourceElement(arguments);
	$(script_tag).replaceWith(text);
}// replaceEventSourceElement

odenki.replaceEventSourceParentElement = function(arguments, html) {
	script_tag = odenki.getEventSourceElement(arguments);
	parent_tag = $(script_tag).parent();
	parent_tag.replaceWith(html);
}// replaceEventSourceParemtElement

odenki.fillText = function(parent, dictionary) {
	if (typeof parent === "string") {
		for (k in dictionary) {
			$("#" + parent + " ." + k).text(dictionary[k]);
		}
	} else {
		for (k in dictionary) {
			e = parent.find("." + k);
			e.text(dictionary[k]);
		}
	}
}// fillText

odenki.hideElement = function(element) {
	if (typeof element === "string") {
		$("#" + element).css("display", "none");
	} else {
		$(element).css("display", "none");
	}
}// hideElement

