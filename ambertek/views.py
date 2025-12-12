from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils import translation

def set_language(request, language_code):
    """
    View to set user's language preference
    """
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        translation.activate(language_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
    
    # Redirect back to the previous page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return redirect('home')