from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from rest_framework.response import Response
from django.http import HttpResponse
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
    # permission_classes = [IsAuthenticated]
    queryset = QuizPerformance.objects.all()
    serializer_class = QuizPerformanceSerializer

    def get_queryset(self):
        # print(self.request.data)
        user = self.request.data['user']
        # user = self.request.user
        # print(user)

        queryset = QuizPerformance.objects.filter(event__user=user)
        return queryset
    
    def retrieve(self, request,pk):
        # print("chjgd")
        user = self.request.data['user']
        # print(user)
        serializer = QuizPerformanceSerializer(QuizPerformance.objects.filter(event__user=user).get(event=pk))
        return Response(serializer.data)

    # def create(self, request):
    #     pass
    
from celery import shared_task
from celery.result import AsyncResult

def generate_pdf(request,pk):

    # res = generate_pdf_file.apply_async(args=[pk])
    res = generate_pdf_file.delay(pk)
    # ress = AsyncResult(res)
    response = FileResponse(generate_pdf_file(pk), 
                            as_attachment=True, 
                            filename=f'{pk}.pdf')
    return response

@shared_task
def generate_pdf_file(pk):
    print("shared taskkkkk")
    # sleep(20)
    # response = HttpResponse(content_type='application/pdf')  
    # response['Content-Disposition'] = 'attachment; filename=f"{pk}.pdf"'  

    from io import BytesIO
 
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    # p= canvas.Canvas(response)
 
    quiz_performance = QuizPerformance.objects.get(uid=pk)
    y=750
    p.drawString(100, y, "Quiz Performance of User")

    user = quiz_performance.event.user 
    # print(user)
    p.drawString(100, y-40, f"User --> {user}")
    p.drawString(100, y-50, f"Question --> {quiz_performance.question}")
    options = Options.objects.filter(question=quiz_performance.question.uid)
    correct_option = None
    yvar=70
    i=1
    for option in options:
        p.drawString(100, y-yvar, f"{i}. {option}")
        if option.is_correct:
            correct_option = option
        # print(option)
        i+=1
        yvar+=10
    p.drawString(100, y-120, f"Your answer: {quiz_performance.user_answer}" )
    p.drawString(100, y-130, f"Correct answer: {correct_option}" )
    p.showPage()
    p.save()
    
    # return response
    buffer.seek(0)
    return buffer

    # return FileResponse(buffer, 
    #                         as_attachment=True, 
    #                         filename=f'{pk}.pdf')
    # print("test celery")
    # # print("result ",result)
    # return HttpResponse({"celery test"})
