from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
    path('register/<str:choice>', views.register_choice, name = 'register_choice'),
    path('create/', views.create, name='create'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category>', views.categories, name='categories'),
    path('instructor/<str:username>', views.instructor, name='instructor'),
    path('student/<str:username>', views.student, name='student'),
    path('course/<int:id>', views.course, name='course'),
    path('join_course/<int:id>', views.join_course, name='join_course'),
    path('course_view/<int:id>', views.course_view, name='course_view'),
    path('disable_course/<int:id>', views.disable_course, name='disable_course'),
    path('certificate/<int:id>', views.certificate, name='certificate'),
    path('review/<int:id>', views.review, name='review'),
    path('comment/<int:id>', views.comment, name='comment'),

    # API Routes
    path("like/<int:id>/<str:content>", views.like, name="like"),
    path("completed/<int:id>", views.completed, name="completed")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)