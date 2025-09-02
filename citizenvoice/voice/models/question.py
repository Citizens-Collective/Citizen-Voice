"""
This code is based on the source code of the django-survey application
by Pierre Sassoulas, 2022, version 1.4.0.
Available at https://github.com/Pierre-Sassoulas/django-survey
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .survey import Survey
from .mapview import MapView
from .dashboard_topic import DashboardTopic
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


# Represents a single question of any type
class Question(models.Model):
    """
    The Question class allows for creating questions of several different types. It also includes the possibility
    to include potential answers as part of the question. These possible answers are not objects, but rather
    captured in a comma-separated text field.
    """

    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT = "select"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    IMAGE_UPLOAD = "image-upload"
    LIKERT_SCALE = "likert-scale"

    QUESTION_TYPES = (
        (TEXT, _("text (multiple line)")),  # syntax (value, label)
        (SHORT_TEXT, _("short text (one line)")),
        (RADIO, _("radio")),
        (SELECT, _("select")),
        (SELECT_MULTIPLE, _("Select Multiple")),
        (INTEGER, _("integer")),
        (FLOAT, _("float")),
        (DATE, _("date")),
        (IMAGE_UPLOAD, _("image upload")),
        (LIKERT_SCALE, _("likert scale")),
    )

    text = models.TextField(_("Question"))
    explanation = models.TextField(
        _("Explanation for the question"), max_length=200, blank=True, null=True
    )
    order = models.IntegerField(_("Order of where question is placed"))
    required = models.BooleanField(_("Question must be filled out"), default=True)
    has_text_input = models.BooleanField(_("Show the input text field"), default=True)
    question_type = models.CharField(
        _("Type of question"), max_length=150, choices=QUESTION_TYPES, default=TEXT
    )
    choices = models.TextField(_("Choices for answers"), blank=True, null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, default=1)
    is_geospatial = models.BooleanField(
        _("If the question must be answered geospatially or not"), default=False
    )
    mapview = models.ForeignKey(
        MapView, on_delete=models.SET_NULL, blank=True, null=True
    )
    topics = models.ManyToManyField(
        DashboardTopic, verbose_name=_("Topics"), blank=True
    )
    likert_config = models.JSONField(
        _("Likert Scale configuration"),
        blank=True,
        null=True,
        help_text=_("JSON configuration for Likert scale labels and values"),
        default=dict,
    )

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ("survey", "order")

    def question_count(self):
        return self.question_set.count()

    def get_default_likert_config(self):
        """
        Returns default 5-point customer satisfaction likert scale configuration.
        """
        return {
            "scale_points": 5,
            "labels": {
                "1": _("Very Dissatisfied"),
                "2": _("Dissatisfied"),
                "3": _("Neither satisfied nor dissatisfied"),
                "4": _("Satisfied"),
                "5": _("Very Satisfied"),
            },
            "left_anchor": _("Very Dissatisfied"),
            "right_anchor": _("Very Satisfied"),
        }

    def get_likert_config(self):
        """
        Returns the likert configuration, or the default if not set.
        """
        if self.question_type == self.LIKERT_SCALE and self.likert_config:
            return self.likert_config
        return self.get_default_likert_config()
