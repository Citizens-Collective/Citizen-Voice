import copy
from rest_framework import serializers
from .models import (
    Answer,
    Question,
    Survey,
    PointFeature,
    PolygonFeature,
    LineFeature,
    MapView,
    LocationCollection,
    DashboardTopic,
)
from .models import Response as ResponseModel
from django.contrib.auth.models import User
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.core.files.images import get_image_dimensions  # ADD THIS IMPORT
from django.conf import settings  # ADD THIS IMPORT

# =============================================
# Create serializer classes for exposing certain model fields to be used in the API
# =============================================


class TopicSerializer(serializers.ModelSerializer):
    """
    A serializer class for the DashboardTopic model.
    """

    class Meta:
        model = DashboardTopic
        fields = ["id", "name"]


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes 'text', 'order', 'required', 'question_type', 'choices', 'is_geospatial', 'map_view', 'likert_config'
    fields of the Question model for the API.
    """

    survey = serializers.HyperlinkedRelatedField(
        queryset=Survey.objects.all(), view_name="survey-detail"
    )
    topics = serializers.HyperlinkedRelatedField(
        view_name="topics-detail", read_only=True, many=True
    )
    likert_config = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "url",
            "text",
            "explanation",
            "has_text_input",
            "order",
            "required",
            "question_type",
            "choices",
            "survey",
            "is_geospatial",
            "mapview",
            "topics",
            "likert_config",
        )
        read_only_fields = ("id", "url")

    def validate_likert_config(self, value):
        """
        Validate Likert scale configuration.
        Ensure it contains required fields.
        """
        if not value:
            return value

        required_fields = ["scale_points", "labels"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: '{field}'")

        # Validate scale points
        scale_points = value.get("scale_points")
        if not isinstance(scale_points, int) or scale_points < 2 or scale_points > 10:
            raise serializers.ValidationError(
                "Scale points must be an integer between 2 and 10."
            )

        # Validate labels
        labels = value.get("labels", {})
        if not isinstance(labels, dict):
            raise serializers.ValidationError("Labels must be a dictionary")

        # Check there are labels for all scale points
        for i in range(1, scale_points + 1):
            if str(i) not in labels:
                raise serializers.ValidationError(f"Missing label for scale point {i}.")

        return value

    def validate(self, attrs):
        """Validate question data."""
        question_type = attrs.get("question_type")
        likert_config = attrs.get("likert_config")

        if question_type == Question.LIKERT_SCALE and not likert_config:
            # Set default Likert scale configuration if not provided
            attrs["likert_config"] = Question().get_default_likert_config()

        return attrs

    def create(self, validated_data):
        question = Question.objects.create(
            text=validated_data["text"],
            order=validated_data["order"],
            required=validated_data["required"],
            question_type=validated_data["question_type"],
            choices=validated_data.get("choices", None),
            survey=validated_data["survey"],
            is_geospatial=validated_data.get("is_geospatial", False),
            has_text_input=validated_data.get("has_text_input", True),
            mapview=validated_data.get("mapview", None),
            likert_config=validated_data.get("likert_config", None),
        )
        return question


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes 'response_id', 'url', 'survey', 'respondent', 'created', 'updated'
    fields of the Response model for the API.
    """

    survey = serializers.HyperlinkedRelatedField(
        queryset=Survey.objects.all(), view_name="survey-detail"
    )
    respondent = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="user-detail", allow_null=True
    )

    def get_respondent(self, User):
        return VoiceUserSerializer(User.respondent).data

    class Meta:
        model = ResponseModel
        fields = ("response_id", "url", "created", "updated", "survey", "respondent")
        extra_kwargs = {
            "response_id": {"read_only": True},
            "url": {"read_only": True},
            "created": {"read_only": True},
        }

    def create(self, validated_data):
        response = ResponseModel.objects.create(**validated_data)
        return response


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'name', 'description', 'submit_message', 'is_published', 'need_logged_user',
    'editable_answers', 'publish_date', 'expire_date', 'public_url', 'designer'
    fields of the Survey model for the API.
    """

    designer = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True
    )

    class Meta:
        model = Survey
        fields = (
            "id",
            "url",
            "name",
            "description",
            "submit_message",
            "is_published",
            "need_logged_user",
            "editable_answers",
            "publish_date",
            "expire_date",
            "public_url",
            "designer",
        )


class VoiceUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'id', 'username', 'first_name', 'last_name', 'email'
    fields of the User model for the API.
    """

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")


class PointFeatureSerializer(GeoFeatureModelSerializer):
    """
    GeoJson serializer for 'id', 'url', 'geom', 'name', 'annotation', 'location'
    fields of the PointLocation model for the API.
    """

    location = serializers.HyperlinkedRelatedField(
        queryset=LocationCollection.objects.all(), view_name="locationcollection-detail"
    )

    class Meta:
        model = PointFeature
        geo_field = "geom"
        fields = ("id", "url", "annotation", "location", "geom")
        read_only_fields = ("id", "url")

    def create(self, validated_data):
        response = PointFeature.objects.create(**validated_data)
        return response


class PolygonFeatureSerializer(GeoFeatureModelSerializer):
    """
    GeoJson serializer for 'id', 'geom', 'annotation', 'location' fields of the PolygonLocation model for the API.
    The 'geom' field is serialized as a GeoJSON field.
    """

    location = serializers.HyperlinkedRelatedField(
        queryset=LocationCollection.objects.all(), view_name="locationcollection-detail"
    )

    class Meta:
        model = PolygonFeature
        geo_field = "geom"
        fields = ("id", "url", "annotation", "location", "geom")
        read_only_fields = ("id", "url")

    def create(self, validated_data):
        response = PolygonFeature.objects.create(**validated_data)
        return response


class LineFeatureSerializer(GeoFeatureModelSerializer):
    """
    Serialises 'id', 'geom', 'annotation' fields of the LineStringLocation model for the API.
    The 'geom' field is serialized as a GeoJSON field.
    """

    location = serializers.HyperlinkedRelatedField(
        queryset=LocationCollection.objects.all(), view_name="locationcollection-detail"
    )

    class Meta:
        model = LineFeature
        geo_field = "geom"
        fields = ("id", "url", "annotation", "location", "geom")
        read_only_fields = ("id", "url")

    def create(self, validated_data):
        response = LineFeature.objects.create(**validated_data)
        return response


class LocationCollectionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'question', 'answer', 'points', 'lines', 'polygons'
    fields of the Location model for the API.
    """

    geojson = serializers.SerializerMethodField()

    class Meta:
        model = LocationCollection
        fields = ("id", "url", "name", "description", "geojson")
        read_only_fields = ("id", "url")

    def get_geojson(self, obj):
        """
        Returns a list of URLs of all the features (points, lines, polygons)
        associated with the location collection.
        """
        points = PointFeatureSerializer(
            PointFeature.objects.filter(location__id=obj.pk),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        lines = LineFeatureSerializer(
            LineFeature.objects.filter(location__id=obj.pk),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        polygons = PolygonFeatureSerializer(
            PolygonFeature.objects.filter(location__id=obj.pk),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        features = copy.deepcopy(points)
        features["features"].extend(lines["features"])
        features["features"].extend(polygons["features"])

        return features


class AnswerCSVSerializer(serializers.ModelSerializer):
    """
    Serialises 'response', 'question', 'created', 'updated', 'body'
    fields of the Answer model for the API.
    """

    response = serializers.SerializerMethodField()
    mapview = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "id",
            "created",
            "updated",
            "question",
            "body",
            "image_url",
            "response",
            "mapview",
        )
        read_only_fields = (
            "id",
            "created",
            "updated",
            "question",
            "response",
            "mapview",
            "image_url",
        )

    def get_image_url(self, obj):
        """Get the full URL of the image if it exists."""
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_response(self, obj):
        serializer = ResponseSerializer(
            obj.response, context={"request": self.context.get("request")}
        )
        return serializer.data

    def get_mapview(self, obj):
        serializer = MapViewSerializer(
            obj.mapview, context={"request": self.context.get("request")}
        )
        return serializer.data

    def get_question(self, obj):
        serializer = QuestionSerializer(
            obj.question, context={"request": self.context.get("request")}
        )
        return serializer.data


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'response', 'question', 'created', 'updated', 'body', 'image'
    fields of the Answer model for the API.
    """

    response = serializers.HyperlinkedRelatedField(
        queryset=ResponseModel.objects.all(), view_name="response-detail"
    )
    question = serializers.HyperlinkedRelatedField(
        queryset=Question.objects.all(), view_name="question-detail"
    )
    mapview = serializers.HyperlinkedRelatedField(
        queryset=MapView.objects.all(),
        view_name="mapview-detail",
        required=False,
        allow_null=True,
    )
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Answer
        fields = (
            "id",
            "url",
            "created",
            "updated",
            "body",
            "image",
            "mapview",
            "question",
            "response",
        )
        read_only_fields = ("id", "url", "created")
        depth = 2

    def validate_image(self, value):
        """Validate uploaded image."""
        if value:
            # Check file size
            if value.size > getattr(settings, "MAX_IMAGE_SIZE", 5242880):
                raise serializers.ValidationError(
                    "Image file too large. Maximum size is 5MB."
                )

            # Check image dimensions
            width, height = get_image_dimensions(value)
            if width > 4000 or height > 4000:
                raise serializers.ValidationError(
                    "Image dimensions too large. Maximum 4000x4000 pixels."
                )

        return value

    def validate(self, attrs):
        """Ensure image is provided for image upload questions and validate Likert responses."""
        question = attrs.get("question")
        body = attrs.get("body")

        if question:
            if question.question_type == Question.IMAGE_UPLOAD:
                if not attrs.get("image") and not body:
                    raise serializers.ValidationError(
                        "An image is required for image-upload questions."
                    )
            elif question.question_type == Question.LIKERT_SCALE:
                if not body:
                    raise serializers.ValidationError(
                        "A response is required for Likert scale questions."
                    )
                try:
                    likert_value = int(body)
                    config = question.get_likert_config()
                    scale_points = config.get("scale_points", 5)
                    if likert_value < 1 or likert_value > scale_points:
                        raise serializers.ValidationError(
                            f"Likert response must be between 1 and {scale_points}."
                        )
                except ValueError:
                    raise serializers.ValidationError(
                        "Likert response must be a valid integer."
                    )
        return attrs

    def create(self, validated_data):
        # Add debugging
        print(f"Validated data: {validated_data}")
        print(f"Mapview in validated_data: {validated_data.get('mapview')}")
        response = Answer.objects.create(**validated_data)
        return response


class MapViewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialises 'name', 'map_service_url' and 'options'
    fields of the MapView model for the API.
    """

    class Meta:
        model = MapView
        fields = (
            "id",
            "url",
            "name",
            "description",
            "map_service_url",
            "options",
            "location",
        )
        read_only_fields = ("id", "url")

    def create(self, validated_data):
        mapview = MapView.objects.create(**validated_data)
        return mapview

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.map_service_url = validated_data.get(
            "map_service_url", instance.map_service_url
        )
        instance.options = validated_data.get("options", instance.options)
        instance.location = validated_data.get("location", instance.location)
        instance.save()
        return instance
