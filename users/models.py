from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import PROTECT, BooleanField, CharField, OneToOneField
from django.db.models.functions import Collate

from resources.models import Picture


class User(AbstractUser):
    picture = OneToOneField(Picture, on_delete=PROTECT, blank=True, null=True)
    collation = CharField(max_length=30, blank=True, null=True)
    is_spectator = BooleanField(default=False)   # Indicates if user can view site content but without editing it

    class Meta:
        ordering = [Collate('username', 'pl-PL-x-icu')]

    @property
    def is_gamemaster(self):
        return all(self.is_staff, self.is_superuser)

    @property
    def is_auxiliary(self):
        """Potentially for game masters missing full admin permissions?"""
        return self.is_staff and not self.is_superuser

    @property
    def is_player(self):
        return not any(self.is_staff, self.is_superuser, self.is_spectator)

    @property
    def is_active_player(self):
        return all(self.is_player, self.is_active)

    @property
    def can_action(self):
        return self.is_active and not self.is_spectator

    @property
    def can_view_all(self):
        return any(self.is_superuser, self.is_staff, self.is_spectator)

    @property
    def picture_url(self):
        try:
            return self.picture.image.url
        except ValueError:
            return settings.STATIC_URL + "users/default.jpg"


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

