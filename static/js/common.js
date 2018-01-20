var timer = 0;
var global_url = ""

function stop_timer() {
	clearInterval(timer);
}

function start_timer(url, tab_name) {
	stop_timer();
	global_url = url;
	set_tab_active(tab_name);
	timer = setInterval(get_mysql_data, 3000);
	get_mysql_data();
}

function get_mysql_data() {
	obj = new Object();
	obj.host_ids = [];
	$.post(global_url, JSON.stringify(obj), function (mysql_data) {
		$("#data").html(mysql_data);
	}).error(function () {
		console.log("get mysql data error")
	});
}


function set_tab_active(tab_name) {
    if (tab_name == "") {
        return false;
    }
    $("#myTab").find("a").each(function () {
        if ($(this).attr("id") == tab_name) {
            $(this).addClass("active");
        } else {
            $(this).removeClass("active");
        }
    });
}