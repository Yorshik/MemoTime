import django.db.models

__all__ = ()


class BaseImageModel(django.db.models.Model):
    def upload_to_path(self, _):
        raise NotImplementedError("overwrite this method in your subclasses")

    image = django.db.models.ImageField(
        verbose_name="картинка/аватарка",
        help_text="картинка заметки/аватарка профиля",
        upload_to=upload_to_path,
    )
