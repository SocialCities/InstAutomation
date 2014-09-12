url_stima = "/get_info";

function stima_tempo(id) {
	$.get( url_stima, { id: id }, success );
}

function success(data) {
	data = data/60;
		
	alert(data+" ore");
}
