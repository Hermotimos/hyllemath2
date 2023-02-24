from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm, ModelMultipleChoiceField, BaseModelForm, TextInput

from characters.models import (
    FirstName, FirstNameGroup, FirstNameTag,
    FamilyName, FamilyNameGroup, FamilyNameTag,
    Character, CharacterVersion, CharacterVersionTag)

from myproject.utils_admin import label_for_m2m_field, GreenAddButtonMixin
from myproject.utils_models import Tag



class TagAdminForm(ModelForm):

    class Meta:
        model = Tag
        exclude = []
        widgets = {'color': TextInput(attrs={'type': 'color'})}


@admin.register(FirstNameTag, FamilyNameTag, CharacterVersionTag)
class TagAdmin(admin.ModelAdmin):
    fields = ['author', 'title', 'color']
    form = TagAdminForm
    list_display = ['id', 'author', 'title', 'color']
    list_editable = fields


#  ------------------------------------------------------------


@admin.register(FirstNameGroup)
class FirstNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


class FirstNameAdminForm(GreenAddButtonMixin, ModelForm):
    tags = ModelMultipleChoiceField(
        queryset=FirstNameTag.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Tags', is_stacked=False),
        label=label_for_m2m_field('Tags'),
    )

    class Meta:
        model = FirstName
        fields = '__all__'


@admin.register(FirstName)
class FirstNameAdmin(admin.ModelAdmin):
    form = FirstNameAdminForm
    list_display = [
        'id', 'gender', 'origin', 'nominative', 'genitive', 'description',
    ]
    list_editable = [
        'gender', 'origin', 'nominative', 'genitive', 'description',
    ]


#  ------------------------------------------------------------


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


class FamilyNameAdminForm(GreenAddButtonMixin, ModelForm):
    tags = ModelMultipleChoiceField(
        queryset=FamilyNameTag.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Tags', is_stacked=False),
        label=label_for_m2m_field('Tags'),
    )

    class Meta:
        model = FamilyName
        fields = '__all__'


@admin.register(FamilyName)
class FamilyNameAdmin(admin.ModelAdmin):
    form = FamilyNameAdminForm
    list_display = [
        'id', 'origin', 'nominative', 'nominative_pl', 'genitive',
        'genitive_pl', 'description',
    ]
    list_editable = [
        'origin', 'nominative', 'nominative_pl', 'genitive', 'genitive_pl',
        'description',
    ]



#  ------------------------------------------------------------

