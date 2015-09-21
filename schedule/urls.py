"""vubics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from .views import (
    detail_all_courses,
    ics_for_course,
    ics_for_selection,
    detail_for_selection,
    create_selection,
    edit_selection,
    selection_planning,)

urlpatterns = [
    url(r'^course$', detail_all_courses, name='all_courses'),

    url(r'^course/(?P<course_id>\d+)\.ics$',
        ics_for_course, name='course_ics'),

    url(r'^selection/(?P<selection_id>\d+)\.ics$',
        ics_for_selection, name='selection_ics'),

    url(r'^selection/(?P<selection_id>\d+)$',
        detail_for_selection, name='selection_detail'),

    url(r'^selection/create$',
        create_selection, name='create_selection'),

    url(r'^selection/(?P<selection_id>\d+)/edit$',
        edit_selection, name='edit_selection'),

    url(r'^selection/(?P<selection_id>\d+)/planning$',
        selection_planning, name='selection_planning'),
]
