
def image_upload_path(instance, filename) -> str:
    return f"{instance.category}/{filename}"


# # Pierwotna wersja tej funkcji, zobaczyć czy nie będzie potrzebna w kontekście GCP
# def image_upload_path(instance, filename):
#     from django.conf import settings
#     print(settings.MEDIA_ROOT + '/{0}/{1}'.format(instance.category, filename))
#     return settings.MEDIA_ROOT + '/{0}/{1}'.format(instance.category, filename)
