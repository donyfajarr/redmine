from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.user)
admin.site.register(models.dept)
admin.site.register(models.status)
admin.site.register(models.priority)