from typing import Callable

from django.contrib import auth, messages
from django.http import HttpResponse
from django.shortcuts import redirect


def auth_character(allowed_status: list) -> Callable:
    """Check User's Character authorization to use a view.
    Log out user if there's a NoReverseMatch exception due to problems with
    session['character_id'] with URL of 'characters:character' view.
    If Character is authorized to use the view, provide request with
    'user_character' attribute that can be accessed in vies and templates.
    """
    from characters.models import Character

    def wrapper(view_func: Callable) -> Callable:

        def wrapped(request, *args, **kwargs) -> HttpResponse:

            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            else:
                try:
                    user_character: Character = Character.objects.get(id=request.session.get('character_id'))
                except Character.DoesNotExist:
                    # user_character = None
                # if not user_character:
                    auth.logout(request)
                    messages.warning(request, 'Wystąpił problem z uwierzytelnieniem. Zaloguj się ponownie!')
                    return redirect('users:logout')

                request.user_character = user_character
                request.user_maincharacterversion = user_character.main_characterversion()

                if 'all' in allowed_status or user_character.status in allowed_status:
                    return view_func(request, *args, **kwargs)
                return redirect('users:dupa')

        return wrapped

    return wrapper
