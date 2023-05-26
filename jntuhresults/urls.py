from django.urls import path
from .views import multi,allResults,result,cMode,exam_codes_api

urlpatterns = [
    path('api/multi',multi.as_view()),
    path('api/single',allResults.as_view()),
    path('api/result',result.as_view()),
    path('api/cmode',cMode.as_view()),
    path('api/ExamCodes', exam_codes_api, name='exam_codes_api'),
]
