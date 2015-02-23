from django.http import HttpResponseRedirect

class BetaMiddleware(object):
    """
    Require beta code session key in order to view any page.
    """
    def process_request(self, request):
        if request.path == '/email_chimp' or request.path == '/admin/':
            pass
        elif request.path != '/beta/' and not request.session.get('in_beta'):
            return HttpResponseRedirect('%s?next=%s' % ('/beta/', request.path))


from social_auth.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render
from social_auth.exceptions import AuthCanceled, AuthFailed

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
    	tipo_ecc = type(exception)
        if (tipo_ecc == AuthCanceled) or (tipo_ecc == AuthFailed):
        	return render(request, "errore_auth.html")
        else:
            pass