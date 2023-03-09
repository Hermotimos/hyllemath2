from django.contrib.admin import ModelAdmin


# -----------------------------------------------------------------------------


def formfield_with_cache(db_field, formfield, request):
    if formfield:
        # this condition is useful to avoid errors for M2M fields absent
        # from the form, so formfield is None, ex. Character.relationships
        choices = getattr(request, f'_{db_field.name}_choices_cache', None)
        if choices is None:
            choices = list(formfield.choices)
            setattr(request, f'_{db_field.name}_choices_cache', choices)
        formfield.choices = choices
    return formfield



class CachedFormfieldsM2MMixin:
    """
    A mixin to ensure cache usage by formfields of ManyToMany fields.
    In order to use cache for all M2M fields, simply apply mixin to admin class.
    In order to restrict cache to certain M2M fields, name them in
    cached_m2m_formfields list, ex. cached_m2m_formfields = ['myfields', 'others'].
    Can be used in ModelAdmin and inlines.
    """
    cached_m2m_formfields = '__all__'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if self.cached_m2m_formfields == '__all__':
            formfield = formfield_with_cache(db_field, formfield, request)
        else:
            if db_field.name in self.cached_m2m_formfields:
                formfield = formfield_with_cache(db_field, formfield, request)
        return formfield



class CachedFormfieldsFKMixin:
    """
    A mixin to ensure cache usage by formfields of foreign key fields.
    In order to use cache for all FK fields, simply apply mixin to admin class.
    In order to restrict cache to certain FK fields, name them in
    cached_fk_formfields list, ex. cached_fk_formfields = ['myfield', 'other'].
    Can be used in ModelAdmin and inlines.
    """
    cached_fk_formfields = '__all__'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if self.cached_fk_formfields == '__all__':
            formfield = formfield_with_cache(db_field, formfield, request)
        else:
            if db_field.name in self.cached_fk_formfields:
                formfield = formfield_with_cache(db_field, formfield, request)
        return formfield


class CachedFormfieldsAllMixin(CachedFormfieldsFKMixin, CachedFormfieldsM2MMixin):
    """
    A utility class for joining the effects of its parent classes.
    Can be used in ModelAdmin and inlines.
    """
    pass


class CustomModelAdmin(CachedFormfieldsAllMixin, ModelAdmin):
    """
    A class to encapsulate some reapeating code for optimizations of
    ModelAdmin FK and M2M formfields queries and other utilities,
    like filter_horizontal.
    """
    pass


# -----------------------------------------------------------------------------


def get_count_color(value):
    colors = {
        range(0, 1): "#00ffff",
        range(2, 3): "#00ff00",
        range(3, 4): "#ffff00",
        range(4, 5): "#ff8000",
        range(5, 11): "#ff0000",
        range(11, 10000): "#ff007f",
    }
    for k, v in colors.items():
        if value in k:
            return v
