from django.urls import path
from .views import cMode,exam_codes_api,homepage,ClassResult,ClassResults,AcademicResult,semresult,notify


urlpatterns = [
    path('api/classresults',ClassResults.as_view()),
    path('api/classresult',ClassResult.as_view()),
    path('api/single',AcademicResult.as_view()),
    path('api/result',semresult.as_view()),
    path('api/cmode',cMode.as_view()),
    path('api/examcodes', exam_codes_api, name='exam_codes_api'),
    path('api/notifications',notify,name='notify'),
    path('',homepage)
]
