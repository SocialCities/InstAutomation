url_stima = "/get_info";

function stima_tempo(id) {
	$.get( url_stima, { id: id }, function(data) {
		success(data,id);
		} );
}

function success(data, id) {
	$("#corpo_modale").html(data);
	
	$("#pulsante_mostrante").attr('onclick', 'appari('+id+')');
	
	$(document).ready(function(){
		$("#myModal").modal('show');
	});
	
}

function appari(id) {
	$('#'+id).css('visibility', 'visible');
}
