
from django.contrib import admin
from money import models

admin.site.register(models.Transaction)
admin.site.register(models.Salary)
admin.site.register(models.Account)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Downpayment)
admin.site.register(models.FastUtgift)
