import os
import uuid

from django.utils.text import slugify


def create_custom_image_file_path(instance, filename, path) -> str:
    _, extension = os.path.splitext(filename)
    new_filename = f"{slugify(instance.__class__.__name__.lower())}-{uuid.uuid4()}{extension}"
    return os.path.join(path, new_filename)


def generate_unique_slug(instance, field_name, slug_field_name="slug"):
    """
    Generate a unique slug for a model instance.

    Args:
        instance: The model instance for which to generate the slug.
        field_name: The name of the field to base the slug on (e.g., "title").
        slug_field_name: The name of the field to store the slug (default: "slug").

    Returns:
        A unique slug as a string.
    """
    field_value = getattr(instance, field_name, "")
    original_slug = slugify(field_value)
    unique_slug = original_slug
    model_class = instance.__class__
    num = 1

    while model_class.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{original_slug}-{num}"
        num += 1

    return unique_slug
