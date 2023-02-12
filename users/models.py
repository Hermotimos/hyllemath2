from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, ImageField, TextField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    image = ImageField(_("image"), upload_to='users', blank=True, null=True)
    collation = CharField(max_length=30, blank=True, null=True)
    bio = TextField(max_length=1000, blank=True, null=True)
    is_spectator = models.BooleanField(default=False)   # Designates whether the user can view site content but without editing it

    @property
    def can_action(self):
        return self.is_active and not self.is_spectator

    @property
    def can_view_all(self):
        return self.is_superuser or self.is_staff or self.is_spectator

    @property
    def user_img_url(self):
        try:
            return self.image.url
        except ValueError:
            return f"{settings.STATIC_URL}imgs/user_default.jpg"


#     @property
#     def undone_demands(self):
#         demands = self.received_demands.exclude(author=self)
#         return demands.exclude(is_done=True)

#     @property
#     def unseen_announcements(self):
#         from communications.models import AnnouncementStatement
#         announcements = self.threads_participated.filter(
#             kind="Announcement",
#             statements__in=AnnouncementStatement.objects.exclude(seen_by=self))
#         if self.status == 'gm':
#             return announcements.filter(participants=self)
#         return announcements

#     @property
#     def unseen_debates(self):
#         from communications.models import DebateStatement
#         debates = self.threads_participated.filter(
#             kind="Debate",
#             statements__in=DebateStatement.objects.exclude(seen_by=self))
#         if self.status != 'gm':
#             return debates.filter(participants=self)
#         return debates

