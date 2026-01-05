from django.core.exceptions import ValidationError
import os

# This function validates uploaded files and allows only image files with specific extensions.
def allow_only_images_validator(value):
    ext=os.path.splitext(value.name)[1]
    print(ext)
    valid_extensions=['.png','.jpg','.jpeg']
    if not ext.lower() in valid_extensions:  # Check if the uploaded file extension is NOT in the allowed list
        raise ValidationError('Unsupported file extension. Allowed extensions: '+str(valid_extensions))  