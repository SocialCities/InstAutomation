from django.conf.urls import patterns, include, url
from django.contrib import admin

from instagram_like.models import ListaTag, BlacklistFoto
from instagram_follow.models import BlacklistUtenti, UtentiRivali, WhitelistUtenti
from accesso.models import trackStats, TaskStatus
from social_auth.models import UserSocialAuth

from accesso.views import beta_home
	
class TagAdmin(admin.ModelAdmin):
	fields=['keyword', 'utente']
	list_display = ('keyword', 'utente')	

class BlacklistFotoAdmin(admin.ModelAdmin):
	fields=['id_foto', 'link_foto', 'utente']
	list_display = ('id_foto', 'link_foto', 'utente')	
	
class BlacklistUtentiAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente', 'unfollowato']
	list_display = ('username', 'id_utente', 'utente', 'unfollowato')
	
class UtentiRivaliAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente']
	list_display = ('username', 'id_utente', 'utente')	

class WhitelistUtentiAdmin(admin.ModelAdmin):
	field = ['username', 'id_utente', 'utente']
	list_display = ('username', 'id_utente', 'utente')	
	
class TaskStatusAdmin(admin.ModelAdmin):
	fields=['task_id', 'completato', 'utente']
	list_display = ('task_id', 'completato', 'utente')	
		
class InitialStatsAdmin(admin.ModelAdmin):
	fields = ['utente', 'follower_iniziali']
	list_display = ('utente', 'follower_iniziali')	

admin.site.register(ListaTag, TagAdmin)
admin.site.register(BlacklistFoto, BlacklistFotoAdmin)
admin.site.register(UserSocialAuth)
admin.site.register(BlacklistUtenti, BlacklistUtentiAdmin)
admin.site.register(UtentiRivali, UtentiRivaliAdmin)
admin.site.register(WhitelistUtenti, WhitelistUtentiAdmin)
admin.site.register(TaskStatus, TaskStatusAdmin)
admin.site.register(trackStats, InitialStatsAdmin)

urlpatterns = patterns('',
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'accesso.views.index'),     
    url(r'^logout$', 'accesso.views.uscita'),
    url(r'^access$', 'accesso.views.access'),
    url(r'^home$', 'accesso.views.home_page'),    
    url(r'^cerca_competitor$', 'accesso.views.cerca_competitor'),  
    url(r'^stop$', 'accesso.views.ferma_task'),   
    url(r'^start$', 'accesso.views.avvia_task'), 
    
    url(r'^beta/$', beta_home.as_view()),      
          
    url(r'^aggiungi_competitor$', 'instagram_follow.views.aggiungi_competitor'),      
    url(r'^aggiungi_tag$', 'instagram_like.views.aggiungi_tag'), 

    #Cose a caso esterne
    url(r'^localize$', 'geoinstagram.views.localize'),
    url(r'^mappa$', 'geoinstagram.views.mappa'),    
    url(r'^report$', 'statistiche.views.report_statistico'), 

    #url(r'^avvia_like$', 'instagram_like.views.avvia_like'),    
    #url(r'^how_i_met_your_follower$', 'instagram_follow.views.prendi_follower'), 
)

# Instagram only allows one callback url so you'll have to change your urls.py to accomodate
# both /complete and /associate routes, for example by having a single /associate url which takes a ?complete=true 
# parameter for the cases when you want to complete rather than associate.
