from django.contrib import messages, auth
from django.shortcuts import redirect


def auth_character(allowed_status: list):
    """Check User's Character authorization to use a view.
    Log out user if there's a NoReverseMatch exception due to problems with
    session['character_id'] with URL of 'characters:character' view.
    If Character is authorized to use the view, provide request with
    'current_character' attribute that can be accessed in vies and templates.
    """
    from characters.models import Character

    def wrapper(view_func):

        def wrapped(request, *args, **kwargs):
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)

            else:
                try:
                    current_character = Character.objects.get(id=request.session.get('character_id'))
                except Character.DoesNotExist:
                    current_character = None

                if not current_character:
                    auth.logout(request)
                    messages.warning(request, 'Wystąpił problem z uwierzytelnieniem sesji użytkownika. Zaloguj się ponownie!')
                    return redirect('users:logout')

                request.current_character = current_character

                if 'all' in allowed_status or current_character.status in allowed_status:
                    return view_func(request, *args, **kwargs)
                return redirect('users:dupa')

        return wrapped

    return wrapper
