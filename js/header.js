function abcde(){
	alert("abcde");
}
function header(selector){
	$(selector).html('\
<div data-role="header" data-position="inline" data-theme="e" >\
<h1>\
<img width="40px" height="40px" src="https://twimg0-a.akamaihd.net/profile_images/1522990803/___________reasonably_small.png"></img>\
みんなでおでんき\
<img width="40px" height="40px" src="https://twimg0-a.akamaihd.net/profile_images/1522990803/___________reasonably_small.png"></img>\
</h1>\
</div>\
	');
}

var a = '<li>\
			<a href="main.html"   data-ajax="false"   data-icon="home" >\
				<div class="ui-bar-a">\
					みんなのおでんき\
				</div>\
			</a>\
	</li>';

var b = '<li >\
			<a href="community.html"   data-ajax="false"   data-icon="star" >\
				<div class="ui-bar-b">\
					なかまのおでんき\
				</div>\
			</a>\
		</li>';

var c = '<li>\
			<a href="myself.html"   data-ajax="false"   data-icon="info">\
				<div class="ui-bar-c">\
					マイおでんき\
				</div>\
			</a>\
		</li>';
		
var d = '<li>\
			<a href="/auth/index.html"   data-ajax="false"   data-icon="gear" >\
				<div class="ui-bar-d">\
					設定\
				</div>\
			</a>\
		</li>';

function navbar(active){
	$("#navbar").html('<div data-role="navbar"><ul>'+a+b+c+d+'</ul></div>');
	$(".ui-bar-"+active).closest("a").addClass("ui-btn-active");
}
