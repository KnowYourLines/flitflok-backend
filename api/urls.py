from django.urls import path

from api import views

urlpatterns = [
    path(r"eula-agreed/", views.EulaAgreedView.as_view()),
]
