from django.contrib import admin
from mysite import models

admin.site.register(models.SiteLog)
admin.site.register(models.Counter)
admin.site.register(models.UserProfile)
