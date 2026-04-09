from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/<str:institution>/', views.login_view, name='login'),
    path('vote/', views.vote_view, name='vote'),
    path('vote/success/', views.vote_success, name='vote_success'),
    path('results/', views.results_view, name='results'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/signup/', views.admin_signup, name='admin_signup'),
    path('admin/upload-excel/', views.upload_students_excel, name='upload_excel'),
    path('api/results/', views.api_results, name='api_results'),
]
