from django.urls import path
from .views import StudentSignUpView, LibrarianSignUpView, CustomLoginView, CustomLogoutView
from . import views

urlpatterns = [
    path('signup/student/', StudentSignUpView.as_view(), name='signup_student'),
    path('signup/librarian/', LibrarianSignUpView.as_view(), name='signup_librarian'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('set-password/', views.set_password, name='set_password'),
    path('password-reset/success/', views.password_reset_success, name='password_reset_success'),

    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]