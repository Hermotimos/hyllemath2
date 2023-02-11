from urllib.parse import urljoin

from django.conf import settings
from google.cloud import storage
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


# ----------------------------------------------------------------------------


class GoogleCloudStaticFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a static file path from STATIC_URL
     not google generated one.
     """
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'static'

    def url(self, name):
        """Gives correct STATIC_URL and not google generated url."""
        print('STATIC',  settings.STATIC_URL, name, '//', urljoin(settings.STATIC_URL, name))
        return urljoin(settings.STATIC_URL, name)


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    """Google file storage class which gives a media file path from MEDIA_URL
    not google generated one.
    """
    bucket_name = setting('GS_BUCKET_NAME')
    location = 'media'

    def url(self, name):
        """Gives correct MEDIA_URL and not google generated url."""
        print('MEDIA', settings.MEDIA_URL, name, '//', urljoin(settings.MEDIA_URL, name))
        return urljoin(settings.MEDIA_URL, name)


def upload_to_bucket(destination_path, source_path, bucket_name):
    # This isn't used at the time, but might be useful as a template
    storage_client = storage.Client.from_service_account_json(
        settings.GOOGLE_APPLICATION_CREDENTIALS)
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(source_path)
    
    return blob.public_url


# ----------------------------------------------------------------------------
