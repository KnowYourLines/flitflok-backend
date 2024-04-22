from django.urls import path

from api import views

urlpatterns = [
    path(r"eula-agreed/", views.EulaAgreedView.as_view()),
    path(r"delete-account/", views.DeleteAccountView.as_view()),
    path(r"video/", views.VideoView.as_view()),
    path(r"video/<uuid:pk>/hide/", views.VideoHideView.as_view()),
    path(r"video/<uuid:pk>/report/", views.VideoReportView.as_view()),
    path(r"video/<uuid:pk>/block/", views.VideoBlockView.as_view()),
    path(r"video/<uuid:pk>/go/", views.VideoGoView.as_view()),
]
