from django.contrib import admin



class FirstNameGroupOfFirstNameFilter(admin.SimpleListFilter):
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
                obj.firstnamegroup
            )
            for obj in qs.distinct()
        ]
        items = list(dict.fromkeys(items))      # remove duplicates
        items.sort(key=lambda a: str(a[1]))     # sort
        return items

    def queryset(self, request, queryset):
        if self.value():
            firstnamegroup_id, parentgroup_id = self.value().split('|')
            return queryset.filter(
                firstnamegroup_id=firstnamegroup_id,
                firstnamegroup__parentgroup_id=parentgroup_id)



class ParentgroupOfFirstNameGroupFilter(admin.SimpleListFilter):
    title = 'parentgroup'
    parameter_name = 'parentgroup'

    def lookups(self, request, model_admin):
        """
        Override a method that serves uniquely for overriding.
        Return a list of tuples (value, verbose value).
        """
        qs = model_admin.get_queryset(request)
        qs = qs.filter(parentgroup__isnull=False)   # get only parentgroups
        items = [
            (obj.parentgroup.id, obj.parentgroup.title)
            for obj in qs.distinct()
        ]
        items = list(dict.fromkeys(items))      # remove duplicates
        items.sort(key=lambda a: a[1])          # sort
        return items

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parentgroup__id=self.value())
