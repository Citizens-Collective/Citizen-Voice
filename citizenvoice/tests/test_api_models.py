from re import template
from django.test import TestCase
from voice.models import Question, Survey, Answer, Response, MapView
from django.contrib.auth.models import User
from datetime import date

TEST_QUESTION_ID = 2

class ModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")

        # Create test user
        user = User(username='testuser', password='testpass')
        user.save()

        # Create test survey
        survey = Survey(name='Test Survey 1', description='This is used to test things',
                        publish_date=date.today(), expire_date=date.today(), 
                        public_url='www.google.com', designer=user)
        survey.save()

        # Create test mapview
        map_view = MapView(map_service_url='www.openstreetmaps.org',options='{"lat":22.3,"lon":32.1,"zoom":4}')
        map_view.save()

        # Create test question
        question = Question(text='Testing question', order=1, required=True,
                                question_type='text', choices='', survey=survey, map_view=map_view)
        question.save()
        pass

    def test_created_label(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        field_label = question._meta.get_field('text').verbose_name
        self.assertEqual(field_label, 'Text of the Question')

    def test_question_type_max_length(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        max_length = question._meta.get_field('question_type').max_length
        self.assertEqual(max_length, 150)

    def test_mapview_json(self):
        question = Question.objects.get(id=TEST_QUESTION_ID)
        zoom_level = question.map_view.options
        json_string = '{"lat":22.3,"lon":32.1,"zoom":4}'
        self.assertEqual(zoom_level, json_string)

