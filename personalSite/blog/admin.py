from django.contrib import admin
from .models import Post, Tag, TaggedPost
from django.db import models
from martor.widgets import AdminMartorWidget

# Register your models here.
admin.site.register(Tag)
admin.site.register(TaggedPost)

class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

admin.site.register(Post, YourModelAdmin)