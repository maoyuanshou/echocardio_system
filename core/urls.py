from django.urls import path
from core import views
from core.views import doctor_dashboard, diagnose_video, admin_dashboard, change_user_role, role_change_history

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/download/<int:video_id>/', views.download_video, name='download_video'),
    path('patient/download_diagnosis/<int:video_id>/', views.download_diagnosis, name='download_diagnosis'),
    path('upload/', views.upload_video, name='upload_video'),
    path('videos/', views.video_list, name='video_list'),

    path('classify/<int:video_id>/', views.classify_view, name='classify_video'),
    path('detect_mi/<int:video_id>/', views.detect_mi_view, name='detect_mi'),

    path('doctor/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/diagnose/<int:video_id>/', diagnose_video, name='diagnose_video'),

    path('admin/dashboard/', admin_dashboard, name='admin_manage_dashboard'),
    path('admin/change_role/<int:user_id>/', change_user_role, name='change_user_role'),
    path('admin/role-history/', views.role_change_history, name='role_change_history'),
    path('admin/all-users/', views.admin_all_users_view, name='admin_all_users'),
    path('admin/edit-user/<int:user_id>/', views.edit_user_info, name='edit_user_info'),
    path('admin/video-records/', views.admin_video_records, name='admin_video_records'),

]
