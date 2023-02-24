from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import ManyToOneRel
from django.utils.html import format_html


def label_for_m2m_field(verbose_name):
    info = """
        <br><br>
        <b style="color: #7FFF00">
            Zielony krzyżyk do dodawania nowych obiektów M2M będzie widoczny po zapisaniu forlumarza
        </b>
    """
    return format_html(verbose_name + info)


class GreenAddButtonMixin:
    """
    A mixin for enabling the green 'add' button aside M2M form fields.
    This feature also requires declaration of each M2M field as a
    ModelMultipleChoiceField within the form that uses this mixin.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            rel = ManyToOneRel('tags', self.instance.tags.model, 'id')
            self.fields['tags'].widget = RelatedFieldWidgetWrapper(self.fields['tags'].widget, rel, admin_site)

