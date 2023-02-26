

def formfield_with_cache(field, formfield, request):
    choices = getattr(request, f'_{field}_choices_cache', None)
    if choices is None:
        choices = list(formfield.choices)
        setattr(request, f'_{field}_choices_cache', choices)
    formfield.choices = choices
    return formfield