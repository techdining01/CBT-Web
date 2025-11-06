import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

class AutoLogoutMiddleware:
    """Automatically logs out users after 10 minutes of inactivity."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed = (now - datetime.datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed > 300: 
                from django.contrib.auth import logout
                logout(request)
                messages.info(request, "You have been logged out due to inactivity.")
                return redirect('login') 

        # Update last activity timestamp
        request.session['last_activity'] = now.isoformat()
        return self.get_response(request)
