url_stima = "/get_info";

function stima_tempo(id) {
	$.get( url_stima, { id: id }, success );
}

function success(data) {		
	alert(data);
}
