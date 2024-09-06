# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('app/', views.app, name='app'),
    path('video_processing/', views.video_processing_page, name='video_processing'),
    path('get_srt_index/', views.get_srt_index, name='get_srt_index'),
    path('process', views.process, name='process'),
    path('process_video/', views.process_video, name='process_video'),
    path('upload_new_scene/', views.upload_new_scene, name='upload_new_scene'),
    path('uploads/<str:filename>/', views.download_file, name='download_file'),
]
