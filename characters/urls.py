from django.urls import path
from characters import views


app_name = 'characters'
urlpatterns = [
    path(
        'characterversions/',
        views.CharacterVersionListView.as_view(),
        name='characterversion-list'
    ),
    path(
        'characterversion/<int:pk>/',
        views.CharacterVersionDetailView.as_view(),
        name='characterversion-detail'
    ),
    path('generic/', views.generic_relations_exemplary_view, name='generic'),
]
