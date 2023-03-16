from django.contrib import admin

# Register your models here.

prepopulated_fields = {
    'genitive': ['nominative'],
    'adjectiveroot': ['nominative']
}