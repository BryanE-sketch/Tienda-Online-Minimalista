from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

MAX_IMAGE_SIZE_MB = 2
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']


def validate_image_size(image):
    """Se conserva porque la migración 0002 hace referencia a esta función."""
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar {MAX_IMAGE_SIZE_MB} MB.')


def validate_image_upload(image):
    """Valida extensión y tamaño solo en subidas nuevas, no en imágenes ya guardadas."""
    if getattr(image, '_committed', True):
        return
    FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS)(image)
    validate_image_size(image)