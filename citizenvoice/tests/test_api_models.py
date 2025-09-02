from re import template
from django.test import TestCase
from voice.models import Question, Survey, Answer, Response, MapView
from django.contrib.auth.models import User
from datetime import date

TEST_QUESTION_ID = 2


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        print(
            "setUpTestData: Run once to set up non-modified data for all class methods."
        )

        # Create test user
        user = User(username="testuser", password="testpass")
        user.save()

        # Create test survey
        survey = Survey(
            name="Test Survey 1",
            description="This is used to test things",
            publish_date=date.today(),
            expire_date=date.today(),
            public_url="www.google.com",
            designer=user,
        )
        survey.save()

        # Create test mapview
        map_view = MapView(
            map_service_url="www.openstreetmaps.org",
            options='{"lat":22.3,"lon":32.1,"zoom":4}',
        )
        map_view.save()

        # Create test question
        question = Question(
            text="Testing question",
            order=1,
            required=True,
            question_type="text",
            choices="",
            survey=survey,
            mapview=map_view,
        )
        question.save()

        # Create test Likert scale question
        likert_config = {
            "scale_points": 5,
            "labels": {
                "1": "Strongly Disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree",
            },
            "left_anchor": "Strongly Disagree",
            "right_anchor": "Strongly Agree",
        }
        likert_question = Question(
            text="How satisfied are you?",
            order=2,
            required=True,
            question_type="likert-scale",
            survey=survey,
            likert_config=likert_config,
        )
        likert_question.save()
        pass

    def test_created_label(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        field_label = question._meta.get_field("text").verbose_name
        self.assertEqual(field_label, "Text of the Question")

    def test_question_type_max_length(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        max_length = question._meta.get_field("question_type").max_length
        self.assertEqual(max_length, 150)

    def test_mapview_json(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        zoom_level = question.mapview.options
        json_string = '{"lat":22.3,"lon":32.1,"zoom":4}'
        self.assertEqual(zoom_level, json_string)

    def test_likert_scale_question_creation(self):
        """Test that Likert scale questions can be created with proper configuration."""
        likert_questions = Question.objects.filter(question_type="likert-scale")
        self.assertTrue(likert_questions.exists())

        likert_question = likert_questions.first()
        self.assertEqual(likert_question.question_type, "likert-scale")
        self.assertIsNotNone(likert_question.likert_config)

        config = likert_question.likert_config
        self.assertEqual(config["scale_points"], 5)
        self.assertIn("labels", config)
        self.assertEqual(len(config["labels"]), 5)

    def test_likert_default_config(self):
        """Test that the default Likert configuration method works correctly."""
        question = Question()
        default_config = question.get_default_likert_config()

        self.assertEqual(default_config["scale_points"], 5)
        self.assertIn("labels", default_config)
        self.assertIn("left_anchor", default_config)
        self.assertIn("right_anchor", default_config)

        # Check that all scale points have labels
        for i in range(1, 6):
            self.assertIn(str(i), default_config["labels"])

    def test_get_likert_config(self):
        """Test that get_likert_config returns the appropriate configuration."""
        # Test with a Likert question that has custom config
        likert_question = Question.objects.filter(question_type="likert-scale").first()
        config = likert_question.get_likert_config()
        self.assertEqual(config["scale_points"], 5)
        self.assertEqual(config["labels"]["1"], "Strongly Disagree")

        # Test with a non-Likert question (should return default)
        text_question = Question.objects.filter(question_type="text").first()
        default_config = text_question.get_likert_config()
        self.assertEqual(default_config["scale_points"], 5)
        self.assertIn("Very Dissatisfied", str(default_config["labels"]["1"]))
