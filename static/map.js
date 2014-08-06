$(document).ready(function() {	
	mappa();
});

function mappa() {
	map = L.map('map').setView([centroLat, centroLng], 15);
			
	var cloudmadeUrl = 'http://{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
		subDomains = ['otile1','otile2','otile3','otile4'],
		cloudmadeAttrib = 'Data, imagery and map information provided by <a href="http://open.mapquest.co.uk" target="_blank">MapQuest</a>, <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> and contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/" target="_blank">CC-BY-SA</a>';
	 
	var cloudmade = new L.TileLayer(cloudmadeUrl, {maxZoom: 18, attribution: cloudmadeAttrib, subdomains: subDomains});

	cloudmade.addTo(map);		

	//var marker = L.marker([centroLat, centroLng]).addTo(map);
	//marker.bindPopup("<b>Ciao!</b>").openPopup();
	
	punti_di_interesse.forEach(function(point) {
		marker = L.marker([point.latitudine, point.longitudine]).addTo(map);
		marker.bindPopup("<img height='100' src='"+ point.thumbnail +"'></img> <a href="+ point.link +" target = '_blank'>Link</a> <a href='http://instagram.com/"+ point.username +"' target = '_blank'>Profilo</a>")
	});
}
