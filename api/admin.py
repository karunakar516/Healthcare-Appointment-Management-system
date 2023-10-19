from django.contrib import admin
from django.contrib.auth.models import User

from api.models import MasterConfig

# Register your models here.
admin.site.register(User)
admin.site.register(MasterConfig)
