from django.urls import path

from api import views

urlpatterns = [
    path(r"eula-agreed/", views.EulaAgreedView.as_view()),
    path(r"delete-account/", views.DeleteAccountView.as_view()),
]
