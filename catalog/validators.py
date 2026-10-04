from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE_MB = 2


def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar {MAX_IMAGE_SIZE_MB} MB.')