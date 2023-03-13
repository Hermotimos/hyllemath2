from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView
from django.utils.decorators import method_decorator

from characters.models import CharacterVersion
from myproject.utils_views import auth_character


# -----------------------------------------------------------------------------

# temp for updating Character.mainversionname
# if True:
#     print('\nUPDATED Character.mainversionname !!!\n')
#     for characterversion in CharacterVersion.objects.all():
#         characterversion.save()

# -----------------------------------------------------------------------------



@method_decorator(login_required, name='dispatch')
@method_decorator(auth_character(['all']), name='dispatch')
class CharacterVersionListView(ListView):
    model = CharacterVersion
    template_name = 'characterversion_main.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if user_character := getattr(self.request, 'user_character', None):
            characterversions = CharacterVersion.objects.filter(
                knowledges__character=user_character)
        else:
            characterversions = CharacterVersion.objects.all()

        context['characterversions'] = characterversions
        context['page_title'] = 'Prosoponomikon'
        return context



# @vary_on_cookie
@login_required
@auth_character(['all'])
def characters_main_view(request):
    user_character = getattr(request, 'user_character', None)

    characterversions = CharacterVersion.objects.all()
    if user_character:
        characterversions = CharacterVersion.objects.filter(knowledges__character=user_character)
    print(characterversions)
    context = {
        'page_title': 'Prosoponomikon',
        'characterversions': characterversions,
    }
    return render(request, 'characters/characterversion_main.html', context)





# @vary_on_cookie
@login_required
@auth_character(['all'])
def generic_relations_exemplary_view(request):
    """A temporary view for experimentation with generic relations."""
    user_character = getattr(request, 'user_character', None)

    # --------------------------------------
    # USE AS A PLAYER TO POPULATE knowledges
    # --------------------------------------

    # characterversions = CharacterVersion.objects.all()
    knowledges = []
    if user_character:
        knowledges = user_character.knowledges.prefetch_related(
            'content_object__picture',
            'content_object__firstname',
            'content_object__tags',
        )
        # print(type(characterversions.first()))
        # print(type(knowledges.first().content_object))
        # print(type(knowledges.first().content_type))

    context = {
        'page_title': 'Prosoponomikon',
        'knowledges': knowledges,
        # 'characterversions': characterversions,
    }
    return render(request, 'characters/exemplary.html', context)

