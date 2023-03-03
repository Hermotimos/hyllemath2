from django.contrib import admin
from django.utils.html import format_html



class FirstNameGroupAdminFilter(admin.SimpleListFilter):
    title = 'firstnamegroup'
    parameter_name = 'firstnamegroup'

    def lookups(self, request, model_admin):
        """
        Override a method that serves uniquely for overriding.
        Return a list of tuples (value, verbose value).
        """
        qs = model_admin.get_queryset(request)
        items = [
            (
                f"{obj.firstnamegroup.id}|{obj.firstnamegroup.parentgroup.id}",
                format_html(f'<strong style="color: #7fff00;">{obj.firstnamegroup.title}</strong> [{obj.firstnamegroup.parentgroup.title}]')
            )
            for obj in qs.distinct()
        ]
        items = list(dict.fromkeys(items))      # remove duplicates
        items.sort(key=lambda a: a[1])          # sort
        return items

    def queryset(self, request, queryset):
        if self.value():
            firstnamegroup_id, parentgroup_id = self.value().split('|')
            return queryset.filter(
                firstnamegroup_id=firstnamegroup_id,
                firstnamegroup__parentgroup_id=parentgroup_id)
