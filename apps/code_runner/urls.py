from django.urls import path
from .views import LanguagesView, ExecuteCodeView

urlpatterns = [
    path('languages/', LanguagesView.as_view(), name='code_languages'),
    path('execute/', ExecuteCodeView.as_view(), name='code_execute'),
]
