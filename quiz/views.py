from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from rest_framework.response import Response
# from rest_framework.authentication import JWT
from rest_framework.permissions import IsAuthenticated
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

        return Response({"message": "destroy method"})

# display only non-archievd quizes
    # def get_queryset(self):
    #     return Quiz.objects.filter(archived=False)

    def get_queryset(self):
        # Filter quizzes to only those that belong to the authenticated user and are not archived
        print(self.request.data)
        return Quiz.objects.filter(created_by=self.request.data['created_by'], archived=False)

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


# from rest_framework_simplejwt.tokens import RefreshToken
# from .serializer import AuthTokenSerializer

# class ObtainAuthTokenView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = AuthTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }, status=status.HTTP_200_OK)
