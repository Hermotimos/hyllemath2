from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.vary import vary_on_cookie

from characters.models import CharacterVersion
from myproject.utils_views import auth_character





# temp for updating Character.mainversionname
if True:
    print('\nUPDATED Character.mainversionname !!!\n')
    for characterversion in CharacterVersion.objects.all():
        characterversion.save()




# @vary_on_cookie
@login_required
@auth_character(['all'])
def characters_main_view(request):
    current_character = getattr(request, 'current_character', None)

    characterversions = CharacterVersion.objects.all()
    if current_character:
        characterversions = CharacterVersion.objects.filter(knowledges__character=current_character)
    print(characterversions)
    context = {
        'page_title': 'Prosoponomikon',
        'characterversions': characterversions,
    }
    return render(request, 'characters/main.html', context)





# @vary_on_cookie
@login_required
@auth_character(['all'])
def generic_relations_exemplary_view(request):
    """A temporary view for experimentation with generic relations."""
    current_character = getattr(request, 'current_character', None)

    # --------------------------------------
    # USE AS A PLAYER TO POPULATE knowledges
    # --------------------------------------

    # characterversions = CharacterVersion.objects.all()
    knowledges = []
    if current_character:
        knowledges = current_character.knowledges.prefetch_related(
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

