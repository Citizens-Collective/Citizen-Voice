from .models import (
    Answer,
    Question,
    Survey,
    PointFeature,
    DashboardTopic,
    PolygonFeature,
    LineFeature,
    MapView,
    LocationCollection,
)
from .models import Response as ResponseModel
from .permissions import IsAuthenticatedAndSelfOrMakeReadOnly, IsAuthenticatedAndSelf
from rest_framework.decorators import api_view
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response as rf_response
from django.middleware import csrf
from django.utils import timezone
from .serializers import (
    AnswerSerializer,
    LocationCollectionSerializer,
    PointFeatureSerializer,
    QuestionSerializer,
    SurveySerializer,
    ResponseSerializer,
    VoiceUserSerializer,
    MapViewSerializer,
    LineFeatureSerializer,
    PolygonFeatureSerializer,
    AnswerCSVSerializer,
    TopicSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
import csv
from django.http import HttpResponse


@api_view(["GET"])
def get_csrf_token(request):
    token = csrf.get_token(request)
    return rf_response({"csrf_token": token})


# TODO: consider if using viewset is a good option for this. Viewsets are a fast way to create a CRUD API,
# but they obfuscate the code; we might want to have more control over the API.
# REF: https://www.django-rest-framework.org/api-guide/viewsets/


class AnswerViewSet(viewsets.ModelViewSet):
    """
    Answer ViewSet used internally to query data from database.
    """

    # Figure out the permissions for the answers, do designers to to see them?
    # permission_classes = [IsAuthenticatedAndSelfOrMakeReadOnly]
    serializer_class = AnswerSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Returns a set of all Answer instances in the database, or
        filters the queryset based on the query parameters.

        Parameters:
            question (int): Question ID to be used for finding related Answers
            survey (int): Survey ID to be used for finding related Answers

        Returns:
            queryset:
        """

        queryset = Answer.objects.all()
        question_id = self.request.query_params.get("question", None)

        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)
        survey_id = self.request.query_params.get("survey", None)

        if survey_id is not None and question_id is None:
            queryset = queryset.filter(question__survey_id=survey_id)
        return queryset

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def upload_image_answer(self, request):
        """Handle image upload for answers."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.save()
            return rf_response(
                AnswerSerializer(answer, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return rf_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Override create to handle both regular and image uploads."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        # Return the created answer with full serialization
        response_serializer = AnswerSerializer(answer, context={"request": request})
        return rf_response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(response_serializer.data),
        )

    @staticmethod
    def GetAnswerByResponse(response_id):
        """
        Get all answers by filtering based either on their related Response.

        Parameters:
            response_id (int): Response ID to be used for finding related Answers

        Return:
            queryset: containing all Answer instances with this response_id
        """
        queryset = Answer.objects.filter(response=response_id)
        return queryset

    @action(detail=False, methods=["get"], url_path="csv")
    def download_csv(self, request, *args, **kwargs):
        queryset = Answer.objects.all()
        serializer = AnswerCSVSerializer(
            queryset, context={"request": request}, many=True
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="answers.csv"'

        # TODO: THIS IS BETTER DONE WITH SQL QUERY
        def flatten_dict(d, parent_key="", sep="."):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        flatten_data = [flatten_dict(answer) for answer in serializer.data]

        writer = csv.writer(response)
        headers = set()
        for item in flatten_data:
            headers.update(item.keys())
        writer.writerow(list(headers))

        for answer in flatten_data:
            _rows = []
            for field in headers:
                try:
                    _row = answer[field]
                    _rows.append(_row)
                except KeyError:
                    print("KeyError", field)
                    _row = ""
                    _rows.append(_row)
            writer.writerow(_rows)

            # writer.writerow([answer[field] for field in headers])

        return response


class QuestionViewSet(viewsets.ModelViewSet, UpdateModelMixin):
    """
    Question ViewSet used to query data from database.
    The `create` method is overwritten to accept one data object or an array of objects.
    """

    permission_classes = [IsAuthenticatedAndSelfOrMakeReadOnly]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        """
        Here we are overwriting the default create method from the Django REST framework to update or create Questions by list or by single instances
        """
        # Checks if the request data is a list, and if not it wraps it in a list
        data = request.data if isinstance(request.data, list) else [request.data]
        questions = []
        """
        Here we iterate over each item in the list and checks if it has an 'id' field. If it does, it retrieves the existing Question object with that ID (if it exists). If it doesn't have an 'id' field, it creates a new Question object.
        """
        for question_data in data:
            if "id" in question_data:
                question = Question.objects.filter(pk=question_data["id"]).first()
                if question is None:
                    continue
                serializer = self.get_serializer(
                    question,
                    data=question_data,
                    partial=True,
                    context={"request": request},
                )
            else:
                serializer = self.get_serializer(
                    data=question_data, context={"request": request}
                )
            serializer.is_valid(raise_exception=True)
            question = serializer.save()
            questions.append(question)

        update_fields = [
            "text",
            "explanation",
            "order",
            "required",
            "question_type",
            "choices",
            "survey",
            "is_geospatial",
            "has_text_input",
            "map_view",
        ]

        # update or create multiple questions in bulk
        Question.objects.bulk_update_or_create(
            questions, update_fields, match_field="id"
        )

        serializer = self.get_serializer(questions, many=True)
        headers = self.get_success_headers(serializer.data)
        return rf_response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        update_fields = [
            "text",
            "explanation",
            "order",
            "required",
            "question_type",
            "choices",
            "survey",
            "is_geospatial",
            "has_text_input",
            "map_view",
        ]
        serializer.save(update_fields=update_fields)

    def perform_update(self, serializer):
        serializer.save(
            update_fields=[
                "text",
                "explanation",
                "order",
                "required",
                "question_type",
                "choices",
                "survey",
                "is_geospatial",
                "show_text",
                "map_view",
            ],
            update_conflicts={
                "text": "keep",
                "explanation": "keep",
                "order": "keep",
                "required": "keep",
                "question_type": "keep",
                "choices": "keep",
                "survey": "keep",
                "is_geospatial": "keep",
                "has_text_input": "keep",
                "map_view": "keep",
            },
        )

    @action(detail=True, methods=["get"])
    def ordered_questions(self, request, pk=None):
        """
        Retrieve a list of questions for a given survey, ordered by the 'order' field.
        API url: `/api/questions/{survey_id}/ordered_questions`

        Parameters:
            request (Request): The request object used to make the API call.
            pk = survey_id (int): The primary key of the Survey instance to retrieve questions for.

        Returns:
            Response: A JSON response containing a list of serialized Question instances.
        """
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.question_set.all().order_by("order")
        serializer = self.get_serializer(questions, many=True)
        return rf_response(serializer.data)


class SurveyViewSet(viewsets.ModelViewSet):
    """
    Survey ViewSet used internally to query data from database.

    """

    permission_classes = [IsAuthenticatedAndSelfOrMakeReadOnly]
    serializer_class = SurveySerializer

    def get_queryset(response):
        """
        Returns a set of all Survey instances in the database.

        Return:
            queryset: containing all Survey instances
        """
        queryset = Survey.objects.all().order_by("name")

        return queryset

    @action(detail=False, methods=["GET"], url_path="my-surveys")
    def my_surveys(self, request, *args, **kwargs):
        print("Getting my surveys...")

        user = self.request.user
        print(type(user))
        if type(user) == User:
            surveys_of_user = (
                Survey.objects.all().filter(designer=user.id).order_by("name")
            )
            survey_serializer = self.get_serializer(surveys_of_user, many=True)
            return rf_response(survey_serializer.data)

        return rf_response({})

    @action(detail=False, methods=["POST"], url_path="create-survey")
    def create_survey(self, request, *args, **kwargs):
        print("Creating a new survey...")

        user = self.request.user
        if type(user) is User:
            survey_name = self.request.data["name"]
            survey_description = self.request.data["description"]
            once_up_a_time = datetime.now()

            tz_aware_datetime = timezone.make_aware(
                once_up_a_time
            )  # Convert to timezone-aware datetime

            survey = Survey(
                name=survey_name,
                description=survey_description,
                publish_date=tz_aware_datetime,
                expire_date=tz_aware_datetime,
                designer=user,
            )
            survey.save()

            survey_serializer = SurveySerializer(
                survey, context={"request": request}
            )  # Pass the request context
            return rf_response(survey_serializer.data)
        else:
            print("User was anonymous")
        return rf_response(None)

    # TODO: remove this one because we are now directly getting the questions from the QuestionViewSet
    @action(detail=True, methods=["GET"], url_path="questions")
    def get_questions_of_survey(self, request, pk=None):
        print("Retreiving questions of survey...")
        user = self.request.user
        survey = Survey.objects.get(id=pk)
        if survey.is_published:
            # if type(user) is User:
            #     survey = Survey.objects.get(id=pk)
            #     if (survey.designer != user.id):
            #         print("uses is not the designer")
            #         print(
            #             f"User id: {user.id} \nDesigner id: {survey.designer_id}")
            #         rf_response([])
            questions = Question.objects.all().filter(survey_id=pk).order_by("order")
            question_serializer = QuestionSerializer(
                questions, many=True, context={"request": request}
            )
            # print(question_serializer.data)
            return rf_response(question_serializer.data)
        # else:
        #     print("User was anonymous")
        return rf_response([])

    # @action(detail=True, methods=['post'])
    # def CreateSurvey(response):
    #     """
    #     Create a survey
    #     """
    #     data = JSONParser().parse(response)
    #     survey_serializer = SurveySerializer(data=data, context={'request': response})
    #     if survey_serializer.is_valid():
    #         survey_serializer.save()
    #         return JsonResponse(survey_serializer.data, status=status.HTTP_201_CREATED)
    #     return JsonResponse(survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def GetSurveyByID(id):
        """
        Get a specific Survey based on its ID.

        Parameters:
            id (int): Survey ID to be used for finding this Survey.

        Return:
            queryset: containing the Survey instance with this id
        """
        queryset = Survey.objects.filter(id=id)
        return queryset

    @staticmethod
    def GetSurveyByDesigner(designer, unexpired_only=False):
        """
        Get a specific Survey based on its author.

        Parameters:
            designer (int): User ID to be used for finding related Surveys.
            unexpired_only (bool):  True - only unexpired surveys (by current date and time) will be returned
                                    False - all surveys will be returned
                                    default = True

        Return:
            queryset: containing the Survey instances related to this user
        """
        if unexpired_only:
            now = datetime.now()
            queryset = Survey.objects.filter(designer=designer, expire_date__gte=now)
        else:
            queryset = Survey.objects.filter(designer=designer)
        return queryset

    @staticmethod
    def GetSurveyByAvailable():
        """
        Get a all Surveys that are still available (current date is not past expiration date).

        Return:
            queryset: containing the Survey instances that have not expired yet
        """

        now = datetime.now()
        queryset = Survey.objects.filter(expire_date__gte=now)
        return queryset


class ResponseViewSet(viewsets.ModelViewSet):
    """
    Response ViewSet used internally to query data from database.
    """

    serializer_class = ResponseSerializer
    """
    POST method is used to create a new response
    Example of a POST request body (JSON):
    {
    "survey": "http://localhost:8000/api/v2/surveys/1/",
    "respondent": "http://localhost:8000/api/v2/users/1/"
    }

    Returns a JSON response with the created response:

    {
    "response_id": "uuid",
    "url": "http://localhost:8000/api/v2/responses/uuid/",
    "created": "2024-04-12T14:31:02.476427Z",
    "updated": "2024-04-12T14:31:02.476456Z",
    "survey": "http://localhost:8000/api/v2/surveys/1/",
    "respondent": "http://localhost:8000/api/v2/users/1/"
    }

    """

    def get_queryset(response):
        """
        Returns a set of all Response instances in the database.

        Return:
            queryset: containing all Response instances
        """

        queryset = ResponseModel.objects.all().order_by("created")
        return queryset

    @action(detail=False, methods=["POST"], url_path="submit-response")
    def submit_response(self, request, *args, **kwargs):
        print("Submitting response...")

        # TODO: test submision using this endpoint
        # TODO: this is already possible via the answers endpoint
        user = self.request.user
        answers = self.request.data["answers"]
        responseId = self.request.data["responseId"]
        question = 1  # TODO: get id of question from request

        if type(user) is User:
            print("User:")
            print(str(User))
        else:
            print("User was anonymous")
        time = datetime.now()

        for answer in answers:
            text = answer["_text"]
            resp = ResponseModel.objects.get(pk=int(responseId))
            # TODO: get question id from request
            quest = Question.objects.get(pk=1)
            storedAnswer = Answer(
                response=resp, question=quest, created=time, updated=time, body=text
            )

            print(str(answer))

            return rf_response(None)

    # @action(detail=True, methods=['POST'], url_path='create-response')
    def create(self, request, pk=None):
        survey_id = request.data.get("survey")
        if survey_id is None:
            return rf_response(
                {"message": "a survey is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        request_serializer = ResponseSerializer(
            data=request.data, context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)
        response = request_serializer.save()

        # deserialize the nested response objects by
        # creating a new ResponseSerializer instance
        response_serializer = ResponseSerializer(response, context={"request": request})

        return rf_response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(response_serializer.data),
        )

    @staticmethod
    def GetResponseByID(id):
        """
        Get a specific Response based on its ID.

        Parameters:
            id (int): Response ID to be used for finding this Response.

        Return:
            queryset: containing the Response instance with this id
        """
        queryset = ResponseModel.objects.filter(id=id)
        return queryset

    @staticmethod
    def GetResponseBySurvey(survey_id):
        """
        Get a specific Response based on its survey.

        Parameters:
            survey_id (int): Survey ID to be used for finding related Responses.

        Return:
            queryset: containing the Response instances related to this Survey
        """

        queryset = ResponseModel.objects.filter(response=survey_id)
        return queryset

    @staticmethod
    def GetResponseByRespondent(respondent):
        """
        Get a specific Response based on its respondent.

        Parameters:
            respondent (int): User ID to be used for finding related Responses.

        Return:
            queryset: containing the Response instances related to this respondent/ user
        """

        queryset = ResponseModel.objects.filter(user=respondent)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet used internally to query data from database for all users.
    """

    permission_classes = [IsAuthenticatedAndSelf]
    serializer_class = VoiceUserSerializer

    def get_queryset(response):
        """
        Returns a set of all User instances in the database.

        Return:
            queryset: containing all User instances
        """

        queryset = User.objects.all().order_by("username")
        return queryset


class LocationViewSet(viewsets.ModelViewSet):
    """
    Location ViewSet used internally to query data from database for all users.
    """

    serializer_class = LocationCollectionSerializer
    queryset = LocationCollection.objects.all()

    @action(detail=True, methods=["get"])
    def features(self, request, *args, **kwargs):
        points = PointFeature.objects.filter(location_id=self.kwargs["pk"])
        serializer = PointFeatureSerializer(
            points, many=True, context={"request": request}
        )

        polygons = PolygonFeature.objects.filter(location_id=self.kwargs["pk"])
        polygon_serializer = PolygonFeatureSerializer(
            polygons, many=True, context={"request": request}
        )

        lines = LineFeature.objects.filter(location_id=self.kwargs["pk"])
        line_serializer = LineFeatureSerializer(
            lines, many=True, context={"request": request}
        )

        serializer_data = serializer.data
        serializer_data.extend(line_serializer.data)
        serializer_data.extend(polygon_serializer.data)
        return Response(serializer_data)


class PointFeatureViewSet(viewsets.ModelViewSet):
    """
    PointLocation ViewSet used internally to query data from database for all users.
    """

    serializer_class = PointFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all PointFeature instances in the database.

        Return:
            queryset: containing all PointFeature instances
        """

        queryset = PointFeature.objects.all()
        return queryset


class PolygonFeatureViewSet(viewsets.ModelViewSet):
    """
    PolygonFeature ViewSet used internally to query data from database for all users.
    """

    serializer_class = PolygonFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all PolygonFeature instances in the database.

        Return:
            queryset: containing all PolygonFeature instances
        """

        queryset = PolygonFeature.objects.all()
        return queryset

    @staticmethod
    def GetLocationsByQuestion(question):
        """
        Get a list of PointFeatures associated to this question.

        Parameters:
            question (int): Question ID to be used for finding related PointFeatures.

        Return:
            queryset: containing the PointFeature instances related to this Question
        """

        queryset = PointFeature.objects.filter(question=question)
        return queryset

    @staticmethod
    def GetLocationsByAnswer(answer):
        """
        Get a list of PolygonFeatures associated to this answer.

        Parameters:
            answer (int): Answer ID to be used for finding related PolygonFeatures.

        Return:
            queryset: containing the PolygonFeature instances related to this Answer
        """

        queryset = PolygonFeature.objects.filter(answer=answer)
        return queryset


class LineFeatureViewSet(viewsets.ModelViewSet):
    """
    LineStringLocation ViewSet used internally to query data from database for all users.
    """

    serializer_class = LineFeatureSerializer

    def get_queryset(response):
        """
        Returns a set of all LineStringLocation instances in the database.

        Return:
            queryset: containing all LineStringLocation instances
        """

        queryset = LineFeature.objects.all()
        return queryset

    @staticmethod
    def GetLocationsByQuestion(question):
        """
        Get a list of LineStringLocations associated to this question.

        Parameters:
            question (int): Question ID to be used for finding related LineStringLocations.

        Return:
            queryset: containing the LineStringLocation instances related to this Question
        """

        queryset = LineFeature.objects.filter(question=question)
        return queryset

    @staticmethod
    def GetLocationsByAnswer(answer):
        """
        Get a list of LineStringLocations associated to this answer.

        Parameters:
            answer (int): Answer ID to be used for finding related LineStringLocations.

        Return:
            queryset: containing the LineStringLocation instances related to this Answer
        """

        queryset = LineFeature.objects.filter(answer=answer)
        return queryset


class MapViewViewSet(viewsets.ModelViewSet):
    """
    Question ViewSet used internally to query data from database.

    """

    serializer_class = MapViewSerializer

    def get_queryset(response):
        """
        Returns a set of all MapView instances in the database.

        Return:
            queryset: containing all MapView instances
        """

        queryset = MapView.objects.all().order_by("id")
        return queryset

    @action(detail=False, methods=["get"])
    def id_names(self, request):
        mapviews = MapView.objects.values("id", "name")
        return Response(mapviews)


class TopicViewSet(viewsets.ModelViewSet):
    """
    A ViewSet that returns the topics associated to a question
    """

    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = DashboardTopic.objects.all()
        return queryset
