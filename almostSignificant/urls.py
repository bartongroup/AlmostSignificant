from django.conf.urls import patterns, url
from almostSignificant import views
urlpatterns = patterns('',
    url(r'^$', views.overview,name="run"),
    url(r'^run/(\d{6}_[^/]+)/$', views.runView, name="runView"),
    url(r'^run/(\d{6}_[^/]+)/Ajax/$', views.runAjax), 
    url(r'^run/(\d{6}_[^/]+)/(\d)/Ajax/$', views.laneAjax), 
#
    url(r'^runs/Ajax/$', views.datasetsAjax),
    url(r'^runs/(\d+)/Ajax/$', views.runSummaryAjax),
    url(r'^runNotes/(\d{6}_[^/]+)/$', views.runNotesEntry), 
#
    url(r'^run/\d{6}_[^/]+/sample/(\d+)/Ajax/$', views.sampleAjax), 
#
    url(r'^project/(\d+)/id/Ajax/$', views.projectSummaryAjax), 
    url(r'^project/([^/]+)/Ajax/$', views.projectAjax, name="projectAjax"), 
    url(r'^project/$', views.projectView, name="project"),
    url(r'^project/Ajax/$', views.projectsAjax, name="projectsAjax"), 
    url(r'^project/([^/]+)/$', views.projectDetailView, name="projectDetailView"),
    url(r'^project/[^/]+/sample/(\d+)/Ajax/$', views.sampleAjax), 
#    url(r'^project/[^/]+/run/(\d{6}_[^/]+)/$', views.runView),
#    url(r'^project/[^/]+/run/(\d{6}_[^/]+)/Ajax/$', views.runAjax), 
#    url(r'^project/[^/]+/run/(\d{6}_[^/]+)/(\d)/Ajax/$', views.laneAjax), 
#    url(r'^project/[^/]+/runs/(\d+)/Ajax/$', views.runSummaryAjax),
#    url(r'^project/[^/]+/run/\d{6}_[^/]+/sample/(\d+)/Ajax/$', views.sampleAjax), 
    url(r'^project/[^/]+/runNotes/(\d{6}_[^/]+)/$', views.runNotesEntry), 
    url(r'^projectNotes/(.*)/$', views.projectNotesEntry), 
    url(r'^project/html/project/(.*)$', views.ProjectDetailViewHTML), 
#
    url(r'^stats/$', views.statistics, name="stats"),
    url(r'^stats/Ajax/$', views.statisticsAjax),
    url(r'^stats/(\w+)/Ajax/$', views.statisticsSummaryAjax),
    url(r'^stupidStats$', views.stupidStats), 

)
