from django.http import HttpResponseRedirect

class BetaMiddleware(object):
    """
    Require beta code session key in order to view any page.
    """
    def process_request(self, request):
        if request.path != '/beta/' and not request.session.get('in_beta'):
            return HttpResponseRedirect('%s?next=%s' % ('/beta/', request.path))
