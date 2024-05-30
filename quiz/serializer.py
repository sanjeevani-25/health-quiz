from .models import *
from roles.serializer import *
from rest_framework import serializers
# from .errorhandler import ErrorHandler
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = ('uid', 'option_name', 'is_correct', 'archived')

class QuestionSerializer(serializers.ModelSerializer):
    # options = serializers.StringRelatedField(many=True)
    options = OptionSerializer(many=True)

    class Meta:
        model = Questions
        fields = ('uid', 'question_name',
                  'number_of_options', 'options', 'archived')

    def create(self, validated_data):
        # print(validated_data)
        options_data = validated_data.pop('options')
        question = Questions.objects.create(**validated_data)
        for option_data in options_data:
            Options.objects.create(question=question, **option_data)
        return question


class QuizSerializer(serializers.ModelSerializer):
    permission_classes = [IsAuthenticated]
    questions = QuestionSerializer(many=True)
    # created_by = serializers.SerializerMethodField()

    # def get_object(self):
    #     obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
    #     self.check_object_permissions(self.request, obj)
    #     print(self.check_object_permissions(self.request, obj))
    #     return obj
    def get_created_by(self, obj):
        print("obj ",obj)
        return obj.created_by.get_full_name()  
    
    def validate_created_by(self, value):
        print("created_ by ",value)
        # print(value.has_perm("quiz.add_quiz")==False)
        # if(value.has_perm("quiz.add_quiz")==False):
        if value.groups.filter(name='User').exists():
            raise ValidationError("You are not authorized to create / update / delete quiz")
            # return Response({"message":"you are not authorized"})
        # if (value.role == 'User'):
        #     raise ValidationError("You are not authorized to create quiz")
        return value

    def validate(self, data):
        print("data ", data)
        # print(type(data))
        # data['created_by']=self.request.user.uid
        num_ques = data['number_of_questions']
        ques_list = data['questions']
        if (num_ques != len(ques_list)):
            raise ValidationError("Number of questions don't match")

        for ques in ques_list:
            num_options = ques['number_of_options']
            option_list = ques['options']
            if (num_options != len(option_list)):
                raise ValidationError("Number of options don't match")

        return data

    def create(self, validated_data):
        # print("csgdyfgyudshg")
        # print("valid data ", validated_data)
        # validated_data['created_by']= User.objects.get(pk=self.user.uid).uid
        # print(type(validated_data.get('created_by').role.get_rolenum()))
        questions_data = validated_data.pop('questions')
        print("validd",validated_data)
        quiz = Quiz.objects.create(**validated_data)
        print("quiz",quiz)
        for ques_data in questions_data:
            # print(ques_data)
            options_data = ques_data.pop('options')
            question = Questions.objects.create(quiz=quiz, **ques_data)
            # print(ques_data)
            # print(options_data)
            for option_data in options_data:
                Options.objects.create(question=question, **option_data)
        return quiz

    def update(self, instance, validated_data):
        '''
        {'quiz_title': 'quiz 200 updated', 'created_by': <User: 43e69e16-8d0d-44c7-825f-4a53bd820eb5>, 'time_duration': datetime.time(2, 0), 'questions': [{'question_name': 'thsi quiz 200 1 updated?', 'number_of_options': 1, 'options': [{'option_name': 'option111', 'is_correct': True}]}], 'number_of_questions': 1}
        '''

        # user = User.objects.get(email=validated_data['created_by'])
        # if (user.has_perm('quiz.change_quiz')==False):
        #     return ValidationError("Update not permitted.")
        # print(user.is_authenticated==True)
        # print(list(instance.questions.all())[0].uid)
        questions_data = validated_data.pop('questions')
        questions = instance.questions.all()
        questions = list(questions)
        instance.quiz_title = validated_data['quiz_title']
        instance.time_duration = validated_data['time_duration']
        # created_by can't be updated
        instance.save()
        # print(questions_data)
        for ques_data in questions_data:
            # ques = questions.get(pk=ques_data['uid'])
            # print(ques)
            ques = questions.pop(-1)
            ques.question_name = ques_data.get(
                'question_name', ques.question_name)
            ques.save()
            options = list(ques.options.all())
            options_data = ques_data['options']
            # print(options_data)
            for option_data in options_data:
                option = options.pop(-1)
                option.option_name = option_data.get(
                    'option_name', option.option_name)
                option.is_correct = option_data.get(
                    'is_correct', option.is_correct)
                option.save()
            '''
            {'question_name': 'thsi quiz 200 1 updated?', 'number_of_options': 1, 'options': [{'option_name': 'option111', 'is_correct': True}]}
            '''
        # print(validated_data)
        return instance

    class Meta:
        model = Quiz
        fields = ('uid', 'quiz_title','created_by', 'time_duration',
                  'questions', 'number_of_questions', 'archived', 'category')


class ScheduledEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScheduledEvent
        fields = ['uid', 'doctor','user', 'quiz', 'is_cancelled']
        # fields='__all__'

    def create(self, validated_data):
        print(validated_data)
        doctor = validated_data.pop('doctor')
        print(doctor.uid)
        if doctor.type!='DOCTOR':
            raise ValidationError("You are not authorised to create event (not a doc)")
        user = User.objects.get(email=validated_data.pop('user'))
        if user.type!='USER':
            raise ValidationError("user is not a user (instead doc or admin).")
        # print(validated_data.get('quiz').uid)
        quiz = validated_data.pop('quiz')
        if quiz.created_by.uid != doctor.uid:
            raise ValidationError("You have not created this quiz.")
        # print(quiz.created_by.uid)
        event = ScheduledEvent.objects.create(doctor_id=doctor.uid, user_id=user.uid, quiz_id=quiz.uid, **validated_data)
        return event

class QuizPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizPerformance
        fields = '__all__'
        # depth = 2
    
    def validate(self, data):
        # print("data ",data)
        event = data['event']

        try:
            question = event.quiz.questions.get(uid=data['question'].uid)
            option = question.options.get(uid=data['user_answer'].uid)

        except Questions.DoesNotExist:
            raise ValidationError("Question not present in quiz assigned to event.")

        except Options.DoesNotExist:
            raise ValidationError("Option not present in assigned Question.")

        return data
    
    def create(self,data):
        # print("valid ", data)
        # print("data ",data)
        event = data['event']
        question = event.quiz.questions.get(uid = data['question'].uid)
        option = question.options.get(uid = data['user_answer'].uid)
        data['is_correct'] = option.is_correct
        performance = QuizPerformance.objects.create(**data)
        return performance


