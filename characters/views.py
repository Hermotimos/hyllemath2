from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator

from characters.models import CharacterVersion
from myproject.utils_views import auth_character


# -----------------------------------------------------------------------------


@method_decorator(login_required, name='dispatch')
@method_decorator(auth_character(['all']), name='dispatch')
class CharacterVersionListView(ListView):
    model = CharacterVersion

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_player:
            user_character = getattr(self.request, 'user_character', None)
            return qs.filter(knowledges__character=user_character)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characterversions'] = self.get_queryset()
        context['page_title'] = 'Prosoponomikon'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(auth_character(['all']), name='dispatch')
class CharacterVersionDetailView(DetailView):
    model = CharacterVersion
    pk_url_kwarg = 'characterversion_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_object().fullname
        return context



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

