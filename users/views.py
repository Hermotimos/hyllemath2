import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.db.models.functions import Length
from django.shortcuts import redirect, render

# from prosoponomikon.forms import CharacterForm
# from prosoponomikon.models import Character, FirstName
from users.forms import UserRegistrationForm, UserUpdateForm, UserImageUpdateForm
# from users.models import Profile


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    # settings.py
    # LOGIN_REDIRECT_URL = 'users:home'
    # LOGIN_URL = 'users:login'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        # provide 'character_id' to session
        user_current_character = user.characters.order_by('-_createdat').first()
        self.request.session['character_id'] = user_current_character.id

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Logowanie'
        return context

    # def get(self, request, *args, **kwargs):
    #     """Override method to handle situation when 'go back' browser button is
    #     used from the home page directly after loging in.
    #     Going back from home page would result in NoReverseMatch exception
    #     as request has no 'current_profile' attribute and some navbar & sidebar
    #     links demand it to resolve URLs.
    #     """
    #     hosts = settings.ALLOWED_HOSTS
    #     if any(host in request.META.get('HTTP_REFERER', '') for host in hosts):
    #         logout(request)
    #         redirect('users:login')
    #     return self.render_to_response(self.get_context_data())


class CustomLogoutView(LogoutView):
    # settings.py
    # LOGOUT_REDIRECT_URL = 'users:login'
    pass


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        # profile = Profile.objects.create(user=user)
        # Character.objects.create(
        #     profile=profile,
        #     first_name=FirstName.objects.create(
        #         form=user.username.replace('_', ' '))
        # )
        messages.info(
            request, f'Utworzono konto dla {user.username}! Zaloguj się!')
        return redirect('users:login')

    context = {
        'page_title': 'Utwórz profil',
        'form': form
    }
    return render(request, 'users/register.html', context)


@login_required
# @auth_profile(['all'])
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.info(request, 'Hasło zostało zaktualizowane!')
            return redirect('users:edit-profile')
        else:
            messages.warning(request, 'Popraw poniższy błąd!')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'page_title': 'Zmiana hasła',
        'form': form
    }
    return render(request, 'users/change_password.html', context)


@login_required
# @auth_profile(['all'])
def edit_user_view(request):
    # current_profile = request.current_profile
    # user_profiles = current_profile.user.profiles.all()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        user_image_form = UserImageUpdateForm(request.POST, request.FILES)

        if user_form.is_valid() and user_image_form.is_valid():
            user_form.save()
            user_image = user_image_form.cleaned_data.get('user_image')
            # if user_image:
            #     for profile in user_profiles:
            #         profile.user_image = user_image
            #         profile.save()

            messages.info(request, 'Zaktualizowano Użytkownika!')
            return redirect('users:edit-user')
    else:
        user_form = UserUpdateForm(instance=request.user)
        user_image_form = UserImageUpdateForm()

    context = {
        'page_title': 'Konto Użytkownika',
        'user_form': user_form,
        'user_image_form': user_image_form,
    }
    return render(request, 'users/edit_user.html', context)


# @login_required
# @auth_profile(['all'])
# def edit_profile_view(request):
#     current_profile = request.current_profile

#     if request.method == 'POST':
#         profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=current_profile)
#         character_form = CharacterForm(request.POST, instance=current_profile.character)
#         if profile_form.is_valid() and character_form.is_valid():
#             profile_form.save()
#             character_form.save()
#             messages.info(request, 'Zaktualizowano Postać!')
#             return redirect('users:edit-profile')
#     else:
#         profile_form = ProfileUpdateForm(instance=current_profile)
#         character_form = CharacterForm(instance=current_profile.character)

#     context = {
#         'page_title': 'Edycja Postaci',
#         'profile_form': profile_form,
#         'character_form': character_form,
#     }
#     return render(request, 'users/edit_profile.html', context)


# @login_required
# @auth_profile(['all'])
# def switch_profile(request, profile_id):
#     request.session['profile_id'] = profile_id
#     chosen_profile = Profile.objects.get(id=profile_id)

#     msg = f"Zmieniono Postać na {chosen_profile.character.fullname}!"
#     messages.info(request, msg)

#     response = redirect(request.META.get('HTTP_REFERER'))
#     if '/dupa/' in response['Location']:
#         msg = """
#             Przekierowano do strony startowej!
#             (Wybrana Postać nie ma dostępu do poprzedniej treści)"""
#         messages.warning(request, msg)
#         return redirect('users:home')

#     return response


# # =============================================================================


# def get_profile(user):
#     """Get User's Profile by the priority of 'status' and probable recent use."""
#     profiles = user.profiles.order_by(
#         'status', '-is_alive', '-is_active', 'character__fullname')
#     return profiles.first()


# def game_event_with_caption(game_events_qs):
#     """Get the beginning (first n words as per words_limit) of a random
#     paragraph from a random GameEvent.description_long from queryset.
#     The paragraph has to have a minimum number of words as per words_min.
#     """
#     if len(game_events_qs) == 0:
#         return None

#     words_min = 40
#     words_limit = 70
#     game_event = sample_from_qs(qs=game_events_qs, max_size=1)[0]

#     paragraphs = game_event.description_long.split('\n')
#     paragraphs = [p for p in paragraphs if len(p.split(' ')) >= words_min]
#     if not paragraphs:
#         return game_event_with_caption(game_events_qs)

#     paragraph = random.choice(paragraphs)
#     caption = paragraph.strip().split(' ')[:words_limit]
#     caption = " ".join(caption).strip().rstrip(";,:.")
#     caption = caption if caption[-1] in ["!", "?", "..."] else caption + "..."
#     game_event.caption = caption

#     return game_event


@login_required
# @auth_profile(['all'])
def home_view(request):
    # current_profile = request.current_profile

    # from imaginarion.models import PictureImage
    # first = PictureImage.objects.first()
    # print(first.image.url)  # /media/post_pics/knowledge_Struktura%20organizacyjna%20Szarej%20Gwardii.jpg
    # print(first.image.path) # C:\Users\Lukasz\PycharmProjects\rpg_hub\media\post_pics\knowledge_Struktura organizacyjna Szarej Gwardii.jpg

    # rand_acquaintanceships = sample_from_qs(
    #     qs=current_profile.character.acquaintanceships().filter(is_direct=True).distinct(),
    #     max_size=4)
    # rand_locations = sample_from_qs(
    #     qs=current_profile.locations_known_annotated().filter(only_indirectly=0).distinct(),
    #     max_size=2)
    # rand_gameevent = game_event_with_caption(
    #     game_events_qs=current_profile.gameevents_known_annotated.filter(
    #         only_indirectly=0
    #     ).annotate(
    #         text_len=Length('description_long')
    #     ).filter(
    #         text_len__gt=400
    #     ).distinct()
    # )

    context = {
        'page_title': 'Hyllemath',
        # 'rand_acquaintanceships': rand_acquaintanceships,
        # 'rand_locations': rand_locations,
        # 'rand_gameevent': rand_gameevent,
    }
    return render(request, 'users/home.html', context)


# @login_required
# @auth_profile(['all'])
# def dupa_view(request):
#     context = {
#         'page_title': 'Dupa',
#     }
#     return render(request, 'users/dupa.html', context)
