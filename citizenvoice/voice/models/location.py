from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.gis.db import models as gis_models

class PointFeature(gis_models.Model)   :
    """
    Represents the location of a question or answer as a POINT
    """
    geom = gis_models.PointField()
    annotation = models.CharField(max_length=150, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)

class PolygonFeature(gis_models.Model):
    """
    Represents the location of a question or answer as a POLYGON
    """
    geom = gis_models.PolygonField()
    annotation = models.CharField(max_length=150, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.annotation}"


class LineFeature(gis_models.Model):
    """
    Represents the location of a question or answer as a LINESTRING
    """
    geom = gis_models.LineStringField()
    annotation = models.CharField(max_length=150, blank=True, null=True)
    location = models.ForeignKey('LocationCollection', on_delete=models.CASCADE)


class LocationCollection(models.Model):
    """
    class for representing geographic locations of
    Questions and Answers.

    Attributes:
    - name: name for the location
    - question: a location may belong to a question
    - answer: a location may belong to an answer
    """

    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        "Returs the name of the location"
        return str(self.name)
