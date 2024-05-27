from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from rest_framework.response import Response
# from rest_framework.authentication import JWT
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import status


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
        # print(request.data)
        quiz = Quiz.objects.get(pk=pk)
        quiz.archived = True
        quiz.save()
        questions_data = request.data['questions']
        # print(self.queryset.get(pk=pk).archived)
        for ques_data in questions_data:
            ques = Questions.objects.get(pk=ques_data['uid'])
            ques.archived = True
            ques.save()
            options_data = ques_data['options']
            for option_data in options_data:
                option = Options.objects.get(pk=option_data['uid'])
                option.archived = True
                option.save()
                # print(option.archived)

        return Response({"message": "destroy method","quiz":quiz},status=status.HTTP_200_OK)

# display only non-archievd quizes
    # def get_queryset(self):
    #     return Quiz.objects.filter(archived=False)
    def create(self,request):
        data = request.data
        user = User.objects.get(pk=request.user.uid)
        data['created_by'] = user.uid

        print(data)
        serializer = QuizSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Filter quizzes to only those that belong to the authenticated user and are not archived
        # print(self.request.user.uid)
        return Quiz.objects.filter(created_by=self.request.user.uid, archived=False)
    

    # def retrieve(self, request):
    #     print(request)
    #     return super().retrieve(request)
# doesn't display archived quizes anyway hehe
    # def retrieve(self, request, pk):
    #     print(request.data)
    #     return super().retrieve(request,pk)


class OptionViewset(ModelViewSet):
    queryset = Options.objects.all()
    serializer_class = OptionSerializer
