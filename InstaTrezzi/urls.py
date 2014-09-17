from django.conf.urls import patterns, include, url
from django.contrib import admin

from instagram_like.models import ListaTag, BlacklistFoto, LikeTaskStatus
from instagram_follow.models import BlacklistUtenti, UtentiRivali, WhitelistUtenti, FollowTaskStatus
from accesso.models import trackStats
from social_auth.models import UserSocialAuth

from accesso.views import task_esistente, beta_home
	
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
	
class InitialStatsAdmin(admin.ModelAdmin):
	fields = ['utente', 'follower_iniziali']
	list_display = ('utente', 'follower_iniziali')	

admin.site.register(ListaTag, TagAdmin)
admin.site.register(BlacklistFoto, BlacklistFotoAdmin)
admin.site.register(LikeTaskStatus, LikeTaskStatusAdmin)
admin.site.register(UserSocialAuth)
admin.site.register(BlacklistUtenti, BlacklistUtentiAdmin)
admin.site.register(UtentiRivali, UtentiRivaliAdmin)
admin.site.register(WhitelistUtenti, WhitelistUtentiAdmin)
admin.site.register(FollowTaskStatus, FollowTaskStatusAdmin)
admin.site.register(trackStats, InitialStatsAdmin)

urlpatterns = patterns('',
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'accesso.views.index'),     
    url(r'^logout$', 'accesso.views.uscita'),
    url(r'^access$', 'accesso.views.access'),
    url(r'^home$', 'accesso.views.home_page'),
    url(r'^task_esistente$', task_esistente.as_view()),
    url(r'^follow$', 'accesso.views.follow_home'),  
    url(r'^like$', 'accesso.views.like_home'),  
    url(r'^beta/$', beta_home.as_view()),      
      
    url(r'^cerca_competitor$', 'instagram_follow.views.cerca_competitor'),       
    url(r'^aggiungi_competitor$', 'instagram_follow.views.aggiungi_competitor'), 
    url(r'^how_i_met_your_follower$', 'instagram_follow.views.prendi_follower'),
    url(r'^get_info$', 'instagram_follow.views.get_info'),      
     
    url(r'^aggiungi_tag$', 'instagram_like.views.aggiungi_tag'), 
    url(r'^avvia_like$', 'instagram_like.views.avvia_like'),    
    url(r'^ferma_like$', 'instagram_like.views.ferma_like'),
    
    url(r'^localize$', 'geoinstagram.views.localize'),
    url(r'^mappa$', 'geoinstagram.views.mappa'),
    
    url(r'^test_statistiche$', 'statistiche.views.test_statistica'),        
   
    url(r'^miei_like$', 'statistiche.views.statistiche_mie_foto'), 
)

# Instagram only allows one callback url so you'll have to change your urls.py to accomodate
# both /complete and /associate routes, for example by having a single /associate url which takes a ?complete=true 
# parameter for the cases when you want to complete rather than associate.
