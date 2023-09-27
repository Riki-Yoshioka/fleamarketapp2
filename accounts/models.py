from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static


class User(AbstractUser):
    icon = models.ImageField(
        upload_to="user_icon/",
        blank=True,
    )
    point = models.IntegerField(default=0)
    profile = models.TextField(max_length=500, blank=True)

    def icon_url(self):
        if self.icon:
            return self.icon.url
        return static("main/img/default-user_icon.png")