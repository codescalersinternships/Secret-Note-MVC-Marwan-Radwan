from django.contrib import admin
from django.utils import timezone
from django.db import models
from . import models

admin.site.register(models.Note)
