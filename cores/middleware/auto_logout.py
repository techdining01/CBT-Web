import datetime
from django.conf import settings
from django.contrib.auth import logout

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Check last activity time
        last_activity = request.session.get('last_activity')
        now = datetime.datetime.now().timestamp()
        timeout = getattr(settings, 'AUTO_LOGOUT_DELAY', 600)  # 10 mins

        if last_activity and now - last_activity > timeout:
            logout(request)
            request.session.flush()

        # Update session
        request.session['last_activity'] = now
        return self.get_response(request)
