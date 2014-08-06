from django.conf.urls import patterns, include, url
from django.contrib import admin

from instagram_like.models import ListaTag, BlacklistFoto, LikeTaskStatus
from instagram_follow.models import BlacklistUtenti, UtentiRivali, WhitelistUtenti, FollowTaskStatus
from social_auth.models import UserSocialAuth



	
class TagAdmin(admin.ModelAdmin):
	fields=['keyword', 'utente']
	list_display = ('keyword', 'utente')	

class BlacklistFotoAdmin(admin.ModelAdmin):
	fields=['id_foto', 'link_foto', 'utente']
	list_display = ('id_foto', 'link_foto', 'utente')	
	
class LikeTaskStatusAdmin(admin.ModelAdmin):
	fields=['task_id', 'completato', 'utente']
	list_display = ('task_id', 'completato', 'utente')	
	
class BlacklistUtentiAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente', 'unfollowato']
	list_display = ('username', 'id_utente', 'utente', 'unfollowato')
	
class UtentiRivaliAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente']
	list_display = ('username', 'id_utente', 'utente')	
	
class WhitelistUtentiAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente']
	list_display = ('username', 'id_utente', 'utente')	
	
class FollowTaskStatusAdmin(admin.ModelAdmin):
	fields=['task_id', 'completato', 'utente']
	list_display = ('task_id', 'completato', 'utente')		

admin.site.register(ListaTag, TagAdmin)
admin.site.register(BlacklistFoto, BlacklistFotoAdmin)
admin.site.register(LikeTaskStatus, LikeTaskStatusAdmin)
admin.site.register(UserSocialAuth)
admin.site.register(BlacklistUtenti, BlacklistUtentiAdmin)
admin.site.register(UtentiRivali, UtentiRivaliAdmin)
admin.site.register(WhitelistUtenti, WhitelistUtentiAdmin)
admin.site.register(FollowTaskStatus, FollowTaskStatusAdmin)

urlpatterns = patterns('',
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'accesso.views.index'), 
    url(r'^access$', 'accesso.views.gestione_accesso'),
    url(r'^logout$', 'accesso.views.uscita'),
     
    url(r'^tag$', 'instagram_like.views.aggiungi_tag'), 
    url(r'^avvia_like$', 'instagram_like.views.avvia_like'),    
    url(r'^ferma_like$', 'instagram_like.views.ferma_like'),
    
    url(r'^how_i_met_your_follower$', 'instagram_follow.views.prendi_follower'),  
    url(r'^ferma_follow$', 'instagram_follow.views.ferma_follow'),  
    url(r'^pulizia_follower$', 'instagram_follow.views.avvia_pulizia_follower'), 
    url(r'^cerca_competitor$', 'accesso.views.cerca_competitor'),   
    url(r'^aggiungi_competitor$', 'instagram_follow.views.aggiungi_competitor'), 
    url(r'^whitelist_follower$', 'instagram_follow.views.follower_whitelist'),
    
    url(r'^porco$', 'instagram_follow.views.porco_giuda'),
    
    url(r'^localize$', 'geoinstagram.views.localize'),
    url(r'^mappa$', 'geoinstagram.views.mappa'),
    
    url(r'^test_statistiche$', 'statistiche.views.test_statistica'),    
    
    #url(r'^commento$', 'struttura.views.aggiungi_commento'),
    #url(r'^rivale$', 'struttura.views.aggiungi_rivale'),    
    #url(r'^check_all_task$', 'struttura.views.check_all_task'),
    #url(r'^check_task$', 'struttura.views.check_task'),
    #url(r'^debug_tag$', 'debug.views.aggiungi_like_debug'),
    #url(r'^test$', 'struttura.views.testNuovo'),
    #url(r'^limite$', 'struttura.views.cerca_limite'),
    #url(r'^attacca_stacca$', 'struttura.views.attacca_stacca'),
    #url(r'^stacca$', 'struttura.views.stacca'),
)

# Instagram only allows one callback url so you'll have to change your urls.py to accomodate
# both /complete and /associate routes, for example by having a single /associate url which takes a ?complete=true 
# parameter for the cases when you want to complete rather than associate.
