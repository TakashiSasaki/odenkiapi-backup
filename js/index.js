function OnChangedEventHandler() {
	query_string = "";
	field1 = $("#field1").get()[0].value;
	string1 = $("#string1").get()[0].value;
	field2 = $("#field2").get()[0].value;
	string2 = $("#string2").get()[0].value;
	field3 = $("#field3").get()[0].value;
	string3 = $("#string3").get()[0].value;
	field4 = $("#field4").get()[0].value;
	string4 = $("#string4").get()[0].value;
	field5 = $("#field5").get()[0].value;
	string5 = $("#string5").get()[0].value;
	if (field1 != "" && string1 != "") {
		query_string = field1 + "=" + string1;
	}
	if (field2 != "" && string2 != "") {
		query_string += '&' + field2 + "=" + string2;
	}
	if (field3 != "" && string3 != "") {
		query_string += '&' + field3 + "=" + string3;
	}
	if (field4 != "" && string4 != "") {
		query_string += '&' + field4 + "=" + string4;
	}
	if (field5 != "" && string5 != "") {
		query_string += '&' + field5 + "=" + string5;
	}
	$("#query_string").get()[0].value = query_string;
}

function Post() {
	var xhr = false;
	if (window.XMLHttpRequest) {
		xhr = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		try {
			xhr = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) {
			xhr = new ActiveXObject("Microsoft.XMLHTTP");
		}
	}
	// if
	// xhr.setRequestHeader("Content-Type",
	// "application/x-www-form-urlencoded");
	xhr.onreadystatechange = function() {
		if (this.readyState == 4) {
			$("#response").get()[0].value = this.responseText;
		} else {
			// $("#response").get()[0].value = this.readyState;
		}// if
	}// function
	// alert($("#query_string").get()[0].value);
	xhr.open("POST", "/post?" + $("#query_string").get()[0].value);
	xhr.send($("#postbody").val());
}// Post

function Get() {
	var xhr = false;
	if (window.XMLHttpRequest) {
		xhr = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		try {
			xhr = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) {
			xhr = new ActiveXObject("Microsoft.XMLHTTP");
		}
	}
	// if
	// xhr.setRequestHeader("Content-Type",
	// "application/x-www-form-urlencoded");
	xhr.onreadystatechange = function() {
		if (this.readyState == 4) {
			$("#response").get()[0].value = this.responseText;
		} else {
			// $("#response").get()[0].value = this.readyState;
		}// if
	}// function
	// alert($("#query_string").get()[0].value);
	xhr.open("GET", "/post?" + $("#query_string").get()[0].value);
	xhr.send($("#postbody").get()[0].value);
}// Post
