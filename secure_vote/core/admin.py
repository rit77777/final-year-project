from django.contrib import admin

# Register your models here.

from .models import Candidate, RegisteredVoters, UniqueID

admin.site.register(Candidate)
admin.site.register(RegisteredVoters)
admin.site.register(UniqueID)