from django.urls import path
from characters import views


app_name = 'characters'
urlpatterns = [
    path('characters/', views.characters_main_view, name='characters'),
    path('generic/', views.generic_relations_exemplary_view, name='generic'),
]
