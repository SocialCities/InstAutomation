from instagram.client import InstagramAPI
import urlparse
import time

def get_cursore(object_to_check):
	return prendi_valore_indice('cursor', object_to_check)	

def get_max_id(object_to_check):
	return prendi_valore_indice('max_id', object_to_check)	

def prendi_valore_indice(stringa, object_to_check):
	blocco_pagination = object_to_check[1]
	
	if blocco_pagination is None:
		return None
	else:
		o = urlparse.urlparse(blocco_pagination)
		query = o.query
		query_parsed = urlparse.parse_qs(query)
		cursore = query_parsed[stringa][0]
		return cursore	

def check_limite(api):
	x_ratelimit_remaining = api.x_ratelimit_remaining
	if (x_ratelimit_remaining < 10) and (x_ratelimit_remaining is not None):
		time.sleep(3600)		 	
