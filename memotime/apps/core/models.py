import uuid

import django.db.models

__all__ = ()


class BaseImageModel(django.db.models.Model):
    def upload_to_path(self, filename):
        new_filename = f"{uuid.uuid4()}.{filename.split('.')[-1]}"
        return (
            f"uploads/{self.__class__.__name__.lower()}/{uuid.uuid4()}/{new_filename}"
        )

    image = django.db.models.ImageField(
        verbose_name="картинка/аватарка",
        help_text="картинка заметки/аватарка профиля",
        upload_to=upload_to_path,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
