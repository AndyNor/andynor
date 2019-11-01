from django.contrib import admin
from blog import models

admin.site.register(models.Category)
admin.site.register(models.Group)
admin.site.register(models.Tag)
admin.site.register(models.Blog)
admin.site.register(models.Comment)
admin.site.register(models.Image)
admin.site.register(models.File)
