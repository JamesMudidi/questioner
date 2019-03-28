from operator import itemgetter
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from meetup.models import Meeting
from meetup.serializers import MeetingSerializer
from question.models import Question
from question.serializers import QuestionSerializer
from vote.models import Vote


class Questions(APIView):
    """
        This class includes the following features;
        - adding a new question to a meeting
        - getting all questions of a particular meeting
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer

    @classmethod
    @swagger_auto_schema(
        operation_description="Get all Questions for a meet up",
        operation_id="Get all questions for a meetup",
        responses={
            200: "QuestionSerializer(many=True)",
            400: "Invalid Meetup Id",
        },
    )
    def get(self, request, meetup_id):
        """
        get:
        Get all Questions for a meet up
        """

        mymeeting = Meeting.objects.filter(id=meetup_id).first()
        if mymeeting:
            questions = Question.objects.filter(meetup_id=meetup_id)
            serializer = QuestionSerializer(questions, many=True)
            results = serializer.data
            all_questions = []
            for result in results:
                up_votes = len(
                    [
                        vote
                        for vote in Vote.objects.filter(
                            question_id=result["id"], vote=1
                        )
                    ]
                )
                dwn_votes = len(
                    [
                        vote
                        for vote in Vote.objects.filter(
                            question_id=result["id"], vote=-1
                        )
                    ]
                )
                votes = [{"up votes": up_votes, "down votes": dwn_votes}]

                Mserializer = MeetingSerializer(mymeeting, many=False)

                user = User.objects.filter(Q(id=result["created_by"])).distinct().first()
                result["created_by_name"] = user.username

                result["meetup_name"] = Mserializer.data["title"]
                result["order_by"] = up_votes
                result["votes"] = votes

                all_questions.append(result)
            return_list = sorted(all_questions, key=itemgetter('order_by'), reverse=True)
            return Response(return_list)
        return Response(
            {"error": "invalid meetup id"}, status=status.HTTP_400_BAD_REQUEST
        )

    @classmethod
    @swagger_auto_schema(
        operation_description="Create a question for a specific meetup.",
        operation_id="Create a question for a specific meetup",
        request_body=QuestionSerializer,
        responses={
            201: QuestionSerializer(many=False),
            400: "Invalid Format Data",
            401: "Unauthorized Access",
        },
    )
    def post(self, request, meetup_id):
        """
        post:
        Create a question for a specific meetup."
        """

        meeting = Meeting.objects.filter(id=meetup_id).first()
        if meeting:
            current_user = request.user
            if current_user.is_superuser:
                return Response(
                    data={
                        "error": "Admin is not allowed to add questions",
                        "status": 401,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            Mserializer = MeetingSerializer(meeting, many=False)

            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():

                serializer.save(created_by=current_user, meetup_id=meeting)
                qn_dict = dict(serializer.data)
                qn_dict["created_by"] = current_user.id
                qn_dict["created_by_name"] = current_user.username
                qn_dict["meetup_id"] = meetup_id
                qn_dict["meetup"] = Mserializer.data["title"]
                return Response(
                    data={
                        "status": status.HTTP_201_CREATED,
                        "data": [
                            {
                                "question": qn_dict,
                                "success": "Question successfully added to meetup",
                            }
                        ],
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"error": "invalid meetup id"}, status=status.HTTP_400_BAD_REQUEST
        )

class OneQuestion(APIView):
    """
    get:
    Get a question for a specific meetup."
    put:
    Update a question for a specific meetup."
    delete:
    Delete a question for a specific meetup."
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerializer

    @classmethod
    @swagger_auto_schema(
        operation_description="Get a question for a specific meetup.",
        operation_id="Get a question for a specific meetup.",
        responses={
            200: QuestionSerializer(many=False),
            400: "Invalid Format Data",
            401: "Unauthorized Access",
        },
    )
    def get(cls, request, meetup_id, question_id):

        meeting = Meeting.objects.filter(id=meetup_id).first()
        if meeting:
            question = get_object_or_404(
                Question, id=question_id, meetup_id=meetup_id
            )
            serializer = QuestionSerializer(question, many=False)
            result = serializer.data
            up_votes = len(
                [
                    votes
                    for votes in Vote.objects.filter(
                        question_id_id=result["id"], vote=1
                    )
                ]
            )
            dwn_votes = len(
                [
                    votes
                    for votes in Vote.objects.filter(
                        question_id=result["id"], vote=-1
                    )
                ]
            )
            votes = [{"up votes": up_votes, "down votes": dwn_votes}]

            Mserializer = MeetingSerializer(meeting, many=False)

            user = User.objects.filter(Q(id=result["created_by"])).distinct().first()
            result["created_by_name"] = user.username
            result["meetup_name"] = Mserializer.data["title"]
            result["votes"] = votes

            return Response(
                data={
                    "status": status.HTTP_200_OK,
                    "data": [{"question": result}],
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "invalid meetup id"}, status=status.HTTP_400_BAD_REQUEST
        )

    @classmethod
    @swagger_auto_schema(
        operation_description="Update a question for a specific meetup.",
        operation_id="Update a question for a specific meetup.",
        request_body=QuestionSerializer,
        responses={
            200: QuestionSerializer(many=False),
            400: "Invalid Format Data",
            401: "Unauthorized Access",
        },
    )
    def put(cls, request, meetup_id, question_id):
        meeting = Meeting.objects.filter(id=meetup_id).first()
        if meeting:
            current_user = request.user
            if current_user.is_superuser:
                return Response(
                    data={
                        "error": "Admin is not allowed to update a question",
                        "status": 401,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            question = get_object_or_404(
                Question,
                id=question_id,
                meetup_id=meetup_id,
                delete_status=False,
            )
            serializer = QuestionSerializer(question, many=False)

            serializer = QuestionSerializer(question, request.data)
            if serializer.is_valid():
                serializer.save(date_modified=timezone.now())

                Mserializer = MeetingSerializer(meeting, many=False)

                qn_dict = dict(serializer.data)
                qn_dict["created_by_name"] = current_user.username
                qn_dict["meetup_name"] = Mserializer.data["title"]
                return Response(
                    data={
                        "status": status.HTTP_200_OK,
                        "data": [
                            {
                                "question": qn_dict,
                                "success": "Question successfully edited",
                            }
                        ],
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"error": "invalid meetup id"}, status=status.HTTP_400_BAD_REQUEST
        )

    @classmethod
    @swagger_auto_schema(
        operation_description="Delete a question for a specific meetup.",
        operation_id="Delete a question for a specific meetup.",
        responses={
            200: QuestionSerializer(many=False),
            400: "Invalid Meetup ID",
            404: "Invalid Question ID",
            401: "Unauthorized Access",
        },
    )
    def delete(cls, request, meetup_id, question_id):
        if Meeting.objects.filter(id=meetup_id):
            question = get_object_or_404(
                Question,
                id=question_id,
                meetup_id=meetup_id,
                delete_status=False,
            )
            current_user = request.user
            if current_user.is_superuser:
                question.delete_status = True
                question.save()
                return Response(
                    data={
                        "status": status.HTTP_200_OK,
                        "data": [
                            {
                                "success": "Question has been soft deleted",
                                "status": status.HTTP_200_OK,
                            }
                        ],
                    },
                    status=status.HTTP_200_OK,
                )
            elif str(question.created_by) != str(current_user.username):
                return Response(
                    data={
                        "status": status.HTTP_401_UNAUTHORIZED,
                        "error": "You cannot delete question created by another user",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            else:
                question.delete()
                return Response(
                    data={
                        "status": status.HTTP_200_OK,
                        "data": [{"success": "Question has been deleted"}],
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"error": "invalid meetup id"}, status=status.HTTP_400_BAD_REQUEST
        )
