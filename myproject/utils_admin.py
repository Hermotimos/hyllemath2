

def formfield_with_cache(db_field, formfield, request):
    # the condition "if formfield:" may be useful at the beginning, if errors
    # when an extra computed field gets here
    choices = getattr(request, f'_{db_field.name}_choices_cache', None)
    if choices is None:
        choices = list(formfield.choices)
        setattr(request, f'_{db_field.name}_choices_cache', choices)
    formfield.choices = choices
    return formfield



class CachedFormfieldsM2M:
    """
    A mixin to ensure cache usage by formfields of ManyToMany fields.
    In order to use cache for all M2M fields, simply apply mixin to admin class.
    In order to restrict cache to certain M2M fields, name them in
    cached_m2m_formfields list, ex. cached_m2m_formfields = ['myfields', 'others'].
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



class CachedFormfieldsFK:
    """
    A mixin to ensure cache usage by formfields of foreign key fields.
    In order to use cache for all FK fields, simply apply mixin to admin class.
    In order to restrict cache to certain FK fields, name them in
    cached_fk_formfields list, ex. cached_fk_formfields = ['myfield', 'other'].
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


class CachedFormfieldsAll(CachedFormfieldsFK, CachedFormfieldsM2M):
    """A utility class for joining the effects of its parent classes."""
    pass
