from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas

# from rest_framework.authentication import JWT
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status
from .tasks import *

class QuestionViewset(ModelViewSet):
    queryset = Questions.objects.all()
    serializer_class = QuestionSerializer


class QuizViewset(ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    # def get_object(self):
    #     obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
    #     self.check_object_permissions(self.request, obj)
    #     return obj

# archive quizes
    def destroy(self, request, pk):
        if not self.request.user.has_perm('quiz.delete_quiz'):
            return Response({"message": "You don't have permission to delete this quiz"}, status=status.HTTP_400_BAD_REQUEST)
        # print(request.data)
        # print(quiz.created_by)
        quiz = Quiz.objects.get(pk=pk)
        if request.user!=quiz.created_by:
            return Response({"message": "You are not authorized to delete this quiz."}, status=status.HTTP_400_BAD_REQUEST)
        if quiz.archived:
            return Response({"message": "Quiz already deleted"}, status=status.HTTP_400_BAD_REQUEST)
        quiz.archived = True
        quiz.save()
        # questions_data = request.data['questions']
        questions_data = Questions.objects.filter(quiz=pk)
        # print(Questions.objects.filter(quiz=pk))
        # print(self.queryset.get(pk=pk).archived)
        for ques_data in questions_data:    
            # print(ques_data)
            ques_data.archived=True
            ques_data.save()
            options_data = Options.objects.filter(question=ques_data.uid)
            for option_data in options_data:
                option_data.archived = True
                option_data.save()
                # print(option.archived)

        return Response({"message": "destroy method","quiz":quiz.uid},status=status.HTTP_200_OK)

# display only non-archievd quizes
    # def get_queryset(self):
    #     return Quiz.objects.filter(archived=False)
    def create(self,request):
        data = request.data
        user = User.objects.get(pk=request.user.uid)
        data['created_by'] = user.uid
        # print("views data",data)
        # print(data)
        serializer = QuizSerializer(data=data)
        if serializer.is_valid():
            # print("sssssss ",serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Filter quizzes to only those that belong to the authenticated user and are not archived
        # print(self.request.user.uid)
        if (self.request.user.type=='ADMIN' or self.request.user.type=='USER'):
            return Quiz.objects.all()
        return Quiz.objects.filter(created_by=self.request.user.uid, archived=False)

class OptionViewset(ModelViewSet):
    queryset = Options.objects.all()
    serializer_class = OptionSerializer

class ScheduledEventViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ScheduledEvent.objects.all()
    serializer_class = ScheduledEventSerializer

    def create(self, request):
        # print(request.user)
        data = request.data
        data['doctor']=self.request.user.uid
        
        serializer = ScheduledEventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request,pk):
        instance = self.get_object()
        # if instance.doctor != self.request.user:
        #     return Response({"msg":"Not authorized"})
        data =request.data
        data['doctor']=self.request.user.uid
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.type =='DOCTOR':
            queryset = queryset.filter(doctor=user.uid)
            # print(queryset.count())
        elif user.type=='USER':
            queryset = queryset.filter(user=user.uid)
        else:
            raise ValidationError("You are admin")
        #     return Response({"message":"You are admin"})
        
        if queryset.count()==0:
            raise ValidationError("You don't have any scheduled quiz")
        #     return Response({"message":"You don't have any scheduled quiz"})

        return queryset

    def destroy(self,request,pk):
        event = self.get_object()
        # print(event)
        event.archived=True
        event.save()
        return Response({f"Event archived"})

class QuizPerformanceViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = QuizPerformance.objects.all()
    serializer_class = QuizPerformanceSerializer

    def get_queryset(self):
        user = self.request.user
        print(user.type)
        if user.type=='DOCTOR':
            queryset = QuizPerformance.objects.filter(event__doctor=user)
        elif user.type=='USER':
            queryset = QuizPerformance.objects.filter(event__user=user)
        return queryset
    

    def retrieve(self, request, pk):
        # queryset = self.get_queryset()
        return QuizPerformance.objects.get(uid=pk)
    
    def create(self,request):
        print(request.data)
        serializer = QuizPerformanceSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def update(self,request,pk):
        pass

    def destroy(self,request,pk):
        qp = self.get_object()
        qp.archived=True
        qp.save()
        return Response({f"Quiz performance archived"})

class QuizFilteredViewset(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):
        data = self.request.data

        try:
            doctor = data['doctor']
        except KeyError:
            raise ValidationError("Doctor field is required.")
        
        if 'quiz_title' in data and 'category' in data:
            quiz_title = data['quiz_title']
            category = data['category']
            print("all")
            queryset = Quiz.objects.filter(quiz_title=quiz_title,category=category, created_by=doctor)
        elif 'quiz_title' in data:
            print("all q")
            quiz_title = data['quiz_title']
            queryset = Quiz.objects.filter(quiz_title=quiz_title, created_by=doctor)
        elif 'category' in data:
            category = data['category']
            queryset = Quiz.objects.filter(category=category, created_by=doctor)
        else:
            raise ValidationError("Enter either quiz title or category of the quiz.")

        return queryset



class QuizPerformanceOfUser(ModelViewSet):
    queryset = QuizPerformance.objects.all()
    serializer_class = QuizPerformanceSerializer

    # def get_queryset(self):
    #     # print(self.request.data)
    #     user = self.request.data['user']
    #     # user = self.request.user
    #     # print(user)

    #     queryset = QuizPerformance.objects.filter(event__user=user)
    #     return queryset
    
    def retrieve(self,request,pk):

        serializer = QuizPerformanceSerializer(QuizPerformance.objects.get(uid=pk))

        res = generate_pdf_file.delay(pk)

        return Response({"data":serializer.data}, status=status.HTTP_200_OK)


class ScheduleEventTimedView(APIView):
    def post(self, request):
        print(request.data)
        data = request.data
        doc_id = data['doctor']
        user_id = data['user']
        quiz_id = data['quiz']
        is_cancelled = data['is_cancelled']
  
        create_event.apply_async(args=[doc_id, user_id, quiz_id, is_cancelled])
        return Response({'status': 'Event creation scheduled'}, status=status.HTTP_201_CREATED)


# def check_pdf_status(request, task_id):
#     # sleep(20)
#     res = AsyncResult(task_id)
#     if res.state == 'SUCCESS':
#         output_path = res.result
#         if os.path.exists(output_path):
#             return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f'{task_id}.pdf')
#     elif res.state == 'FAILURE':
#         return JsonResponse({'status': 'failed', 'error': str(res.result)})
#     return JsonResponse({'status': res.state})
