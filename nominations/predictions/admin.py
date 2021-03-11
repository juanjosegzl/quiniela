from django.contrib import admin

from . import models

admin.site.register(models.Event)
admin.site.register(models.Category)
admin.site.register(models.Entity)
admin.site.register(models.Nomination)
admin.site.register(models.Prediction)
