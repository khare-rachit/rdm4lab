from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", RedirectView.as_view(url="/"), name="redirect-home"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/update/", views.update_profile, name="update-profile"),
    path(
        "profile/update/change-password/", views.change_password, name="change-password"
    ),
    path("experiments/", views.experiments, name="experiments"),
    path(
        "experiments/<str:experiment_id>/", views.experiments_id, name="experiments-id"
    ),
    path("my-experiments/", views.my_experiments, name="my-experiments"),
    path(
        "my-experiments/<str:experiment_id>/",
        views.my_experiments_id,
        name="my-experiments-id",
    ),
    path(
        "my-experiments/<str:experiment_id>/data/",
        views.redirect_to_experiment_data,
        name="redirect-to-experiment-data",
    ),
    path(
        "my-experiments/<str:experiment_id>/data/analysis/",
        views.redirect_to_experiment_data_analysis,
        name="redirect-to-experiment-data-analysis",
    ),
]
