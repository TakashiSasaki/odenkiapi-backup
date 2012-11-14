var lib = lib || {}
lib.ui = lib.ui || {}

lib.ui.a = '<li>\
                <a href="/html/main.html"   data-ajax="false"   data-icon="home" >\
                    <div class="ui-bar-a">\
                        みんなのおでんき\
                    </div>\
                </a>\
        </li>';
    
lib.ui.b = '<li >\
                <a href="/html/community.html"   data-ajax="false"   data-icon="star" >\
                    <div class="ui-bar-b">\
                        なかまのおでんき\
                    </div>\
                </a>\
            </li>';
    
lib.ui.c = '<li>\
                <a href="/html/myself.html"   data-ajax="false"   data-icon="info">\
                    <div class="ui-bar-c">\
                        マイおでんき\
                    </div>\
                </a>\
            </li>';
            
lib.ui.d = '<li>\
    <a href="/html/equipments.html"   data-ajax="false"   data-icon="grid" >\
        <div class="ui-bar-d">\
            記録作成\
        </div>\
    </a>\
</li>';

lib.ui.e = '<li>\
    <a href="/html/settings.html"   data-ajax="false"   data-icon="gear" >\
        <div class="ui-bar-e">\
            ユーザー設定\
        </div>\
    </a>\
</li>';

lib.ui.makeHeader = function(){
    $('div[data-role="header"]').remove();
	$('div[data-role="page"]').prepend('\
<div data-role="header" data-position="inline" data-theme="e" >\
<h1>\
<img width="40px" height="40px" src="https://twimg0-a.akamaihd.net/profile_images/1522990803/___________reasonably_small.png"></img>\
みんなでおでんき\
<img width="40px" height="40px" src="https://twimg0-a.akamaihd.net/profile_images/1522990803/___________reasonably_small.png"></img>\
</h1>\
</div>\
        ');
}//header

lib.ui.makeNavbar = function(active){
    $('div[data-role="navbar"]').remove();
    $('div[data-role="page"]').prepend('<div data-role="navbar"><ul>'+lib.ui.a+lib.ui.b+lib.ui.c+lib.ui.d+lib.ui.e+'</ul></div>');
    $(".ui-bar-"+active).closest("a").addClass("ui-btn-active");
}//makeNavbar

lib.ui.makeTab = function(active){
    lib.ui.makeNavbar(active);
    lib.ui.makeHeader();
}

lib.ui.showElement=function(selector){
				$(selector).each(function() {
					$(this).css("display", "block");
					//$(this).css("background", "lightgreen");
					//$(this).css("margin", "1px");
				});
}//showElement

lib.ui.hideElement = function (selector){
				$(selector).each(function() {
					$(this).css("display", "none");
					//$(this).css("background", "lightgreen");
					//$(this).css("margin", "1px");
				});
}//hideElement

lib.ui.collapse = function(selector){
    $(selector).trigger("collapse");
}

lib.ui.expand = function(selector){
    $(selector).trigger("expand");
}

lib.ui.onExpand = function(selector, handler) {
    $(selector).bind("expand", handler);
}

lib.ui.livePageCreate = function(selector, handler){
    $(selector).live('pagecreate', handler);
}

lib.ui.loadVisualization = function(){
    google.load("visualization", "1", {
        packages : ["corechart", 'table']
    });
}

lib.ui.setOnLoadCallback = function(callback){
    google.setOnLoadCallback(callback);
}
