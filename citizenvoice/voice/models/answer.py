"""
This code is based on the source code of the django-survey application
by Pierre Sassoulas, 2022, version 1.4.0.
Available at https://github.com/Pierre-Sassoulas/django-survey
"""

# from abc import update_abstractmethods
# Import geographic model since we will be saving location data
# from django.contrib.gis.db import moßdels
import os
from django.db import models
from .response import Response
from .question import Question
from .mapview import MapView
from django.utils.translation import gettext_lazy as _


def answer_image_upload_path(instance, filename):
    """Generate upload path for answer images."""
    return f"survey_answers/{instance.question.survey.id}/{instance.question.id}/{filename}"


# Represents a single answer given to a certain question as part of a user's response
class Answer(models.Model):
    """
    The type-specific Answer model uses a generic text field to allow for flexible
    field sizes to accommodate for different Question types. It also contains latitude
    and longitude fields to capture spatial answers.
    """

    response = models.ForeignKey(
        Response, to_field="response_id", on_delete=models.CASCADE
    )  # this field is not inheriting data type. Must be uuid.
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    mapview = models.ForeignKey(
        MapView, on_delete=models.SET_NULL, blank=True, null=True
    )
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Last edited"), auto_now=True)
    body = models.TextField(_("Answer Body"), blank=True)
    image = models.ImageField(
        _("Image"),
        upload_to=answer_image_upload_path,
        blank=True,
        null=True,
        help_text=_("Upload an image as your answer"),
    )

    @property
    def values(self):
        """Return answer values based on question type."""
        if self.question.question_type == Question.IMAGE_UPLOAD and self.image:
            return [self.image.url]
        elif self.body:
            # For multiple choice questions, split by comma
            if self.question.question_type in [Question.SELECT_MULTIPLE]:
                return self.body.split(",")
            return [self.body]
        return []

    # TODO: [manuel] Shall we define types for answers?

    def __str__(self):
        if self.image:
            return f"{self.__class__.__name__} to '{self.question}' : 'Image: {os.path.basename(self.image.name)}'"
        return f"{self.__class__.__name__} to '{self.question}' : '{self.body}'"
