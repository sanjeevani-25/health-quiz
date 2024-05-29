from .views import *
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('quiz', QuizViewset)
router.register('questions', QuestionViewset)
router.register('options', OptionViewset)
router.register('scheduled-event',ScheduledEventViewSet)
router.register('quiz-performance',QuizPerformanceViewset)
router.register('quiz-filtered',QuizFilteredViewset, basename='quiz-filtered')
router.register('quiz-performance-of-user',QuizPerformanceOfUser, basename='quiz-performance-of-user')

urlpatterns = [
    path('', include(router.urls)),
    # path('quiz-filtered/',FilteredQuiz)
]

'''
# register user
# getuser
# register quiz
# get all quiz
# get particular quiz and its question-options
# Update Quiz and Questions
# delete quiz
# save quiz performance
# get-filtered-quiz (filter by doctor and (category or title))
get total performance of user
get detailed quiz performance of user
#### get list of quiz events completed  by therapist
#### apply filter to get overall performance of students
'''