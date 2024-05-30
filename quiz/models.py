from django.db import models
import uuid
from roles.models import *

# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Quiz(BaseModel):
    CATEGORIES = {
        'E': 'Easy',
        'M': 'Medium',
        'H': 'Hard'
    }
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='quizes')
    quiz_title = models.CharField(max_length=100)
    number_of_questions = models.IntegerField(null=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='E')
    time_duration = models.TimeField(auto_now=False, auto_now_add=False)
    '''
    '%H:%M:%S',     # '14:30:59'           '%H:%M',        # '14:30'
    '''

    class Meta:
        db_table = 'QUIZ'

    def __str__(self):
        return str(self.uid)
        # return str(self.quiz_title)


class Questions(BaseModel):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    question_name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=200, null=True)
    number_of_options = models.IntegerField(null=True)

    def __str__(self):
        return self.question_name

    class Meta:
        db_table = 'QUESTIONS'


class Options(BaseModel):
    question = models.ForeignKey(
        Questions, on_delete=models.CASCADE, related_name='options')
    option_name = models.CharField(max_length=50)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'OPTIONS'

    def __str__(self) -> str:
        return self.option_name

class ScheduledEvent(BaseModel):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_doctor')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_user')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='scheduled_quiz')
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'SCHEDULED_EVENTS'
    '''
    id
    doc id student id, quiz id, is cancelled'''

class QuizPerformance(BaseModel):
    # event_id = models.ForeignKey(ScheduledEvent, on_delete=models.CASCADE, related_name='quiz_performance', unique=True)
    event = models.OneToOneField(ScheduledEvent,on_delete=models.CASCADE, related_name='quiz_performance')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='quiz_performance_ques')
    user_answer = models.ForeignKey(Options, on_delete=models.CASCADE , related_name='selected_option')
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'QUIZ_PERFORMANCE'
    '''event id -- unique 
    appointment 
    doc id -- user id
    quiz 
    question -- (option chosen)
    user response 
    iscorrect 
    created at 
    updated Attribute
    is archived'''
