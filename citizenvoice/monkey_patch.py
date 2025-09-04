# monkey_patch.py
from drf_spectacular.utils import extend_schema
import types

# Manual mapping of ViewSet classes to their display names
VIEWSET_MAPPINGS = {
    'AnswerViewSet': 'Answer',
    'QuestionViewSet': 'Question', 
    'SurveyViewSet': 'Survey',
    'ResponseViewSet': 'Response',
    'UserViewSet': 'User',
    'LocationViewSet': 'Location',
    'PointFeatureViewSet': 'PointFeature',
    'PolygonFeatureViewSet': 'PolygonFeature',
    'LineFeatureViewSet': 'LineFeature',
    'MapViewViewSet': 'MapView',
    'TopicViewSet': 'Topic',
}

def patch_viewset_class(cls):
    """Patch a specific ViewSet class with manual schema decorations."""
    class_name = cls.__name__
    
    # Skip if not in our mapping
    if class_name not in VIEWSET_MAPPINGS:
        print(f"Skipping {class_name} - not in mapping")
        return cls
    
    # Skip if already patched
    if getattr(cls, '_schema_patched', False):
        print(f"Skipping {class_name} - already patched")
        return cls
    
    model_name = VIEWSET_MAPPINGS[class_name]
    print(f"Patching {class_name} with model name: {model_name}")
    
    # Create new method instances to avoid sharing between ViewSets
    def create_method_with_schema(original_method, summary, description, operation_id):
        @extend_schema(
            summary=summary,
            description=description,
            operation_id=operation_id
        )
        def new_method(self, request, *args, **kwargs):
            return original_method(self, request, *args, **kwargs)
        return new_method
    
    # Only patch methods that don't already have custom schema decorations
    if not hasattr(cls.list, '_spectacular_annotation'):
        cls.list = create_method_with_schema(
            cls.list,
            f"Lists {model_name}s",
            f"Retrieves all {model_name}s.",
            f"listing{model_name}s"
        )
    
    if not hasattr(cls.create, '_spectacular_annotation'):
        cls.create = create_method_with_schema(
            cls.create,
            f"Create a new {model_name}",
            f"Create a new {model_name}.",
            f"create{model_name}"
        )
    
    if not hasattr(cls.retrieve, '_spectacular_annotation'):
        cls.retrieve = create_method_with_schema(
            cls.retrieve,
            f"Retrieve a spesific {model_name}",
            f"Retrieve a specific {model_name} by its ID.",
            f"retrieve{model_name}"
        )
    
    if not hasattr(cls.update, '_spectacular_annotation'):
        cls.update = create_method_with_schema(
            cls.update,
            f"Update a spesific {model_name}",
            f"Update a specific {model_name} by its ID.",
            f"update{model_name}"
        )
    
    if not hasattr(cls.partial_update, '_spectacular_annotation'):
        cls.partial_update = create_method_with_schema(
            cls.partial_update,
            f"Partially update a specific {model_name}",
            f"Partially update a specific {model_name} by its ID.",
            f"partialUpdate{model_name}"
        )
    
    if not hasattr(cls.destroy, '_spectacular_annotation'):
        cls.destroy = create_method_with_schema(
            cls.destroy,
            f"Delete a specific {model_name}",
            f"Delete a specific {model_name} by its ID.",
            f"delete{model_name}"
        )
    
    cls._schema_patched = True
    return cls